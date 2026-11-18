"""Builds templates/library/for-unto-us-a-child-is-born.json from notes.txt (the reading of Prout's 1902
edition, bars 7 to 91) and meta.json: keeps Handel's key, G, writes the beginner breaths
listed in BREATHS, marks each line's first note, and adds sections, phrases and chords.
    python3 -I parked/for-unto-us-a-child-is-born/build/build.py"""
import json, os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parse

ROOT = HERE.parents[2]
SHIFT = 0  # Handel's key, G, as printed (Hillel, 2026-11-18)
NEED = 0.75  # the shortest breath at the tempo (singable rule 1: half a second, in quarter beats)
B = lambda bar, beat=1: (bar - 7) * 4 + (beat - 1)  # template beat of a bar and beat

# Each breath: (parts, where the new line starts, how), applied in order.
#   ('run', vowel): mid-run; the beat before keeps its first semiquaver, the rest of it is the breath, and
#                   the note at the new line re-sings the vowel.
#   ('cut', gap):   the note before the new line is shortened so the rest before it is `gap` beats.
#   ('split', at, gap, vowel): a held note is broken at `at`: it ends `gap` beats before, then re-sings the vowel.
BREATHS = [
    (['soprano'], B(16), ('run', '(o)')),                       # "born" run, bars 14 to 18
    (['bass'], B(22), ('run', '(o)')),                          # "born" run, bars 20 to 24
    (['alto'], B(59), ('run', '(o)')),                          # "born" run, bars 57 to 61
    (['soprano', 'alto'], B(76), ('run', '(o)')),               # the last "born" run, bars 74 to 78
    (['soprano', 'alto'], B(78, 2), ('cut', 0.75)),             # after "born", before "unto us"
    (['tenor'], B(29), ('cut', 1.0)),                           # "shoulder": the held A ends a beat early
    (['soprano'], B(31), ('cut', 1.0)),                         # "shoulder": the held A ends a beat early
    (['alto'], B(46), ('split', B(46), 1.0, '(ou)-')),          # "shoulder": the six-beat D, halved
    (['tenor'], B(63, 2), ('cut', 0.75)),                       # "shoulder": before "der;"
    (['soprano'], B(82), ('cut', 1.0)),                         # "shoulder": the held D ends a beat early
    (['alto'], B(36, 4.5), ('cut', 0.75)),                      # "Father," before "The Prince of Peace. Unto us"
    (['tenor'], B(52, 4.5), ('cut', 0.75)),                     # "Father," before "The Prince of Peace. Unto us"
    (['tenor'], B(40), ('run', '(o)')),                         # "born" run, bars 39 to 41
    (['bass'], B(24, 2), ('cut', 0.75)),                        # after "born", before "unto us"
    (['bass'], B(72, 4), ('cut', 0.75)),                        # "Prince of Peace." before "Unto us"
    (['soprano', 'alto', 'tenor', 'bass'], B(89, 4.5), ('cut', 0.75)),  # "Prince of Peace," before the last "The"
]

# Sections: the four times through "For unto us" and "Wonderful", at bar lines; phrases inside them.
SECTIONS = [
    ('For unto us', 7, 33, [7, 13, 19, 24, 28]),
    ('Wonderful', 33, 38, [33, 35]),
    ('Unto us again', 38, 49, [38, 43]),
    ('Wonderful again', 49, 54, [49, 51]),
    ('A Son is given', 54, 68, [54, 59, 62]),
    ('Wonderful, Counsellor', 68, 73, [68, 70]),
    ('For unto us, all together', 73, 85, [73, 76, 79]),
    ('The Prince of Peace', 85, 92, [85, 87, 89]),
]

# The local key from each bar: Handel's G, D and C as printed (moved with SHIFT).
KEY_REGIONS = [(bar, (key + SHIFT) % 12) for bar, key in [(7, 7), (18, 2), (38, 7), (54, 0), (59, 7), (62, 0), (71, 7)]]

