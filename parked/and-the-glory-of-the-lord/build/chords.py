"""The chords field for And the Glory of the Lord, at Handel's pitch (A major): one chord a beat, from the
four voices sounding on it, with the orchestra's bass line (Bassi, read from the same score) where the
voices' bass rests. Repeats are merged. build.py moves the result with the song.

    python3 -I chords.py   (prints the chords bar by bar, for checking)
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import trans  # noqa: E402

# The Bassi (Handel's continuo line, played by cellos and basses) where the bass voice rests, read from
# Prout's full score: bar -> the pitch on each beat (None: resting).
P = trans.midi
BASSI = {
    11: [P('A2'), P('A2'), None], 12: [None, P('C#3'), P('A2')], 13: [P('D3'), P('B2'), P('E3')],
    14: [P('A2'), P('C#3'), P('A2')],
    17: [P('A3'), P('A2'), P('C#3')], 18: [P('F#3'), P('F#2'), P('G#2')], 19: [P('A2'), P('C#3'), P('A2')],
    22: [P('E3'), P('E3'), P('E3')], 23: [P('D#3'), P('B2'), P('E3')],
    25: [P('E3'), P('E2'), P('C#3')], 26: [P('D#3'), P('B2'), P('E3')], 27: [P('A2'), P('F#2'), P('B2')],
    28: [P('E2'), P('E3'), P('G#3')], 29: [P('B3'), P('B3'), P('G#3')], 30: [P('E3'), P('F#3'), P('E3')],
    31: [P('D#3'), P('E3'), P('B2')], 32: [P('C#3'), P('D#3'), P('D#3')], 33: [P('E3'), P('G#3'), P('E3')],
    43: [P('E3'), P('C#3'), P('A2')], 44: [P('E3'), P('C#3'), P('A2')], 45: [P('E3'), P('C#4'), P('A3')],
    46: [P('E4'), P('G#3'), P('E3')], 47: [P('A3'), P('A3'), P('G#3')], 48: [P('A3'), P('F#3'), P('D3')],
    49: [P('A3'), P('F#3'), P('D3')], 50: [P('A3'), P('F#3'), P('D3')],
    63: [P('A3'), P('C#3'), P('A2')], 64: [P('E3'), P('G#3'), P('E3')], 65: [P('B3'), P('A3'), P('G#3')],
    66: [P('F#3'), P('A3'), P('B3')], 67: [P('E3'), P('D#3'), P('C#3')],
    83: [P('A#3'), P('F#3'), None],
    89: [None, P('G#3'), P('E3')], 90: [P('B3'), P('B2'), P('E3')], 91: [P('D#3'), P('B2'), P('G#3')],
    92: [P('B3'), P('B3'), P('B2')],
    102: [P('E3'), P('C#3'), P('A2')], 103: [P('E3'), P('G#3'), P('E3')], 104: [P('A3'), P('C#3'), P('A2')],
    106: [P('F#3'), P('G#3'), P('G#3')], 107: [P('A3'), P('A2'), None], 110: [None, P('C#3'), P('A2')],
    114: [P('E3'), P('E2'), P('E3')],
}
# Chords set by hand where the voices alone can't tell (the soprano alone in bars 58, 108 and 109; the
# soprano and alto alone in 84 to 88): (bar, beat) -> (root, quality, bass or None), Handel's harmony for
# the same notes elsewhere in the chorus.
SET = {
    (58, 0): (9, 'maj', None), (58, 2): (9, 'maj', None),
    (108, 0): (4, 'maj', None), (108, 2): (9, 'maj', 1), (109, 0): (2, 'maj', 6), (109, 2): (4, 'maj', 8),
    (84, 0): (11, 'maj', None), (84, 1): (11, 'maj', 3), (84, 2): (11, 'maj', None),
    (85, 0): (11, 'maj', None), (85, 2): (11, 'maj', 3),
    (86, 0): (8, 'min7', None), (86, 1): (8, 'min7', None), (86, 2): (6, 'dom7', 10), (87, 0): (11, 'maj', None), (87, 2): (11, 'maj', None),
    (88, 0): (4, 'maj', None), (88, 2): (11, 'maj', 3),
    # where the voices' passing notes mislead the count, the chord Handel's bass and its other bars give
    (12, 1): (9, 'maj', 1), (17, 2): (9, 'maj', 1), (20, 0): (4, 'maj', 8), (20, 1): (4, 'maj', 8),
    (20, 2): (4, 'maj', 8), (21, 0): (8, 'min7', 6), (21, 1): (8, 'min7', 6), (21, 2): (8, 'min', None),
    (22, 0): (4, 'add9', None), (22, 1): (4, 'add9', None), (22, 2): (4, 'maj', None), (116, 2): (9, 'maj', None),
    (36, 2): (11, 'dom7', 6), (47, 2): (4, 'dom7', 8), (56, 1): (4, 'dom7', 11), (56, 2): (4, 'dom7', 11),
    (67, 1): (4, 'maj', None), (67, 2): (6, 'dom7', 1), (72, 2): (6, 'dom7', 1), (80, 0): (6, 'maj', 10),
    (91, 0): (11, 'maj', 3), (96, 0): (1, 'min7', None), (99, 0): (1, 'min7', None), (99, 2): (11, 'dom7', 3),
    (43, 0): (9, 'maj', 4), (43, 1): (9, 'maj', 1), (44, 0): (9, 'maj', 4), (44, 1): (9, 'maj', 1),
    (45, 0): (9, 'maj', 4), (45, 1): (9, 'maj', 1), (102, 1): (9, 'maj', 1), (111, 2): (9, 'maj', 1),
    (32, 0): (9, 'maj', 1), (32, 1): (11, 'dom7', 3), (32, 2): (11, 'dom7', 3), (105, 0): (4, 'maj', 8), (117, 0): (4, 'dom7', 11), (117, 1): (4, 'dom7', 11), (120, 0): (9, 'maj', 4),
}
QUAL = {'maj': (0, 4, 7), 'min': (0, 3, 7), 'dim': (0, 3, 6), 'dom7': (0, 4, 7, 10), 'min7': (0, 3, 7, 10),
        'hdim7': (0, 3, 6, 10), 'dim7': (0, 3, 6, 9)}
PREF = {'maj': 0.3, 'min': 0.2, 'dom7': 0, 'min7': -0.3, 'dim': -0.4, 'hdim7': -0.6, 'dim7': -0.5}


def sounding(d, v, b, beat):
    t = 0.0
    for p, dur, lyr, tie in d[v][b]:
        if t <= beat < t + dur - 1e-9:
            return p
        t += dur
    return None


def held_into(d, v, b, beat):
    """The pitch sounding at the beat, counting a note tied over the bar line."""
    p = sounding(d, v, b, beat)
    return p


def scale_near(d, b):
    """A major's notes and every accidental sung within a bar either side: the key the chord sits in."""
    pcs = {9, 11, 1, 2, 4, 6, 8}
    for v in 'SATB':
        for bb in (b - 1, b, b + 1):
            for p, dur, lyr, tie in d[v].get(bb, []):
                if p is not None:
                    pcs.add(p % 12)
    for bb in (b - 1, b, b + 1):
        for p in BASSI.get(bb, []):
            if p is not None:
                pcs.add(p % 12)
    # a sharpened note replaces its natural (D# for D, A# for A, E# for E)
    for sharp, nat in ((3, 2), (10, 9), (5, 4)):
        if sharp in pcs:
            pcs.discard(nat)
    return pcs


