# usage: python3 -I staves.py page.jpg [...]
# Finds staff lines (rows mostly dark across the page) and groups them into staves of five.
import sys
sys.path.append('/Users/hillel/Library/Python/3.14/lib/python/site-packages')
from PIL import Image

for path in sys.argv[1:]:
    im = Image.open(path).convert('L')
    w, h = im.size
    px = im.load()
    x0, x1 = int(w * 0.12), int(w * 0.95)
    rows = []
    for y in range(h):
        dark = sum(1 for x in range(x0, x1, 3) if px[x, y] < 110)
        rows.append(dark / ((x1 - x0) / 3))
    lines = []
    y = 0
    while y < h:
        if rows[y] > 0.5:
            y2 = y
            while y2 + 1 < h and rows[y2 + 1] > 0.5:
                y2 += 1
            lines.append((y + y2) / 2)
            y = y2 + 1
        else:
            y += 1
    staves = []
    cur = []
    for ln in lines:
        if cur and ln - cur[-1] > 40:
            staves.append(cur)
            cur = []
        cur.append(ln)
    if cur:
        staves.append(cur)
    print(path, [(round(s[0]), round(s[-1]), len(s)) for s in staves])
