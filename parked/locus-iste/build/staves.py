"""Staff lines and note heads on a page scan (24-bit BMP from sips), pure Python.

python3 -I staves.py page.bmp  -> prints each staff's five line rows and the
heads found (x, y, step from the bottom line, filled or hollow), so a reading by
eye can be checked against measured positions.
"""
import struct
import sys


def load(path):
    b = open(path, 'rb').read()
    off = struct.unpack_from('<I', b, 10)[0]
    w, h = struct.unpack_from('<ii', b, 18)
    top_down = h < 0
    h = abs(h)
    row = (w * 3 + 3) & ~3
    g = []
    for y in range(h):
        yy = y if top_down else h - 1 - y
        r = b[off + yy * row: off + yy * row + w * 3]
        g.append(bytes((r[i] + r[i + 1] + r[i + 2]) // 3 for i in range(0, w * 3, 3)))
    return w, h, g


def staff_lines(w, h, g, x0, x1, thr=150, frac=0.4):
    rows = []
    for y in range(h):
        r = g[y]
        d = sum(1 for x in range(x0, x1) if r[x] < thr)
        if d > frac * (x1 - x0):
            rows.append(y)
    # merge adjacent rows
    lines = []
    for y in rows:
        if lines and y - lines[-1][-1] <= 1:
            lines[-1].append(y)
        else:
            lines.append([y])
    centres = [sum(l) / len(l) for l in lines]
    staves = []
    i = 0
    while i + 4 < len(centres):
        five = centres[i:i + 5]
        gaps = [five[k + 1] - five[k] for k in range(4)]
        if max(gaps) - min(gaps) < 2.5 and 5 < gaps[0] < 20:
            staves.append(five)
            i += 5
        else:
            i += 1
    return staves


def main():
    path = sys.argv[1]
    x0 = int(sys.argv[2]) if len(sys.argv) > 2 else 200
    x1 = int(sys.argv[3]) if len(sys.argv) > 3 else 900
    w, h, g = load(path)
    for s in staff_lines(w, h, g, x0, x1):
        print(' '.join('%.1f' % y for y in s), ' gap %.2f' % ((s[4] - s[0]) / 4))


if __name__ == '__main__':
    main()
