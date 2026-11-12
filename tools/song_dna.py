"""Song DNA: what a singer can hear in each open song's melody, as data.

Writes dna/<id>.json for every open song (`reviewed: true`) in templates/library and
templates/free, and removes the file of a song that is no longer open. `--check` writes nothing and
fails when a file is missing, stale or left over. `--report` prints the sanity numbers (the
difficulty score against the editors' labels, over every song, hidden ones too).

Method (from the 2026-11-12 pilot, docs in the Stackapella repository):
- Repeated material is dropped first: a section whose notes repeat an earlier section's (same
  rhythm and pitches, the words may differ) counts once, per part.
- Opening and ending merge repeated notes, as kin does.
- Sol-fa is movable do: do is the tonic in a major key, la is the tonic in a minor key.
- A phrase end's hold is from its onset to the next note's (the templates shorten a line's last
  note to leave the breath), against the average note.
- A phrase ends on the note before the breath mark (`br`) nearest each section phrase's end
  (within PHRASE_REACH beats, so a pickup sung before the bar line is not the end), else on the
  last note before that end. Breaths added mid-line for singability are not phrase ends.
- A Scotch snap is a 16th (or shorter) starting on an eighth, joined to a note three times as long.
- The scale is the pitch classes holding at least 2% of the melody's sung time.
- Difficulty mixes eight measures, each mapped from a fixed floor to a fixed ceiling, so one
  song's score never moves when another song changes: range, mean interval, leaps of a 4th or
  more, the largest leap, chromatic notes, syncopation, rhythmic variety and notes per second.
- Kin: the longest run of notes two melodies share, in the same sol-fa and the same intervals
  (repeated notes merged, so different words still match), at least KIN_RUN notes long and with
  at least KIN_LEAPS leaps of a 3rd or more (two tunes that only walk the scale are not kin). A
  run over SAME_TUNE of the shorter melody makes them the same tune (a translation or another
  setting). Only open songs are kin.
  A shared opening of KIN_OPENING notes counts too, ranked after every run.

Standard library only.
"""

from __future__ import annotations

import glob
import json
import math
import os
import sys
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'dna')
FORMAT = 1
EPS = 0.01
MAIN_SHARE = 0.02
KIN_RUN = 9
KIN_OPENING = 4
KIN_MAX = 3
KIN_LEAPS = 2
SAME_TUNE = 0.6
PHRASE_REACH = 1.5

NOTE_PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
# Semitones above do. 8 is si in a minor key (the raised 7th) and le in a major one.
SOLFA = ['do', 'di', 're', 'me', 'mi', 'fa', 'fi', 'sol', None, 'la', 'te', 'ti']
MAJOR = {0, 2, 4, 5, 7, 9, 11}
MINOR_OK = MAJOR | {8}  # the minor's raised 7th is in the key

# (measure, floor, ceiling) for the difficulty score.
ANCHORS = [
    ('range', 5, 19),
    ('meanInterval', 1.0, 4.0),
    ('leapRate', 0.0, 0.25),
    ('maxLeap', 4, 12),
    ('chromaticRate', 0.0, 0.15),
    ('syncopationRate', 0.0, 0.3),
    ('rhythmEntropy', 0.5, 2.5),
    ('notesPerSecond', 1.0, 4.0),
]


def key_info(key: str) -> tuple[int, bool]:
    minor = key.endswith('m')
    name = key[:-1] if minor else key
    pc = NOTE_PC[name[0]] + name[1:].count('#') - name[1:].count('b')
    return pc % 12, minor


def solfa(pitch: int, do: int, minor: bool) -> str:
    rel = (pitch - do) % 12
    if rel == 8:
        return 'si' if minor else 'le'
    return SOLFA[rel]


def r3(x: float) -> float:
    return round(x + 0.0, 3)


def kept_notes(song: dict, part: dict) -> tuple[list[dict], list[float], float]:
    """The part's notes with repeated sections dropped, the kept phrases' end beats, and the kept
    span in beats."""
    notes = sorted(part['guide']['notes'], key=lambda n: n['beat'])
    sections = song.get('sections') or []
    if not sections:
        end = max(n['beat'] + n['length'] for n in notes)
        return notes, [end], end
    seen = set()
    out, bounds, span = [], [], 0.0
    for s in sections:
        a, b = s['startBeat'], s['endBeat']
        inside = [n for n in notes if a - EPS <= n['beat'] < b - EPS]
        sig = tuple((r3(n['beat'] - a), n['pitch'], r3(n['length'])) for n in inside)
        if not inside or sig in seen:
            continue
        seen.add(sig)
        out.extend(inside)
        span += b - a
        bounds.extend(p[1] for p in s.get('phrases') or [[a, b]])
    return out, bounds, span


