# Builds templates/library/hallelujah-chorus.json from trans.txt (Handel's four voice parts as Prout's
# 1902 Novello edition prints them, read from the scans) and meta.json, with the changes listed in
# SHORTEN and DELAY (breaths for beginners), in Handel's key, D.
# Run: python3 -I build.py   (writes the template and prints what it changed)
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parse import load, FIRST_BAR  # noqa: E402

ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SHIFT = 0
PART_KEYS = {'S': 'soprano', 'A': 'alto', 'T': 'tenor', 'B': 'bass'}


def at(bar, beat):
    """Score bar and beat (1-based) to the template's beat (bar 4, beat 1 is 0)."""
    return (bar - FIRST_BAR) * 4 + (beat - 1)


# Breaths written in for beginners. Each: (parts, bar, beat of the note that ends, new length, why).
# The note's end moves earlier, leaving a rest before the next line (singable rule 1).
SHORTEN = [
    # "for the Lord God Omnipotent | reigneth": a quick breath before "reign"
    ('SATB', 13, 4, 0.5, 'tent'), ('S', 23, 4, 0.5, 'tent'), ('A', 18, 4, 0.5, 'tent'),
    ('T', 18, 4, 0.5, 'tent'), ('B', 18, 4, 0.5, 'tent'), ('B', 26, 4, 0.5, 'tent'),
    ('T', 26, 4, 0.5, 'tent'), ('A', 30, 4, 0.5, 'tent'),
    ('T', 30, 4, 0.5, 'tent'),
    # tenor bar 31: "reign-eth, | Hal-le-lu-jah"
    ('T', 31, 3, 1, 'eth,'),
    # soprano bar 31: "Hal-le-lu-jah, | Hal-le-lu-jah!"
    ('S', 31, 3, 0.5, 'jah,'),
    # "this world" held a beat less, so the line is 8 seconds
    ('SATB', 35, 1, 3, 'world'),
    # "is become | the Kingdom of our Lord, | and of His Christ, | and of His Christ;"
    ('SATB', 37, 1, 2.5, 'come'), ('SATB', 39, 1, 1, 'Lord'), ('SATB', 40, 1, 1, 'Christ,'),
    ('B', 41, 1, 1, 'Christ;'),
    # "and He shall reign | for ever and ever": a quick breath before "for"
    ('B', 42, 1, 0.5, 'reign'), ('T', 44, 3, 0.5, 'reign'), ('A', 47, 1, 0.5, 'reign'),
    ('S', 49, 3, 0.5, 'reign'), ('S', 72, 3, 0.5, 'reign'), ('T', 72, 3, 1, 'reign'),
    ('A', 72, 3, 0.5, 'reign (its last note)'),
    ('SB', 79, 1, 0.5, 'reign'), ('T', 79, 1, 0.5, 'reign'), ('A', 79, 3, 0.5, 'reign'),
    ('S', 86, 3, 0.5, 'reign'), ('A', 86, 3, 0.5, 'reign'), ('T', 86, 3, 0.5, 'reign'),
    ('B', 86, 1, 0.5, 'reign'), ('B', 70, 1, 0.5, 'reign'),
    # "for ever and ever. | King of Kings"
    ('S', 51, 1, 1.5, 'er.'), ('A', 51, 2, 0.5, 'er.'), ('T', 74, 1, 1.5, 'er,'), ('A', 74, 1, 1.5, 'er,'),
    ('B', 74, 2, 0.5, 'er,'),
    # the long "Kings" and "Lords": each line at most 9 seconds, then a breath
    ('SA', 52, 1, 7, 'Kings,'), ('S', 55, 1, 6, 'Lords,'), ('A', 55, 1, 6, 'Lords,'),
    ('S', 58, 1, 7, 'Kings,'), ('S', 61, 1, 6, 'Lords,'), ('S', 64, 1, 6.5, 'Kings,'),
    ('S', 67, 1, 5, 'Lords,'), ('T', 75, 1, 5, 'Kings,'),
    # bass: "King of Kings, | and Lord of Lords, | and He shall reign"
    ('B', 69, 1, 1, 'Lords,'),
    # bass bar 88: "ever, | for ever and ever" after an eight-second line
    ('B', 88, 1, 0.5, 'er,'),
]

