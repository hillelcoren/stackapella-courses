"""Builds templates/library/and-the-glory-of-the-lord.json from trans.txt (Handel's voice parts as read from
Prout's full score, Novello 1902) and meta.json (the words around the music).

    python3 -I build.py [--down N] [--out PATH]

What it does to Handel's parts, in order (each one is named in the licence):
- the orchestra's bars are left out: bars 1 to 10 (the voices enter in bar 11, the alto alone), and the
  interludes, bars 39 to 42 and 74 to 75, each become one bar's rest (as the Ave verum model does);
- the closing Adagio (bars 136 to 138) is written half as slow again, one and a half times its printed
  values, since a song has one tempo; the last note, under the fermata, is held 4 beats (its 4.5 less half a
  beat), so the song ends on a whole bar;
- ties are joined into one note;
- the breaths in BREATHS are written in: the note before gives up the time (a beat at 100);
- the whole can be moved down N semitones (default 0: Handel's A major, as choirs sing it; Hillel, 2026-11-18);
- `br` marks each note that starts a new line after a rest.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trans  # noqa: E402
import chords as chordmod  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
KEYS = {'S': 'soprano', 'A': 'alto', 'T': 'tenor', 'B': 'bass'}
NAMES = {'soprano': 'Soprano', 'alto': 'Alto', 'tenor': 'Tenor', 'bass': 'Bass'}

# Handel's bar b, beat x (0, 1, 2) is hb = 3 * (b - 1) + x. The song starts on bar 11's second beat.
START = 3 * 10 + 1
CUT = [(3 * 39, 3 * 42), (3 * 74, 3 * 75)]  # Handel beats left out: bars 40 to 42, bar 75
ADAGIO = 3 * 135  # from bar 136: every beat is written as one and a half
SLOW = 1.5
FINAL = 4  # the last note's length, in beats


def song_beat(hb):
    """Template beat for Handel beat hb."""
    t = hb - START
    for a, b in CUT:
        if hb >= b:
            t -= b - a
        elif hb > a:
            raise ValueError(f'beat {hb} falls in a cut')
    if hb > ADAGIO:
        t += (hb - ADAGIO) * (SLOW - 1)
    return t


def length(hb, beats):
    return song_beat(hb + beats) - song_beat(hb)


# Breaths written in (singable rules 1 and 2: a beat's rest at 100, no line over 10 s): (voice, Handel bar,
# beat in the bar of the note that gives up time, beats it gives up, beats the next note (a pickup) starts later
# and gives up from its own length, as rule 1 allows when the note before can give only half a beat).
BREATHS = [
    # bar 36, everyone: "...of the Lord, | shall be revealed"
    ('S', 36, 0, 1, 0), ('A', 36, 0, 1, 0), ('T', 36, 0, 1, 0), ('B', 36, 0, 1, 0),
    # the tenor's first "Lord, | shall be revealed"
    ('T', 17, 0, 1, 0),
    # the alto's long "be revealed, | be revealed, | and the glory"
    ('A', 27, 1, 1, 0), ('A', 33, 0, 0.5, 0.5),
    # "For the mouth of the Lord | hath spoken it" (tenor and bass, then the soprano, then all at bar 71)
    ('T', 55, 0, 1, 0), ('B', 55, 0, 1, 0),
    ('S', 57, 0, 1, 0), ('S', 61, 0, 1, 0),
    ('T', 68, 0, 1, 0), ('T', 71, 0, 1, 0), ('B', 71, 0, 1, 0),
    # bar 79: "the glory of the Lord, | and all flesh"
    ('A', 79, 0, 0.5, 0.5), ('T', 79, 0, 0.5, 0.5),
    # "together, | the mouth" (soprano at 83), "the mouth | of the Lord" (alto at 97)
    ('S', 83, 1, 0.5, 0.5), ('A', 97, 0, 1, 0),
    # the tenor at bar 97: "the glory of the Lord, | shall be revealed"
    ('T', 97, 0, 1, 0),
    # the alto at bar 113: "the glory of the Lord | shall be revealed"
    ('A', 113, 0, 1, 0),
    # bar 119: "revealed, | and all flesh" (tenor), "revealed, | for the mouth" (bass)
    ('T', 119, 0, 0.5, 0.5), ('B', 119, 0, 0.5, 0.5), ('B', 122, 0, 1, 0),
    # bar 122: the tenor's "together, | together"; bar 124: the soprano's "together, | For the mouth of the Lord"
    ('T', 122, 1, 0.5, 0.5), ('S', 124, 0, 0.5, 0.5),
    # bar 129: "hath spoken it, | for the mouth of the Lord" (soprano and alto)
    ('S', 129, 0, 0.5, 0.5), ('A', 129, 0, 0.5, 0.5),
    # bar 102: the alto's "hath spoken it, | and all flesh"
    ('A', 102, 0, 0.5, 0.5),
]
# Notes changed in the review: (voice, Handel bar, beat in bar, old midi, new midi) at the printed pitch.
FIXES = []


def events(d, v):
    """[(hb, beats, midi, lyric)] for one voice, ties joined, bars 11 to 138."""
    out = []
    tie = False
    for b in range(1, trans.BARS + 1):
        x = 0.0
        for p, dur, lyr, t in d[v][b]:
            hb = 3 * (b - 1) + x
            x += dur
            if p is None:
                tie = False
                continue
            if tie and out and out[-1][2] == p and abs(out[-1][0] + out[-1][1] - hb) < 1e-9:
                out[-1] = (out[-1][0], out[-1][1] + dur, p, out[-1][3])
                if lyr:
                    raise ValueError(f'{v} bar {b}: a tied note with words')
            else:
                if tie:
                    raise ValueError(f'{v} bar {b}: tie to a different pitch')
                out.append((hb, dur, p, lyr))
            tie = t
    return [e for e in out if e[0] >= START]


def build(down=0):
    d = trans.read()
    meta = json.load(open(os.path.join(HERE, 'meta.json'), encoding='utf-8'))
    parts = []
    for v in 'SATB':
        ev = events(d, v)
        for fv, fb, fx, old, new in FIXES:
            if fv != v:
                continue
            hb = 3 * (fb - 1) + fx
            i = next(i for i, e in enumerate(ev) if abs(e[0] - hb) < 1e-9)
            if ev[i][2] != old:
                raise ValueError(f'fix {fv} {fb}:{fx}: found {ev[i][2]}, not {old}')
            ev[i] = (ev[i][0], ev[i][1], new, ev[i][3])
        notes = []
        for hb, dur, p, lyr in ev:
            n = {'beat': round(song_beat(hb), 6), 'length': round(length(hb, dur), 6), 'pitch': p - down}
            if lyr:
                n['lyric'] = lyr
            notes.append(n)
        for bv, bb, bx, give, later in BREATHS:
            if bv != v:
                continue
            hb = 3 * (bb - 1) + bx
            i = next(i for i, n in enumerate(notes) if abs(n['beat'] - song_beat(hb)) < 1e-9)
            nxt = notes[i + 1]
            if notes[i]['length'] - give < 0.5 - 1e-9 or nxt['length'] - later < 0.5 - 1e-9:
                raise ValueError(f'breath {bv} {bb}:{bx}: a note would be under half a beat')
            if abs(nxt['beat'] - notes[i]['beat'] - notes[i]['length']) > 1e-9:
                raise ValueError(f'breath {bv} {bb}:{bx}: there is a rest there already')
            if not nxt.get('lyric'):
                raise ValueError(f'breath {bv} {bb}:{bx}: the next note starts no words')
            notes[i]['length'] = round(notes[i]['length'] - give, 6)
            nxt['beat'] = round(nxt['beat'] + later, 6)
            nxt['length'] = round(nxt['length'] - later, 6)
        # a new line after every rest; the song's first note too
        for i, n in enumerate(notes):
            gap = n['beat'] - (notes[i - 1]['beat'] + notes[i - 1]['length']) if i else 1
            if gap > 1e-9:
                if not n.get('lyric'):
                    raise ValueError(f'{v} at {n["beat"]}: a line starting without words')
                n['br'] = True
        notes[-1]['length'] = FINAL
        key = KEYS[v]
        ps = [n['pitch'] for n in notes]
        part = {'key': key, 'name': NAMES[key], 'range': {'low': min(ps), 'high': max(ps)},
                'guide': {'type': 'notes', 'notes': notes}}
        if key == 'soprano':
            part['melody'] = True
        parts.append(part)
    song = dict(meta)
    song['key'] = ['A', 'Ab', 'G', 'F#', 'F', 'E', 'Eb'][down]
    song['chords'] = []
    for c in chordmod.chords():
        hb = max(c['hb'], START)
        if any(a < hb <= b for a, b in CUT) or (song['chords'] and song_beat(hb) <= song['chords'][-1]['beat']):
            continue
        song['chords'].append({'beat': round(song_beat(hb), 6), 'root': (c['root'] - down) % 12, 'quality': c['quality'],
                               'bass': None if c['bass'] is None else (c['bass'] - down) % 12})
    song['parts'] = parts
    return song


if __name__ == '__main__':
    down = int(sys.argv[sys.argv.index("--down") + 1]) if "--down" in sys.argv else 0
    out = sys.argv[sys.argv.index('--out') + 1] if '--out' in sys.argv else os.path.join(ROOT, 'templates', 'library', 'and-the-glory-of-the-lord.json')
    s = build(down)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(json.dumps(s, indent=1, ensure_ascii=False) + '\n')
    end = max(n['beat'] + n['length'] for p in s['parts'] for n in p['guide']['notes'])
    print(out, f'{end:g} beats, {end * 60 / s["tempo"]:.0f} s', {p['key']: (p['range']['low'], p['range']['high']) for p in s['parts']})