QUALITIES = [('maj', (0, 4, 7)), ('min', (0, 3, 7)), ('dom7', (0, 4, 7, 10)), ('min7', (0, 3, 7, 10)),
             ('dim', (0, 3, 6)), ('maj7', (0, 4, 7, 11)), ('hdim7', (0, 3, 6, 10)), ('dim7', (0, 3, 6, 9)),
             ('sus4', (0, 5, 7))]


def name_chord(pcs, bass):
    best = None
    for root in range(12):
        for q, iv in QUALITIES:
            tones = {(root + i) % 12 for i in iv}
            if not pcs <= tones:
                continue
            # prefer full triads, the third present, the bass on the root, fewer extra tones
            score = len(pcs & tones) * 2 - len(tones) + (2 if bass == root else 0) + (1 if (root + iv[1]) % 12 in pcs else 0)
            score -= {'sus4': 3, 'dim7': 1, 'hdim7': 1, 'maj7': 1, 'dim': 1}.get(q, 0)
            if best is None or score > best[0]:
                best = (score, root, q)
    if not best:
        return None
    third = (best[1] + dict(QUALITIES)[best[2]][1]) % 12
    if best[2] != 'sus4' and third not in pcs:
        return None
    return {'root': best[1], 'quality': best[2], 'bass': None if bass == best[1] else bass}


