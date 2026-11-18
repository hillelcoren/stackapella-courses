"""look.py page.pgm top x [x ...] : a small picture in characters of the note at each x
(columns x-6..x+6, rows from 2.2 spaces over the staff's top line to 2.2 under its bottom one).
A '<' after a row: the columns beside the note are dark there, so the row is a staff (or ledger) line."""
import sys
d = open(sys.argv[1], 'rb').read(); p = d.split(b'\n', 3); w, h = map(int, p[1].split()); px = p[3]
D = lambda x, y: 255 - px[y * w + x]
top = int(sys.argv[2])
xs = [int(a) for a in sys.argv[3:]]
rows = range(top - 10, top + 30)
blocks = []
for x in xs:
    side = list(range(x - 18, x - 8)) + list(range(x + 9, x + 19))
    col = []
    for y in rows:
        v = sorted(D(c, y) for c in side)
        med = v[len(v) // 2]
        col.append(''.join(' .:-=+*#%@'[min(9, D(c, y) * 10 // 200)] for c in range(x - 6, x + 7)) + ('<' if med > 75 else ' '))
    blocks.append(col)
print('      ' + '  '.join('x%-13d' % x for x in xs))
for i, y in enumerate(rows):
    print('%4d  ' % y + '  '.join(b[i] for b in blocks))
