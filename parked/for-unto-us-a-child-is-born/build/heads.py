# Reading aid for the full score's voice staves (pure Python): finds staff lines, bar lines and filled
# noteheads, and names each notehead's pitch from its height. Rhythm, rests, accidentals, hollow notes and
# words are read by eye from the same crop; this only removes guesswork about line-counting.
# usage: python3 -I heads.py crop.jpg CLEFS     (CLEFS top to bottom: T treble, C tenor C clef, B bass)
import sys, subprocess, struct, os
img, clefs = sys.argv[1], sys.argv[2]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scanlib
W, H, D, tilt = scanlib.load(img)
prof = [sum(D[y][0:W:2]) / (W / 2) for y in range(H)]
cand = [y for y in range(H) if prof[y] > 0.35 and (y == 0 or prof[y] >= prof[y - 1]) and (y == H - 1 or prof[y] >= prof[y + 1])]
peaks = []
for y in cand:
    if peaks and y - peaks[-1] < 4:
        if prof[y] > prof[peaks[-1]]: peaks[-1] = y
    else: peaks.append(y)
staves = []
i = 0
while i + 4 < len(peaks):
    g = peaks[i:i + 5]; dd = [g[k + 1] - g[k] for k in range(4)]
    if max(dd) - min(dd) <= 3: staves.append(g); i += 5
    else: i += 1
NAMES = 'CDEFGAB'
BASE = {'T': (2, 4), 't': (2, 3), 'C': (1, 3), 'B': (4, 2)}
for si, st in enumerate(staves):
    clef = clefs[si] if si < len(clefs) else 'T'
    sp = (st[4] - st[0]) / 4
    lo, hi = max(0, int(st[0] - 4.5 * sp)), min(H, int(st[4] + 4.5 * sp))
    if si > 0: lo = max(lo, int((staves[si - 1][4] + st[0]) / 2))
    if si + 1 < len(staves): hi = min(hi, int((st[4] + staves[si + 1][0]) / 2))
    cols = []
    for x in range(W):
        runs, start = [], None
        for y in range(lo, hi):
            if D[y][x]:
                if start is None: start = y
            elif start is not None:
                runs.append((start, y - 1)); start = None
        if start is not None: runs.append((start, hi - 1))
        cols.append([((a + b) / 2) for a, b in runs if 0.6 * sp <= b - a + 1 <= 1.45 * sp])
    # bar lines: a dark column from the top line to the bottom line, light just outside, thin
    barx = []
    for x in range(W):
        if all(D[y][x] for y in range(st[0], st[4] + 1)) and not D[int(st[0] - 0.6 * sp)][x] and not D[int(st[4] + 0.6 * sp)][x]:
            if not barx or x - barx[-1][-1] > 2: barx.append([x])
            else: barx[-1].append(x)
    bars = [sum(b) / len(b) for b in barx if len(b) <= 5]
    # notehead tracks: runs whose centre persists across neighbouring columns
    tracks = []
    for x, cs in enumerate(cols):
        for c in cs:
            for t in tracks:
                if t['x1'] >= x - 4 and abs(t['c'] - c) <= 0.3 * sp:
                    t['x1'] = x; t['ys'].append(c); t['c'] = c; break
            else:
                tracks.append({'x0': x, 'x1': x, 'c': c, 'ys': [c]})
    heads = []
    for t in tracks:
        w = t['x1'] - t['x0'] + 1
        if 0.6 * sp <= w <= 2.0 * sp:
            cy = sorted(t['ys'])[len(t['ys']) // 2]
            steps = round((st[4] - cy) / (sp / 2))
            b = BASE[clef]; n = b[0] + steps
            heads.append(((t['x0'] + t['x1']) / 2, f'{NAMES[n % 7]}{b[1] + n // 7}'))
    items = sorted([(x, '|') for x in bars] + heads)
    print(f'staff {si} {clef} sp {sp:.1f}: ' + ' '.join(p if p == '|' else f'{p}' for x, p in items))
    print('   x: ' + ' '.join('|' if p == '|' else str(round(x)) for x, p in items))