def entropy(lengths: list[float]) -> float:
    counts: dict[float, int] = defaultdict(int)
    for x in lengths:
        counts[round(x * 12) / 12] += 1
    total = len(lengths)
    return -sum(c / total * math.log2(c / total) for c in counts.values())


def on_beat(b: float) -> bool:
    return abs(b - round(b)) < EPS


def measures(notes: list[dict], span: float, tempo: float, tonic: int, minor: bool) -> dict:
    pitches = [n['pitch'] for n in notes]
    ints = [b - a for a, b in zip(pitches, pitches[1:])]
    moving = [abs(i) for i in ints]
    total = sum(n['length'] for n in notes) or 1.0
    in_key = MINOR_OK if minor else MAJOR
    do = (tonic + 3) % 12 if minor else tonic  # in_key is in semitones above do
    chroma = sum(n['length'] for n in notes if (n['pitch'] - do) % 12 not in in_key)
    sync = sum(1 for n in notes if not on_beat(n['beat']) and n['beat'] + n['length'] > math.ceil(n['beat']) + EPS)
    seconds = span * 60.0 / tempo if span else 1.0
    return {
        'range': max(pitches) - min(pitches),
        'meanInterval': sum(moving) / len(moving) if moving else 0.0,
        'leapRate': sum(1 for i in moving if i >= 5) / len(moving) if moving else 0.0,
        'maxLeap': max(moving) if moving else 0,
        'chromaticRate': chroma / total,
        'syncopationRate': sync / len(notes),
        'rhythmEntropy': entropy([n['length'] for n in notes]),
        'notesPerSecond': len(notes) / seconds,
    }


def difficulty(m: dict) -> int:
    score = 0.0
    for name, lo, hi in ANCHORS:
        score += min(1.0, max(0.0, (m[name] - lo) / (hi - lo)))
    return round(100 * score / len(ANCHORS))


def tokens(notes: list[dict], do: int, minor: bool) -> list[tuple]:
    """(sol-fa, interval from the last note, beat) with repeated notes merged."""
    out, last = [], None
    for n in notes:
        if last is not None and n['pitch'] == last:
            continue
        out.append((solfa(n['pitch'], do, minor), 0 if last is None else n['pitch'] - last, n['beat']))
        last = n['pitch']
    return out


