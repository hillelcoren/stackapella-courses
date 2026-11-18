"""heads.py page.pgm [x0 x1] : find the staves on a scanned page and the noteheads on each.
Prints, per staff (top down), its line positions and each notehead as x, staff step (0 = bottom
line, 1 = the space above it, -1 = the space below...) and whether it looks filled or open.
Pitches are named later by the reader, from the clef and key; this only measures."""
import sys

def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = map(int, parts[1].split())
    return w, h, bytearray(parts[3])

def lines_in(px, w, h, x0, x1):
    rows = []
    for y in range(h):
        seg = px[y * w + x0:y * w + x1]
        rows.append(sum(1 for v in seg if v < 170) / (x1 - x0))
    groups = []
    for y in range(h):
        if rows[y] > 0.45:
            if groups and y - groups[-1][-1] <= 1:
                groups[-1].append(y)
            else:
                groups.append([y])
    cs = [sum(y * rows[y] for y in g) / sum(rows[y] for y in g) for g in groups]
    staves = []
    i = 0
    while i + 4 < len(cs):
        g = cs[i:i + 5]
        gaps = [g[k + 1] - g[k] for k in range(4)]
        if max(gaps) - min(gaps) <= 2.0 and 3.5 <= min(gaps) <= 9:
            staves.append(g)
            i += 5
        else:
            i += 1
    return staves

VOC = [0]
TN = {-4: 'A3', -3: 'B3', -2: 'C4', -1: 'D4', 0: 'E4', 1: 'F4', 2: 'G4', 3: 'A4', 4: 'B4', 5: 'C5', 6: 'D5', 7: 'E5', 8: 'F5', 9: 'G5', 10: 'A5', 11: 'B5'}
BN = {-4: 'C2', -3: 'D2', -2: 'E2', -1: 'F2', 0: 'G2', 1: 'A2', 2: 'B2', 3: 'C3', 4: 'D3', 5: 'E3', 6: 'F3', 7: 'G3', 8: 'A3', 9: 'B3', 10: 'C4', 11: 'D4', 12: 'E4'}

def main():
    w, h, px = load(sys.argv[1])
    X0 = int(sys.argv[2]) if len(sys.argv) > 2 else 60
    X1 = int(sys.argv[3]) if len(sys.argv) > 3 else w - 60
    # staff lines measured in three windows, matched to the centre one, interpolated across
    wins = [(X0 + 60, X0 + 200), (420, 560), (X1 - 200, X1 - 60)]
    found = [lines_in(px, w, h, a, b) for a, b in wins]
    xs_ = [(a + b) / 2 for a, b in wins]
    pairs = []
    for g in found[1]:
        side = []
        for k in (0, 2):
            best = min(found[k], key=lambda r: abs(r[0] - g[0]), default=None)
            side.append(best if best is not None and abs(best[0] - g[0]) < 5 else g)
        pairs.append((side[0], g, side[1]))
    def liney(st, j, x):
        if x <= xs_[1]:
            a, b, xa, xb = st[0][j], st[1][j], xs_[0], xs_[1]
        else:
            a, b, xa, xb = st[1][j], st[2][j], xs_[1], xs_[2]
        return a + (b - a) * (x - xa) / (xb - xa)
    dark = lambda x, y: px[y * w + x] < 150
    for si, st in enumerate(pairs):
        sp = (st[1][4] - st[1][0]) / 4
        top = int(min(st[0][0], st[1][0], st[2][0]) - 3.5 * sp)
        bot = int(max(st[0][4], st[1][4], st[2][4]) + 3.5 * sp)
        # mask: dark pixels, minus staff-line pixels with light above and below, minus thin vertical strokes
        H = bot - top
        m = [[False] * w for _ in range(H)]
        for y in range(top, bot):
            for x in range(X0, X1):
                if not dark(x, y):
                    continue
                on_line = any(abs(y - liney(st, j, x)) <= 1.0 for j in range(5)) or any(abs(y - (liney(st, 0, x) - k * sp)) <= 1.0 for k in (1, 2)) and False
                if on_line and not dark(x, y - 2) and not dark(x, y + 2):
                    continue
                m[y - top][x] = True
        # remove thin vertical strokes (stems, bar lines): horizontal run <= 2
        m2 = [[False] * w for _ in range(H)]
        for yy in range(H):
            row = m[yy]
            x = X0
            while x < X1:
                if row[x]:
                    s = x
                    while x < X1 and row[x]:
                        x += 1
                    if x - s >= 3:
                        for k in range(s, x):
                            m2[yy][k] = True
                else:
                    x += 1
        # connected components
        seen = [[False] * w for _ in range(H)]
        heads = []
        for yy in range(H):
            for x in range(X0, X1):
                if m2[yy][x] and not seen[yy][x]:
                    stack = [(yy, x)]
                    seen[yy][x] = True
                    pts = []
                    while stack:
                        cy, cx = stack.pop()
                        pts.append((cy, cx))
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and X0 <= nx < X1 and m2[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True
                                stack.append((ny, nx))
                    ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                    bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
                    if 0.9 * sp <= bw <= 2.2 * sp and 0.6 * sp <= bh <= 1.7 * sp and len(pts) >= 0.35 * bw * bh:
                        cy = sum(ys) / len(ys) + top
                        cx = sum(xs) / len(xs)
                        fill = len(pts) / (bw * bh)
                        bl = liney(st, 4, cx)
                        step = (bl - cy) / (sp / 2)
                        heads.append((cx, step, fill, bw, bh))
        heads.sort()
        if sp > 5.6:
            continue  # the piano's staves (wider) are left out
        def nm(stp):
            r = round(stp)
            return '%s/%s' % (TN.get(r, '?'), BN.get(r, '?'))
        print('staff %d y%.0f sp %.1f' % (si, st[1][0], sp))
        print('   ' + '  '.join('x%d:%s(%+.1f)%s' % (hx, nm(stp), stp, '' if fl > 0.72 else 'o') for hx, stp, fl, bw, bh in heads if hx > 100))

main()