# Pitches changed for voices (none: in D the alto's octave drop on "Om-", G3 at bars 18 and 30, is inside
# the app's hard alto range, so Handel's note is sung).
REPITCH = []

# The tenor's "for" (bars 25 and 29) comes half a beat late, after a breath: Handel's "Hal-le-lu-jah!"
# runs straight into it on an eighth note, too short to give up anything.
DELAY = [('T', 25, 1, 0.5, 'for'), ('T', 29, 1, 0.5, 'for')]


def build():
    parts, problems = load()
    if problems:
        sys.exit('\n'.join(problems))
    notes = {}
    log = []
    for k, ns in parts.items():
        notes[k] = [{'beat': b, 'length': l, 'pitch': n + SHIFT, 'lyric': ly} for b, l, n, ly in ns]
    for who, bar, beat, new, word in SHORTEN:
        b = at(bar, beat)
        for k in who:
            hit = [n for n in notes[k] if abs(n['beat'] - b) < 1e-9]
            if len(hit) != 1:
                sys.exit(f'SHORTEN: no {k} note at bar {bar} beat {beat} ({word})')
            n = hit[0]
            if new >= n['length']:
                sys.exit(f'SHORTEN: {k} bar {bar} beat {beat} is {n["length"]}, not longer than {new}')
            log.append(f'{PART_KEYS[k]} bar {bar} beat {beat:g} "{n["lyric"] or word}": {n["length"]:g} to {new:g} beats')
            n['length'] = new
    for who, bar, beat, pitch, word in REPITCH:
        b = at(bar, beat)
        for k in who:
            n = next(n for n in notes[k] if abs(n['beat'] - b) < 1e-9)
            log.append(f'{PART_KEYS[k]} bar {bar} beat {beat:g} "{n["lyric"]}": pitch {n["pitch"]} to {pitch}')
            n['pitch'] = pitch
    for who, bar, beat, by, word in DELAY:
        b = at(bar, beat)
        for k in who:
            n = next(n for n in notes[k] if abs(n['beat'] - b) < 1e-9)
            log.append(f'{PART_KEYS[k]} bar {bar} beat {beat:g} "{n["lyric"]}": starts {by:g} beat later ({n["length"]:g} to {n["length"] - by:g})')
            n['beat'] += by
            n['length'] -= by
    meta = json.load(open(os.path.join(HERE, 'meta.json'), encoding='utf-8'))
    out_parts = []
    for k in 'SATB':
        ns = sorted(notes[k], key=lambda n: n['beat'])
        guide = []
        prev_end = None
        for i, n in enumerate(ns):
            g = {'beat': round(n['beat'], 6), 'length': round(n['length'], 6), 'pitch': n['pitch']}
            if n['lyric']:
                g['lyric'] = n['lyric']
            if i == 0 or (n['beat'] - prev_end >= 0.5 - 1e-9 and n['lyric']):
                g['br'] = True
            guide.append(g)
            prev_end = n['beat'] + n['length']
        pitches = [g['pitch'] for g in guide]
        part = {'key': PART_KEYS[k], 'name': PART_KEYS[k].capitalize(), 'range': {'low': min(pitches), 'high': max(pitches)},
                'guide': {'type': 'notes', 'notes': guide}}
        if k == 'S':
            part['melody'] = True
        out_parts.append(part)
    t = dict(meta)
    t['sections'] = sections(notes)
    t['chords'] = chords(notes)
    t['parts'] = out_parts
    path = os.path.join(ROOT, 'templates', 'library', 'hallelujah-chorus.json')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(t, indent=1, ensure_ascii=False) + '\n')
    return log


SECTIONS = [
    ('Hallelujah', 4, 12),
    ('For the Lord God Omnipotent reigneth', 12, 33),
    ('The kingdom of this world', 33, 41),
    ('And He shall reign', 41, 51),
    ('King of Kings', 51, 69),
    ('And He shall reign, again', 69, 81),
    ('King of Kings, and Hallelujah', 81, 95),
]


def pickup_before(notes, x):
    """The earliest onset in the beat before x that starts a part's line after a rest (a pickup into x)."""
    best = x
    for ns in notes.values():
        ns = sorted(ns, key=lambda n: n['beat'])
        for prev, n in zip(ns, ns[1:]):
            if x - 1 - 1e-9 <= n['beat'] < x - 1e-9 and n['beat'] - (prev['beat'] + prev['length']) >= 0.5 - 1e-9:
                best = min(best, n['beat'])
    return best


