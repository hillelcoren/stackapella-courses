"""probe.py page.pgm staff_top clef x [x ...] : measure the note standing at each x on one staff.
The five lines are found in the columns beside the note (x-16..x-7 and x+7..x+16); the head's
centre is the ink in x-4..x+4 that is not line (darker than the same row beside it), its stem
column left out. Prints the step (0 = bottom line) and the name (T treble, B bass; letter only,
the key's flats and any accidental are the reader's)."""
import sys
d = open(sys.argv[1], 'rb').read(); p = d.split(b'\n', 3); w, h = map(int, p[1].split()); px = p[3]
D = lambda x, y: 255 - px[y * w + x]
top0 = float(sys.argv[2]); clef = sys.argv[3]
TN = ['E', 'F', 'G', 'A', 'B', 'C', 'D']
names = (lambda s: '%s%d' % (TN[s % 7], 4 + (s + 2) // 7)) if clef == 'T' else (lambda s: '%s%d' % ('GABCDEF'[s % 7], 2 + (s + 5) // 7))
show = '-v' in sys.argv
exec(open(__file__.replace('probe.py', 'heads.py')).read().split('def main():')[0].split('VOC = [0]')[0])
_w, _h, _px = load(sys.argv[1])
_ref = {}
for a, b in ((240, 380), (420, 560), (700, 840)):
    gs = [g for g in lines_in(_px, _w, _h, a, b) if abs(g[0] - top0) < 6]
    if gs:
        _ref[(a + b) / 2] = min(gs, key=lambda g: abs(g[0] - top0))[0]
def top_at(x):
    ks = sorted(_ref)
    if len(ks) == 1:
        return _ref[ks[0]]
    for a, b in zip(ks, ks[1:]):
        if x <= b or b == ks[-1]:
            return _ref[a] + (_ref[b] - _ref[a]) * (x - a) / (b - a)
for xs in [a for a in sys.argv[4:] if a != '-v']:
    x = int(xs)
    side = [c for c in list(range(x - 16, x - 6)) + list(range(x + 7, x + 17)) if 0 <= c < w]
    prof = {}
    for y in range(int(top0 - 15), int(top0 + 40)):
        vals = sorted(D(c, y) for c in side)
        prof[y] = vals[len(vals) // 2]
    # five lines: best offset and spacing
    best = None
    t0 = top_at(x)
    for o10 in range(-25, 26, 1):
        for s10 in range(42, 54):
            t = t0 + o10 / 10; s = s10 / 10
            sc = 0
            for j in range(5):
                y = t + j * s; yi = int(y); f = y - yi
                sc += prof.get(yi, 0) * (1 - f) + prof.get(yi + 1, 0) * f
            if best is None or sc > best[0]:
                best = (sc, t, s)
    _, t, s = best
    lines = [t + j * s for j in range(5)]
    # head ink: darker than the row beside it
    cols = range(x - 4, x + 5)
    runs = {}
    for c in cols:
        r = m = 0
        for y in range(int(t - 3 * s), int(t + 7 * s)):
            if D(c, y) - prof.get(y, 0) > 45 or D(c, y) > 150 and prof.get(y, 0) < 60:
                r += 1; m = max(m, r)
            else:
                r = 0
        runs[c] = m
    stem = [c for c in cols if runs[c] >= 2.2 * s]
    tot = my = 0.0
    rows = {}
    for c in cols:
        if c in stem:
            continue
        for y in range(int(t - 2.6 * s), int(t + 6.6 * s)):
            e = D(c, y) - prof.get(y, 0)
            if e > 45:
                rows[y] = rows.get(y, 0) + e
    # keep the largest run of rows (the head), not stray ink
    ys = sorted(rows)
    groups = []
    for y in ys:
        if groups and y - groups[-1][-1] <= 2:
            groups[-1].append(y)
        else:
            groups.append([y])
    if not groups:
        print('x%d: nothing' % x); continue
    ok = [gg for gg in groups if 0.5 * s <= gg[-1] - gg[0] + 1 <= 1.9 * s]
    g = max(ok or groups, key=lambda gg: sum(rows[y] for y in gg))
    cy = sum(y * rows[y] for y in g) / sum(rows[y] for y in g)
    step = (lines[4] - cy) / (s / 2)
    r = round(step)
    print('x%d: step %+.2f %s  (lines %s, head rows %d-%d, stem cols %s)' % (x, step, names(r), ' '.join('%.1f' % v for v in lines), g[0], g[-1], stem))
    if show:
        for y in range(int(t - 2.5 * s), int(t + 6.5 * s)):
            mark = '<' if any(abs(y - l) < 0.6 for l in lines) else ' '
            print('   %4d%s ' % (y, mark) + ''.join(' .:-=+*#%@'[min(9, D(c, y) * 10 // 200)] for c in range(x - 7, x + 8)))
