"""heads2.py page.pgm x0 x1 [ytop ...] : noteheads on the vocal staves, measured against the staff
lines where each note stands (pages are skewed). Staff lines are found per 24-px block of columns;
the ink left after taking away each row's running horizontal median (the lines) and thin vertical
strokes (stems, bar lines) is grouped into blobs; blobs of a notehead's size are reported as
x:step(treble/bass name), step 0 = bottom line; 'o' marks an open head (light centre)."""
import sys
exec(open(__file__.replace('heads2.py', 'heads.py')).read().split('def main():')[0])

INK = 100

def main():
    w, h, px = load(sys.argv[1])
    X0, X1 = int(sys.argv[2]), int(sys.argv[3])
    D = lambda x, y: 255 - px[y * w + x]
    tops = [float(a) for a in sys.argv[4:]]
    if not tops:
        tops = [g[0] for g in lines_in(px, w, h, 420, 560) if (g[4] - g[0]) / 4 < 5.6]
        cen = {g[0]: g for g in lines_in(px, w, h, 420, 560)}
    else:
        cen = {}
    allc = lines_in(px, w, h, 420, 560)
    for t in tops:
        g = min(allc, key=lambda r: abs(r[0] - t))
        sp = (g[4] - g[0]) / 4
        rel = [v - g[0] for v in g]
        # local offset of the staff per block of columns
        offs = {}
        prev = 0.0
        blocks = list(range(X0, X1, 12))
        # walk outwards from the centre so the offset follows the skew smoothly
        centre_i = min(range(len(blocks)), key=lambda i: abs(blocks[i] - 490))
        order = list(range(centre_i, len(blocks))) + list(range(centre_i - 1, -1, -1))
        last = {}
        for i in order:
            bx = blocks[i]
            ref = last.get(i - 1 if i > centre_i else i + 1, 0.0)
            best = None
            for o10 in range(int((ref - 3) * 10), int((ref + 3) * 10) + 1, 2):
                o = o10 / 10
                s = 0.0
                for r in rel:
                    y = g[0] + o + r
                    yi = int(y); fr = y - yi
                    for x in range(bx, min(bx + 24, X1)):
                        s += D(x, yi) * (1 - fr) + D(x, yi + 1) * fr
                if best is None or s > best[0]:
                    best = (s, o)
            last[i] = best[1]
            offs[bx] = best[1]
        def off(x):
            ks = sorted(offs)
            if x <= ks[0] + 12: return offs[ks[0]]
            if x >= ks[-1] + 12: return offs[ks[-1]]
            for a, b in zip(ks, ks[1:]):
                if a + 12 <= x <= b + 12:
                    return offs[a] + (offs[b] - offs[a]) * (x - a - 12) / (b - a)
            return 0.0
        top = int(g[0] - 4.5 * sp); bot = int(g[4] + 4.5 * sp)
        H = bot - top
        # residual ink: darkness minus the row's running median over 21 px
        res = [[0] * w for _ in range(H)]
        for yy in range(H):
            y = top + yy
            row = [D(x, y) for x in range(w)]
            for x in range(X0, X1):
                win = sorted(row[max(0, x - 10):x + 11])
                med = win[len(win) // 2]
                res[yy][x] = row[x] - med
        def ink(x, y):
            return D(x, y) > INK
        mask = [[False] * w for _ in range(H)]
        for yy in range(H):
            y = top + yy
            for x in range(X0, X1):
                if ink(x, y) and (res[yy][x] > 50 or (ink(x, y - 2) and ink(x, y + 2)) or (ink(x, y - 1) and ink(x, y + 1) and res[yy][x] > 25)):
                    mask[yy][x] = True
        m2 = [[False] * w for _ in range(H)]
        for yy in range(H):
            x = X0
            while x < X1:
                if mask[yy][x]:
                    s = x
                    while x < X1 and mask[yy][x]:
                        x += 1
                    if x - s >= 3:
                        for k in range(s, x):
                            m2[yy][k] = True
                else:
                    x += 1
        # close small gaps (open heads cut by a staff line): a pixel joins if ink lies on both sides of it
        m3 = [row[:] for row in m2]
        for yy in range(1, H - 1):
            for x in range(X0 + 1, X1 - 1):
                if not m2[yy][x] and ((m2[yy - 1][x] and m2[yy + 1][x]) or (m2[yy][x - 1] and m2[yy][x + 1])):
                    m3[yy][x] = True
        m2 = m3
        seen = [[False] * w for _ in range(H)]
        heads = []
        for yy in range(H):
            for x in range(X0, X1):
                if m2[yy][x] and not seen[yy][x]:
                    stack = [(yy, x)]; seen[yy][x] = True; pts = []
                    while stack:
                        cy, cx = stack.pop(); pts.append((cy, cx))
                        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)):
                            ny, nx = cy + dy, cx + dx
                            if 0 <= ny < H and X0 <= nx < X1 and m2[ny][nx] and not seen[ny][nx]:
                                seen[ny][nx] = True; stack.append((ny, nx))
                    ys = [p[0] for p in pts]; xs = [p[1] for p in pts]
                    bw, bh = max(xs) - min(xs) + 1, max(ys) - min(ys) + 1
                    if 0.9 * sp <= bw <= 2.0 * sp and 0.7 * sp <= bh <= 1.6 * sp and len(pts) >= 0.3 * bw * bh:
                        wsum = sum(max(1, D(p[1], p[0] + top)) for p in pts)
                        cy = sum(max(1, D(p[1], p[0] + top)) * (p[0] + top) for p in pts) / wsum
                        cx = sum(xs) / len(xs)
                        o = off(cx)
                        bl = g[4] + o
                        step = (bl - cy) / (sp / 2)
                        cyi, cxi = int(round(cy)) - top, int(round(cx))
                        centre = sum(res[cyi][xx] for xx in (cxi - 1, cxi, cxi + 1)) / 3
                        heads.append((cx, step, centre < 60, bw, bh))
        heads.sort()
        def nm(stp):
            r = round(stp)
            return '%s/%s' % (TN.get(r, '?'), BN.get(r, '?'))
        print('staff y%.0f sp %.1f' % (g[0], sp))
        print('   ' + '  '.join('x%d:%+.1f(%s)%s' % (hx, stp, nm(stp), 'o' if op else '') for hx, stp, op, bw, bh in heads))

main()