def build():
    meta = json.loads((HERE / 'meta.json').read_text())
    parts = parse.read()
    for ns in parts.values():
        for n in ns:
            n['pitch'] += SHIFT
            n.pop('bar', None)
    for keys, at, how in BREATHS:
        for key in keys:
            ns = parts[key]
            i = next((i for i, n in enumerate(ns) if abs(n['beat'] - at) < 1e-9), None)
            assert i is not None or how[0] == 'split', (key, at)
            if how[0] == 'run':
                beat_before = [n for n in ns if at - 1 - 1e-9 <= n['beat'] < at - 1e-9]
                assert len(beat_before) == 4 and all(n['length'] == 0.25 and not n.get('lyric') for n in beat_before), (key, at)
                for n in beat_before[1:]:
                    ns.remove(n)
                i = next(i for i, n in enumerate(ns) if abs(n['beat'] - at) < 1e-9)
                assert not ns[i].get('lyric'), (key, at)
                ns[i]['lyric'] = how[1]
            elif how[0] == 'cut':
                prev = ns[i - 1]
                gap = at - (prev['beat'] + prev['length'])
                cut = how[1] - gap
                assert cut > 0 and prev['length'] - cut >= 0.25 - 1e-9, (key, at, prev)
                prev['length'] -= cut
                assert ns[i].get('lyric'), (key, at)
            elif how[0] == 'split':
                _, split_at, gap, vowel = how
                held = next(n for n in ns if n['beat'] < split_at < n['beat'] + n['length'])
                end = held['beat'] + held['length']
                held['length'] = split_at - gap - held['beat']
                again = {'beat': split_at, 'length': end - split_at, 'pitch': held['pitch'], 'lyric': vowel}
                ns.insert(ns.index(held) + 1, again)
                i = ns.index(again)
            ns[i]['br'] = True
    # every line's first note: the first, and each after a breath's worth of rest
    for ns in parts.values():
        ns[0]['br'] = True
        for prev, n in zip(ns, ns[1:]):
            if n['beat'] - (prev['beat'] + prev['length']) >= NEED - 1e-9:
                n['br'] = True
                assert n.get('lyric'), n
    # chords on each beat from the voices sounding there: three or more voices name it; where one or two
    # sing, the chord before goes on if it holds their notes, else the next named chord, else the triad
    # on the lowest note that holds them
    end = max(n['beat'] + n['length'] for ns in parts.values() for n in ns)
    tones = lambda c: {(c['root'] + i) % 12 for i in dict(QUALITIES)[c['quality']]}
    named, few = {}, {}
    for beat in range(int(end)):
        sounding = [n['pitch'] for ns in parts.values() for n in ns if n['beat'] <= beat + 1e-9 < n['beat'] + n['length']]
        if not sounding:
            continue
        pcs = {p % 12 for p in sounding}
        c = name_chord(pcs, min(sounding) % 12) if len(sounding) >= 3 and len(pcs) >= 3 else None
        if c:
            named[beat] = c
        else:
            basses = [n['pitch'] for n in parts['bass'] if n['beat'] <= beat + 1e-9 < n['beat'] + n['length']]
            few[beat] = (pcs, basses[0] % 12 if basses else None)
    chosen = {}
    for beat in range(int(end)):
        if beat in named:
            chosen[beat] = named[beat]
        elif beat in few:
            pcs, low = few[beat]
            before = chosen.get(beat - 1)
            if before and pcs <= tones(before) and (low is None or before['bass'] in (None, low) and low in tones(before)):
                chosen[beat] = before
                continue
            key = next(k for first, k in KEY_REGIONS[::-1] if beat >= B(first))
            diatonic = [{'root': (key + r) % 12, 'quality': q, 'bass': None} for r, q in
                        ((0, 'maj'), (7, 'maj'), (5, 'maj'), (9, 'min'), (2, 'min'), (7, 'dom7'), (4, 'min'))]
            fits = [c for c in diatonic if pcs <= tones(c)]
            if fits:
                c = dict(fits[0])
                if low is not None and low in tones(c) and low != c['root']:
                    c['bass'] = low
                chosen[beat] = c
                continue
            before = chosen.get(beat - 1)
            after = next((named[b] for b in sorted(named) if b > beat), None)
            if before and pcs <= tones(before):
                chosen[beat] = before
            elif after and pcs <= tones(after):
                chosen[beat] = after
            else:
                options = [{'root': r, 'quality': q, 'bass': None if low in (None, r) else low} for r in range(12) for q in ('maj', 'min', 'dom7', 'min7')
                           if pcs <= {(r + i) % 12 for i in dict(QUALITIES)[q]}]
                options.sort(key=lambda c: (c['quality'] not in ('maj', 'min'), c['bass'] is not None, c['quality'] != 'maj'))
                if options:
                    chosen[beat] = options[0]
    chords, last = [], None
    for beat in sorted(chosen):
        c = chosen[beat]
        if last is None or (c['root'], c['quality'], c['bass']) != (last['root'], last['quality'], last['bass']):
            chords.append({'beat': beat, **c})
            last = c
    sections = []
    for name, a, b, starts in SECTIONS:
        cuts = [B(s) for s in starts] + [B(b)]
        sections.append({'name': name, 'startBeat': B(a), 'endBeat': min(B(b), end),
                         'phrases': [[x, min(y, end)] for x, y in zip(cuts, cuts[1:])]})
    out_parts = []
    for key in ('soprano', 'alto', 'tenor', 'bass'):
        ns = parts[key]
        notes = []
        for n in ns:
            m = {'beat': round(n['beat'], 6), 'length': round(n['length'], 6), 'pitch': n['pitch']}
            if n.get('lyric'):
                m['lyric'] = n['lyric']
            if n.get('br'):
                m['br'] = True
            notes.append(m)
        part = {'key': key, 'name': key.capitalize()}
        if key == 'soprano':
            part['melody'] = True
        part['range'] = {'low': min(n['pitch'] for n in notes), 'high': max(n['pitch'] for n in notes)}
        part['guide'] = {'type': 'notes', 'notes': notes}
        out_parts.append(part)
    song = {k: v for k, v in meta.items() if not k.startswith('_')}
    song['chords'] = chords
    song['sections'] = sections
    song['parts'] = out_parts
    path = ROOT / 'templates' / 'library' / f"{song['id']}.json"
    path.write_text(json.dumps(song, indent=1, ensure_ascii=False) + '\n')
    print('wrote', path, 'end beat', end, 'chords', len(chords))


if __name__ == '__main__':
    build()