def sections(notes):
    out = []
    for name, a, b in SECTIONS:
        s, e = at(a, 1), at(b, 1)
        phrases = []
        x = s
        while x < e:
            y = min(x + 8, e)
            if e - y < 4 and y < e:
                y = e
            if y < e:
                y = pickup_before(notes, y)
            phrases.append([x, y])
            x = y
        out.append({'name': name, 'startBeat': s, 'endBeat': e, 'phrases': phrases})
    return out


SHAPES = [('maj', (0, 4, 7)), ('min', (0, 3, 7)), ('dom7', (0, 4, 7, 10)), ('min7', (0, 3, 7, 10)),
          ('dim', (0, 3, 6)), ('maj7', (0, 4, 7, 11)), ('dim7', (0, 3, 6, 9)), ('hdim7', (0, 3, 6, 10)),
          ('sus4', (0, 5, 7))]


def chords(notes):
    """The chord on each beat, read from the four voices: the shape that covers the most of what is sung
    in the beat (weighted by length; the bass note as root preferred, the chord before kept when it fits).
    A beat sung in unison or by one voice alone takes the chord around it that holds its note. Changes only."""
    end = max(n['beat'] + n['length'] for ns in notes.values() for n in ns)
    STEP = 0.5
    beats = int(round(end / STEP))
    found = []
    for i in range(beats):
        t = i * STEP
        weight = {}
        low = None
        for k in 'SATB':
            for n in notes[k]:
                a, b = max(n['beat'], t), min(n['beat'] + n['length'], t + STEP)
                if b - a > 1e-9:
                    w = (b - a) * (3 if n['beat'] <= t + 1e-9 else 1)
                    weight[n['pitch'] % 12] = weight.get(n['pitch'] % 12, 0) + w
                    if n['beat'] <= t + 1e-9 and (low is None or n['pitch'] < low):
                        low = n['pitch']
        found.append((weight, None if low is None else low % 12))
    out = []
    last = None
    picks = []
    for i, (weight, bass) in enumerate(found):
        if len(weight) < 2:
            picks.append(None)
            continue
        best = None
        total = sum(weight.values())
        for root in range(12):
            for q, ints in SHAPES:
                shape = {(root + x) % 12 for x in ints}
                covered = sum(w for pc, w in weight.items() if pc in shape)
                score = (total - covered) * 3 + (0 if root == bass else 0.8) + (1.0 if q not in ('maj', 'min') else 0)
                score += 0.6 * len(shape - set(weight))
                if q == 'sus4':
                    score += 2
                if last and (root, q) == last[:2]:
                    score -= 0.7
                if best is None or score < best[0]:
                    best = (score, root, q)
        _, root, q = best
        last = (root, q, None if bass == root else bass)
        picks.append(last)
    # one voice or a unison: the chord before (or after) that holds the note
    for i, p in enumerate(picks):
        if p is not None:
            continue
        weight, bass = found[i]
        if not weight:
            continue
        pc = next(iter(weight))
        def holds(c):
            return c is not None and pc in {(c[0] + x) % 12 for x in dict(SHAPES)[c[1]]}
        before = next((picks[j] for j in range(i - 1, -1, -1) if picks[j] is not None), None)
        after = next((picks[j] for j in range(i + 1, len(picks)) if picks[j] is not None), None)
        if holds(before):
            picks[i] = (before[0], before[1], None)
        elif holds(after):
            picks[i] = (after[0], after[1], None)
        else:
            scale = {(2 + x) % 12 for x in (0, 2, 4, 5, 7, 9, 11)}  # D major, the key here
            picks[i] = (pc, 'min' if (pc + 3) % 12 in scale and (pc + 4) % 12 not in scale else 'maj', None)
    prev = None
    for i, p in enumerate(picks):
        if p is None:
            continue
        root, q, b = p
        b = None if b == root else b
        if (root, q, b) != prev:
            out.append({'beat': i * STEP, 'root': root, 'quality': q, 'bass': b})
            prev = (root, q, b)
    return out


if __name__ == '__main__':
    for line in build():
        print(line)
