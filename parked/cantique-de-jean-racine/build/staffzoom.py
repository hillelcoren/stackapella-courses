"""staffzoom.py page.pgm x0 x1 y0 y1 scale out.ppm [clefs]
Enlarge a region of a scanned page and colour the staff positions on the paper (not on the ink):
lines red, spaces green, the first ledger line and space above and below orange and blue.
Prints each staff's line centres (original pixels) and, with clefs (e.g. TTTB: treble or bass per
staff, top down), the pitch name of each line, bottom up."""
import sys

def load(path):
    d = open(path, 'rb').read()
    parts = d.split(b'\n', 3)
    w, h = map(int, parts[1].split())
    return w, h, parts[3]

def main():
    pgm, x0, x1, y0, y1, s, out = sys.argv[1], *map(int, sys.argv[2:7]), sys.argv[7]
    clefs = sys.argv[8] if len(sys.argv) > 8 else ''
    w, h, px = load(pgm)
    rows = []
    for y in range(y0, y1):
        line = px[y * w + x0:y * w + x1]
        rows.append(sum(1 for v in line if v < 170) / max(1, len(line)))
    cand = [y0 + i for i, f in enumerate(rows) if f > 0.45]
    lines = []
    for y in cand:
        if lines and y - lines[-1][-1] <= 1:
            lines[-1].append(y)
        else:
            lines.append([y])
    centres = [sum(y * rows[y - y0] for y in l) / sum(rows[y - y0] for y in l) for l in lines]
    staves = []
    i = 0
    while i + 4 < len(centres):
        g = centres[i:i + 5]
        gaps = [g[k + 1] - g[k] for k in range(4)]
        if max(gaps) - min(gaps) <= 2.5 and 3 <= min(gaps) <= 12:
            staves.append(g)
            i += 5
        else:
            i += 1
    names_t = ['E4', 'G4', 'B4', 'D5', 'F5']
    names_b = ['G2', 'B2', 'D3', 'F3', 'A3']
    for k, g in enumerate(staves):
        c = clefs[k] if k < len(clefs) else '?'
        nm = names_t if c == 'T' else names_b if c == 'B' else ['?'] * 5
        print('staff', k, c, ' '.join('%s@%.1f' % (nm[4 - j], g[j]) for j in range(5)))
    marks = {}
    for g in staves:
        sp = (g[4] - g[0]) / 4
        for j in range(5):
            marks[round(g[j] * s)] = (220, 40, 40)
        for j in range(4):
            marks[round((g[j] + sp / 2) * s)] = (40, 170, 40)
        marks[round((g[0] - sp) * s)] = (240, 140, 0)
        marks[round((g[0] - sp / 2) * s)] = (60, 90, 230)
        marks[round((g[4] + sp) * s)] = (240, 140, 0)
        marks[round((g[4] + sp / 2) * s)] = (60, 90, 230)
    W, H = (x1 - x0) * s, (y1 - y0) * s
    buf = bytearray(W * H * 3)
    for Y in range(H):
        sy = y0 + Y // s
        row = px[sy * w:(sy + 1) * w]
        col = marks.get(Y + y0 * s)
        base = Y * W * 3
        for X in range(W):
            v = row[x0 + X // s]
            o = base + X * 3
            if col and v > 150:
                buf[o], buf[o + 1], buf[o + 2] = col
            else:
                buf[o] = buf[o + 1] = buf[o + 2] = v
    open(out, 'wb').write(b'P6\n%d %d\n255\n' % (W, H) + bytes(buf))

main()
