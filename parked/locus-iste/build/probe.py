"""Measure note heads against the staff lines on a page scan (24-bit BMP), pure Python.

python3 -I probe.py page.bmp y_top y_bot x_from x_to
Finds the staff's five lines between y_top and y_bot (rows dark across most of
x_from..x_to), then scans columns for note heads: runs of at least 5 dark rows
that are at least 5 columns wide. Prints each head's x, centre y and its step
counted from the bottom line (0 = bottom line, 1 = first space, 2 = second line, ...).
"""
import sys

sys.path.insert(0, __file__.rsplit('/', 1)[0])
import staves  # noqa: E402


def lines_in(g, y0, y1, x0, x1, thr=170):
    score = []
    for y in range(y0, y1):
        r = g[y]
        score.append((sum(1 for x in range(x0, x1) if r[x] < thr), y))
    # pick 5 best separated peaks
    score.sort(reverse=True)
    picks = []
    for s, y in score:
        if all(abs(y - p) > 3 for p in picks):
            picks.append(y)
        if len(picks) == 5:
            break
    picks.sort()
    # refine: weighted centre of rows within 1
    out = []
    for p in picks:
        rows = [(sum(1 for x in range(x0, x1) if g[yy][x] < thr), yy) for yy in (p - 1, p, p + 1)]
        tot = sum(r for r, _ in rows) or 1
        out.append(sum(r * yy for r, yy in rows) / tot)
    return out


def heads(g, y0, y1, x0, x1, lines, thr=110):
    gap = (lines[4] - lines[0]) / 4
    line_rows = set()
    for l in lines:
        line_rows.update((round(l) - 1, round(l), round(l) + 1))
    cols = []
    for x in range(x0, x1):
        # dark rows in this column, ignoring nothing; find runs
        run = []
        best = []
        for y in range(y0, y1):
            if g[y][x] < thr:
                run.append(y)
            else:
                if len(run) >= 4:
                    best.append((run[0], run[-1]))
                run = []
        if len(run) >= 4:
            best.append((run[0], run[-1]))
        # keep runs shorter than 1.6 gaps (heads, not stems)
        cols.append([(a, b) for a, b in best if b - a + 1 <= 1.6 * gap])
    found = []
    x = 0
    n = len(cols)
    while x < n:
        if cols[x]:
            for a, b in cols[x]:
                c = (a + b) / 2
                w = 1
                while x + w < n and any(abs((aa + bb) / 2 - c) < gap * 0.6 for aa, bb in cols[x + w]):
                    w += 1
                if w >= 5:
                    found.append((x0 + x, x0 + x + w - 1, c))
            x += 1
        else:
            x += 1
    # merge duplicates
    merged = []
    for a, b, c in sorted(found):
        if merged and a <= merged[-1][1] and abs(c - merged[-1][2]) < gap * 0.6:
            continue
        merged.append((a, b, c))
    out = []
    for a, b, c in merged:
        # refine: in the head's middle columns, the extent of dark pixels within a gap of c
        mids = []
        for x in range(a + (b - a) // 4, b - (b - a) // 4 + 1):
            ys = [y for y in range(round(c - gap), round(c + gap) + 1) if g[y][x] < thr + 30]
            if ys:
                mids.append((min(ys) + max(ys)) / 2)
        mids.sort()
        cc = mids[len(mids) // 2] if mids else c
        out.append((a, b, cc, (lines[0] + 4 * gap - cc) / (gap / 2)))
    return out


def main():
    path = sys.argv[1]
    y0, y1, x0, x1 = (int(v) for v in sys.argv[2:6])
    _, _, g = staves.load(path)
    ln = lines_in(g, y0, y1, x0, x1)
    gap = (ln[4] - ln[0]) / 4
    print('lines', ' '.join('%.1f' % v for v in ln), 'gap %.2f' % gap)
    bars = [x for x in range(x0, x1) if all(g[y][x] < 150 for y in range(round(ln[0]) + 1, round(ln[4])))]
    bl = []
    for x in bars:
        if not bl or x - bl[-1][-1] > 2:
            bl.append([x])
        else:
            bl[-1].append(x)
    print('barlines', [b[0] for b in bl])
    for a, b, c, st in heads(g, round(ln[0] - 5 * gap), round(ln[4] + 5 * gap), x0, x1, ln):
        print('x %4d-%4d  y %6.1f  step %5.2f' % (a, b, c, st))


if __name__ == '__main__':
    main()
