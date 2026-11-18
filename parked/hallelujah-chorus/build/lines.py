# usage: python3 -I lines.py crop.png x0 x1
# Prints the y of each staff line (rows dark across x0..x1), grouped in staves of five.
import sys
sys.path.append('/Users/hillel/Library/Python/3.14/lib/python/site-packages')
from PIL import Image

im = Image.open(sys.argv[1]).convert('L')
x0, x1 = int(sys.argv[2]), int(sys.argv[3])
px = im.load()
hits = []
for y in range(im.height):
    dark = sum(1 for x in range(x0, x1) if px[x, y] < 128)
    if dark > 0.7 * (x1 - x0):
        hits.append(y)
lines = []
for y in hits:
    if lines and y - lines[-1][-1] <= 2:
        lines[-1].append(y)
    else:
        lines.append([y])
centres = [round(sum(l) / len(l)) for l in lines]
groups, cur = [], []
for c in centres:
    if cur and c - cur[-1] > 60:
        groups.append(cur)
        cur = []
    cur.append(c)
groups.append(cur)
for g in groups:
    print(g)