def best(pcs, bass, prev, scale=None):
    out = None
    for root in range(12):
        for q, iv in QUAL.items():
            ct = {(root + i) % 12 for i in iv}
            m = len(pcs & ct)
            x = len(pcs - ct)
            s = 2 * m - 3 * x + PREF[q] + (1 if bass == root else 0) + (-3 if bass is not None and bass not in ct else 0)
            if scale is not None:
                s -= 1.5 * len(ct - scale)
            if len(iv) == 4 and (root + iv[3]) % 12 not in pcs:
                s -= 2  # a seventh only when someone sings it
            if prev and (root, q) == prev[:2]:
                s += 0.4
            if out is None or s > out[0]:
                out = (s, root, q)
    return out[1], out[2]


def per_beat():
    d = trans.read()
    res = []
    prev = None
    for b in range(11, trans.BARS + 1):
        for x in range(3):
            if (b, x) in SET:
                r, q, bs = SET[(b, x)]
                prev = (r, q, bs)
                res.append((b, x, prev))
                continue
            ps = [held_into(d, v, b, x) for v in 'SATB']
            ps = [p for p in ps if p is not None]
            bassi = BASSI.get(b, [None] * 3)[x]
            low = min(ps) if ps else None
            if bassi is not None:
                ps.append(bassi)
                low = bassi if low is None else min(low, bassi)
            if not ps:
                res.append((b, x, prev))
                continue
            pcs = {p % 12 for p in ps}
            if len(pcs) == 1 and prev and next(iter(pcs)) in {(prev[0] + i) % 12 for i in QUAL[prev[1]]}:
                res.append((b, x, prev))
                continue
            root, q = best(pcs, low % 12, prev, scale_near(d, b))
            bs = None if low % 12 == root else low % 12
            prev = (root, q, bs)
            res.append((b, x, prev))
    return res


def chords():
    """[{beat (Handel beat), root, quality, bass}] with repeats merged."""
    out = []
    for b, x, c in per_beat():
        if c is None:
            continue
        hb = 3 * (b - 1) + x
        if out and (out[-1]['root'], out[-1]['quality'], out[-1]['bass']) == c:
            continue
        out.append({'hb': hb, 'root': c[0], 'quality': c[1], 'bass': c[2]})
    return out


if __name__ == '__main__':
    N = 'C C# D D# E F F# G G# A A# B'.split()
    cur = None
    line = ''
    for b, x, c in per_beat():
        if b != cur:
            if line:
                print(line)
            cur = b
            line = f'{b:3d}:'
        line += '  ' + ('-' if c is None else N[c[0]] + {'maj': '', 'min': 'm', 'dom7': '7', 'min7': 'm7', 'dim': 'dim', 'hdim7': 'm7b5', 'dim7': 'dim7'}[c[1]] + ('' if c[2] is None else '/' + N[c[2]]))
    print(line)
