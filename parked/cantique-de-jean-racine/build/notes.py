"""notes.py page.pgm x0 x1 : the vocal staves' notes found from their stems.
For each vocal staff (line spacing under 5.6 px), every stem (a thin vertical run at least 2.3
spaces long) gives one note; its head is the ink blob at the stem's lower end (stem up, head on
the left) or upper end (stem down, head on the right). The head's centre, with staff-line rows
left out, gives the staff step: 0 = bottom line, 1 = the space above, ... Printed per staff as
x:step(name) with 'o' for an open (white) head. Names are for treble/bass: T-name/B-name."""
import sys
exec(open(__file__.replace('notes.py', 'heads.py')).read().split('def main():')[0])

def main():
    w, h, px = load(sys.argv[1])
    X0, X1 = int(sys.argv[2]), int(sys.argv[3])
    wins = [(X0 + 60, X0 + 200), (420, 560), (X1 - 200, X1 - 60)]
    found = [lines_in(px, w, h, a, b) for a, b in wins]
    xs_ = [(a + b) / 2 for a, b in wins]
    D = lambda x, y: 255 - px[y * w + x]
    for g in found[1]:
        sp = (g[4] - g[0]) / 4
        if sp > 5.6:
            continue
        side = []
        for k in (0, 2):
            best = min(found[k], key=lambda r: abs(r[0] - g[0]), default=None)
            side.append(best if best is not None and abs(best[0] - g[0]) < 5 else g)
        st = (side[0], g, side[1])
        def liney(j, x):
            if x <= xs_[1]:
                a, b, xa, xb = st[0][j], st[1][j], xs_[0], xs_[1]
            else:
                a, b, xa, xb = st[1][j], st[2][j], xs_[1], xs_[2]
            return a + (b - a) * (x - xa) / (xb - xa)
        top = int(g[0] - 4 * sp); bot = int(g[4] + 4 * sp)
        # stems: columns with a dark vertical run >= 2.3 spaces whose neighbours 2 px away are mostly light
        stems = []
        for x in range(X0 + 40, X1):
            run = best = 0; bs = be = 0; s0 = 0
            for y in range(top, bot):
                if D(x, y) > 110:
                    if run == 0:
                        s0 = y
                    run += 1
                    if run > best:
                        best, bs, be = run, s0, y
                else:
                    run = 0
            if best >= 2.3 * sp:
                thin = sum(1 for y in range(bs, be + 1) if D(x - 2, y) < 90 and D(x + 2, y) < 90 or D(x - 3, y) < 90 and D(x + 3, y) < 90)
                if thin >= 0.5 * (be - bs + 1):
                    stems.append((x, bs, be))
        # merge adjacent stem columns
        merged = []
        for s in stems:
            if merged and s[0] - merged[-1][0] <= 2:
                merged[-1] = (merged[-1][0], min(merged[-1][1], s[1]), max(merged[-1][2], s[2]))
            else:
                merged.append(s)
        out = []
        for x, ya, yb in merged:
            # barline: spans the staff exactly with no head; candidates: head at the bottom-left or top-right
            best = None
            for hx0, hx1, hy in ((x - 8, x - 1, yb), (x + 1, x + 8, ya)):
                ys = range(int(hy - sp * 0.9), int(hy + sp * 0.9) + 1)
                tot = 0.0; my = 0.0; cnt = 0
                for y in ys:
                    if any(abs(y - liney(j, (hx0 + hx1) / 2)) < 0.8 for j in range(5)):
                        continue
                    for xx in range(hx0, hx1 + 1):
                        d = D(xx, y)
                        if d > 70:
                            tot += d; my += d * y; cnt += 1
                if cnt and (best is None or tot > best[0]):
                    best = (tot, my / tot, (hx0 + hx1) / 2, cnt)
            if best is None or best[3] < 6:
                continue
            tot, cy, hx, cnt = best
            # open head: the centre pixel row of the head is lighter than its rim
            cyi = int(round(cy)); hxi = int(round(hx))
            centre = sum(D(xx, cyi) for xx in range(hxi - 1, hxi + 2)) / 3
            step = (liney(4, hx) - cy) / (sp / 2)
            r = round(step)
            out.append('x%d:%+.1f(%s/%s)%s' % (hx, step, TN.get(r, '?'), BN.get(r, '?'), 'o' if centre < 120 else ''))
        print('staff y%.0f sp %.1f' % (g[0], sp))
        print('   ' + '  '.join(out))

main()
