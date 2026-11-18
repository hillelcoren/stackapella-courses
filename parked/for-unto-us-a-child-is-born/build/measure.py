# Reading aid: measure staff lines and notehead heights in a cropped score image (pure Python).
# usage: python3 -I measure.py crop.jpg CLEFS X1,X2,... [X...]
#   CLEFS: one letter per staff top to bottom (T treble, t tenor-octave treble, B bass, C tenor C-clef on line 4)
#   one comma list of x positions (crop pixels) per staff; "-" skips a staff.
import sys, subprocess, struct, os
img, clefs, xs = sys.argv[1], sys.argv[2], sys.argv[3:]
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import scanlib
W, H, D, tilt = scanlib.load(img)
def dark(x, y):
    return D[y][x]
prof = [sum(dark(x, y) for x in range(0, W, 3)) / (W / 3) for y in range(H)]
cand = [y for y in range(H) if prof[y] > 0.35 and (y == 0 or prof[y] >= prof[y - 1]) and (y == H - 1 or prof[y] >= prof[y + 1])]
peaks = []
for y in cand:
    if peaks and y - peaks[-1] < 4:
        if prof[y] > prof[peaks[-1]]: peaks[-1] = y
    else:
        peaks.append(y)
staves = []
i = 0
while i + 4 < len(peaks):
    g = peaks[i:i + 5]; dd = [g[k + 1] - g[k] for k in range(4)]
    if max(dd) - min(dd) <= 3: staves.append(g); i += 5
    else: i += 1
NAMES = 'CDEFGAB'
BASE = {'T': (2, 4), 't': (2, 3), 'B': (4, 2), 'C': (1, 3)}  # bottom line: E4, E3 (8vb), G2, tenor C clef bottom line D3
print('staves', staves)
for si, st in enumerate(staves):
    if si >= len(xs) or xs[si] == '-': continue
    sp = (st[4] - st[0]) / 4
    clef = clefs[si]
    out = []
    for x in map(int, xs[si].split(',')):
        # dark rows in a narrow strip, ignoring staff-line rows
        rows = []
        for y in range(max(0, int(st[0] - 5 * sp)), min(H, int(st[4] + 5 * sp))):
            c = sum(dark(xx, y) for xx in range(max(0, x - int(sp * 0.35)), min(W, x + int(sp * 0.35))))
            rows.append((y, c / (2 * int(sp * 0.35))))
        # longest run of rows that are mostly dark
        best, cur = [], []
        for y, f in rows:
            if f > 0.6: cur.append(y)
            else:
                if len(cur) > len(best): best = cur
                cur = []
        if len(cur) > len(best): best = cur
        if not best: out.append(f'{x}:?'); continue
        cy = (best[0] + best[-1]) / 2
        steps = round((st[4] - cy) / (sp / 2))
        b = BASE[clef]; n = b[0] + steps
        out.append(f'{x}:{NAMES[n % 7]}{b[1] + n // 7}(h{len(best)})')
    print(f'staff {si} {clef} lines {st} sp {sp:.1f}:', ' '.join(out))