def analyse(song: dict) -> dict:
    tonic, minor = key_info(song['key'])
    do = (tonic + 3) % 12 if minor else tonic
    tempo = float(song['tempo'])
    melody = next(p for p in song['parts'] if p.get('melody'))
    notes, bounds, span = kept_notes(song, melody)

    # Scale: pitch classes with at least 2% of the sung time, in sol-fa from do.
    total = sum(n['length'] for n in notes)
    share: dict[int, float] = defaultdict(float)
    for n in notes:
        share[(n['pitch'] - do) % 12] += n['length'] / total
    start = 9 if minor else 0  # list the scale from the tonic: la in minor, do in major
    main = sorted((pc for pc, s in share.items() if s >= MAIN_SHARE), key=lambda pc: (pc - start) % 12)
    names = [solfa(do + pc, do, minor) for pc in main]
    home = MAJOR
    mode = 'minor' if minor else 'major'
    if not minor and 10 in main and 11 not in main:
        mode = 'mixolydian'
    if minor and 6 in main and 5 not in main:
        mode = 'dorian'
    if mode == 'mixolydian':
        home = (MAJOR - {11}) | {10}
    elif mode == 'dorian':
        home = (MAJOR - {5}) | {6}
    missing = [solfa(do + pc, do, minor) for pc in sorted(home, key=lambda pc: (pc - start) % 12) if pc not in main]
    if minor and 8 in main and 7 not in main:
        missing = [x for x in missing if x != 'sol']
    count = len(main)
    semis = any((b - a) % 12 in (1, 11) for a in main for b in main)
    kind = 'chromatic' if count > 7 else 'other'
    if count == 5 and not semis:
        kind = 'pentatonic'  # five notes, no half steps: the gapped scale
    elif count == 6:
        kind = 'hexatonic'
    elif count == 7:
        kind = 'diatonic' if set(main) <= (home | ({8} if minor else set())) else 'chromatic'

    # Rhythm: Scotch snaps (a short note on the beat or half-beat, then one three times as long),
    # dotted pairs.
    compound = song['timeSignature'] in ('6/8', '9/8', '12/8')  # a beat is a dotted quarter
    sixteenth, eighth = (1 / 6, 1 / 3) if compound else (0.25, 0.5)
    snaps = dotted = 0
    for a, b in zip(notes, notes[1:]):
        joined = abs(a['beat'] + a['length'] - b['beat']) < EPS
        short = a['length'] <= sixteenth + EPS and on_beat(a['beat'] / eighth)
        if joined and short and abs(b['length'] - 3 * a['length']) < EPS:
            snaps += 1
        if joined and b['length'] <= 0.5 + EPS and abs(a['length'] - 3 * b['length']) < EPS:
            dotted += 1

    # Phrase ends: the note before each breath, and the last note, against the average note.
    mean_len = total / len(notes)
    ratios = []
    for end in bounds:
        near = [i for i, n in enumerate(notes) if i and n.get('br') and abs(n['beat'] - end) <= PHRASE_REACH]
        if near:
            i = min(near, key=lambda i: abs(notes[i]['beat'] - end)) - 1
        else:
            before = [i for i, n in enumerate(notes) if n['beat'] < end - EPS]
            if not before:
                continue
            i = before[-1]
        # Onset to the next onset: the templates shorten a line's last note to leave the breath.
        held = notes[i + 1]['beat'] - notes[i]['beat'] if i + 1 < len(notes) else notes[i]['length']
        ratios.append(held / mean_len)
    ratios.sort()
    hold = ratios[len(ratios) // 2] if ratios else None

    # Climax: where the highest note first comes, through the kept material.
    pitches = [n['pitch'] for n in notes]
    top = pitches.index(max(pitches))
    climax = top / max(1, len(notes) - 1)

    m = measures(notes, span, tempo, tonic, minor)
    parts = {}
    for p in song['parts']:
        pn, _, pspan = kept_notes(song, p)
        if pn:
            parts[p['key']] = difficulty(measures(pn, pspan, tempo, tonic, minor))

    toks = tokens(notes, do, minor)
    return {
        'id': song['id'],
        'templateVersion': song['version'],
        'melodyPart': melody['key'],
        'range': {'low': min(pitches), 'high': max(pitches), 'semitones': max(pitches) - min(pitches)},
        'scale': {'notes': count, 'kind': kind, 'solfa': names, 'missing': missing},
        'mode': mode,
        'meter': {'timeSignature': song['timeSignature'], 'pickupBeats': song['pickupBeats']},
        'rhythm': {
            'notes': len(notes),
            'scotchSnaps': snaps,
            'dottedPairs': dotted,
            'syncopations': round(m['syncopationRate'] * len(notes)),
        },
        'phraseEndHold': round(hold, 2) if hold is not None else None,
        'climaxAt': round(climax, 2),
        'opening': [t[0] for t in toks[:4]],
        'ending': [t[0] for t in toks[-3:]],
        'difficulty': {'melody': parts[melody['key']], 'parts': parts},
        '_tokens': toks,
    }


def longest_run(a: list[tuple], b: list[tuple]) -> tuple[int, int, int]:
    """Length and start indexes of the longest shared run (sol-fa and interval, the first note's
    interval ignored)."""
    ka = [(t[0], t[1]) for t in a]
    kb = [(t[0], t[1]) for t in b]
    best = (0, 0, 0)
    prev = [0] * (len(kb) + 1)
    for i in range(1, len(ka) + 1):
        cur = [0] * (len(kb) + 1)
        for j in range(1, len(kb) + 1):
            if ka[i - 1][0] == kb[j - 1][0]:
                # A run continues only if the step into this note matches too.
                cur[j] = prev[j - 1] + 1 if prev[j - 1] and ka[i - 1][1] == kb[j - 1][1] else 1
                if cur[j] > best[0]:
                    best = (cur[j], i - cur[j], j - cur[j])
        prev = cur
    return best


def leaps(run: list[tuple]) -> int:
    return sum(1 for t in run[1:] if abs(t[1]) >= 3)


def kin(dna: dict[str, dict]) -> None:
    grams: dict[tuple, set] = defaultdict(set)
    for sid, d in dna.items():
        k = [(t[0], t[1]) for t in d['_tokens']]
        for i in range(1, len(k) - KIN_RUN + 2):
            grams[tuple(k[i:i + KIN_RUN - 1])].add(sid)
    pairs = set()
    for ids in grams.values():
        for a in ids:
            for b in ids:
                if a < b:
                    pairs.add((a, b))
    found: dict[str, list] = defaultdict(list)
    for a, b in sorted(pairs):
        ta, tb = dna[a]['_tokens'], dna[b]['_tokens']
        n, i, j = longest_run(ta, tb)
        same = n >= SAME_TUNE * min(len(ta), len(tb))
        if n < KIN_RUN or (not same and leaps(ta[i:i + n]) < KIN_LEAPS):
            continue
        run = [t[0] for t in ta[i:i + n]]
        kind = 'sameTune' if same else 'sharedRun'
        if same:
            run = run[:KIN_RUN]
        found[a].append({'id': b, 'kind': kind, 'notes': n, 'solfa': run, 'beat': r3(ta[i][2]), 'theirBeat': r3(tb[j][2])})
        found[b].append({'id': a, 'kind': kind, 'notes': n, 'solfa': run, 'beat': r3(tb[j][2]), 'theirBeat': r3(ta[i][2])})
    openings: dict[tuple, list] = defaultdict(list)
    for sid, d in dna.items():
        t = d['_tokens']
        if len(t) >= KIN_OPENING:
            openings[tuple((x[0], x[1]) for x in t[1:KIN_OPENING]) + (t[0][0],)].append(sid)
    for ids in openings.values():
        for a in ids:
            for b in ids:
                if a != b and not any(k['id'] == b for k in found[a]):
                    found[a].append({'id': b, 'kind': 'sameOpening', 'notes': KIN_OPENING,
                                     'solfa': [x[0] for x in dna[a]['_tokens'][:KIN_OPENING]], 'beat': 0.0, 'theirBeat': 0.0})
    for sid, d in dna.items():
        mine = d['difficulty']['melody']
        order = {'sameTune': 0, 'sharedRun': 1, 'sameOpening': 2}
        ranked = sorted(found[sid], key=lambda k: (order[k['kind']], -k['notes'],
                                                   abs(dna[k['id']]['difficulty']['melody'] - mine), k['id']))
        d['kin'] = ranked[:KIN_MAX]


def load() -> list[dict]:
    songs = []
    for f in sorted(glob.glob(os.path.join(ROOT, 'templates', 'library', '*.json')) +
                    glob.glob(os.path.join(ROOT, 'templates', 'free', '*.json'))):
        with open(f, encoding='utf-8') as fh:
            d = json.load(fh)
        if 'parts' in d:
            songs.append(d)
    return songs


def build(songs: list[dict]) -> dict[str, str]:
    dna = {s['id']: analyse(s) for s in songs if s.get('reviewed')}
    kin(dna)
    out = {}
    for sid, d in sorted(dna.items()):
        d.pop('_tokens')
        doc = {'format': FORMAT, 'generatedBy': 'tools/song_dna.py', **d}
        out[sid] = json.dumps(doc, ensure_ascii=False, indent=2) + '\n'
    return out


def report(songs: list[dict]) -> None:
    rows = [(s['id'], s['difficulty'], analyse(s)['difficulty']['melody'], s.get('reviewed')) for s in songs]
    by = defaultdict(list)
    for _, label, score, _ in rows:
        by[label].append(score)
    for label, xs in sorted(by.items()):
        xs.sort()
        print(f'{label:13} n={len(xs):3} median={xs[len(xs) // 2]:3} min={xs[0]:3} max={xs[-1]:3}')
    b, i = by.get('beginner', []), by.get('intermediate', [])
    if b and i:
        wins = sum((x > y) + 0.5 * (x == y) for x in i for y in b)
        print(f'AUC intermediate over beginner: {wins / (len(i) * len(b)):.2f}')
    hard = sorted((r for r in rows if r[1] == 'beginner'), key=lambda r: -r[2])[:8]
    print('hardest "beginner" melodies:', ', '.join(f'{r[0]} {r[2]}{"" if r[3] else "*"}' for r in hard))


def main() -> int:
    songs = load()
    if '--report' in sys.argv:
        report(songs)
        return 0
    want = build(songs)
    have = {os.path.basename(f)[:-5]: f for f in glob.glob(os.path.join(OUT, '*.json'))}
    if '--check' in sys.argv:
        bad = [sid for sid in want if sid not in have or open(have[sid], encoding='utf-8').read() != want[sid]]
        bad += [f'{sid} (no longer open)' for sid in have if sid not in want]
        if bad:
            print('song_dna: stale, run python3 -I tools/song_dna.py:', ', '.join(sorted(bad)))
            return 1
        print(f'song_dna: {len(want)} songs current')
        return 0
    os.makedirs(OUT, exist_ok=True)
    for sid, text in want.items():
        with open(os.path.join(OUT, sid + '.json'), 'w', encoding='utf-8') as fh:
            fh.write(text)
    for sid, f in have.items():
        if sid not in want:
            os.remove(f)
    print(f'song_dna: wrote {len(want)} songs')
    return 0


if __name__ == '__main__':
    sys.exit(main())
