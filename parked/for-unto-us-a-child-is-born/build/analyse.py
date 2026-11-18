"""Reading aid: range excursions by key, and each part's lines over 7.5 s (rests of 0.75 beat or more break a line)."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse
ps = parse.read()
T = 76; sec = 60 / T
R = {"soprano": (62, 76), "alto": (55, 72), "tenor": (48, 65), "bass": (41, 58)}
for shift in range(-6, 3):
    out = {k: sum(1 for n in ns if not R[k][0] <= n['pitch'] + shift <= R[k][1]) for k, ns in ps.items()}
    print('shift', shift, out, sum(out.values()))
for k, ns in ps.items():
    start = ns[0]['beat']; runs = []
    for p, n in zip(ns, ns[1:]):
        gap = n['beat'] - p['beat'] - p['length']
        if gap >= 0.75 - 1e-9:
            runs.append((start, p['beat'] + p['length'])); start = n['beat']
    runs.append((start, ns[-1]['beat'] + ns[-1]['length']))
    longs = [(a, b, round((b - a) * sec, 1)) for a, b in runs if (b - a) * sec > 7.5]
    print(k, 'lines', len(runs), 'over 7.5 s:', [(f'bar {7 + a / 4:.2f}-{7 + b / 4:.2f}', s) for a, b, s in longs])
