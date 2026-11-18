# usage: python3 -I heads.py crop.png lx0 lx1 clefs [sharps]
# Finds filled noteheads on each staff of a vocal system crop and names their pitch.
# lx0..lx1: an x range where the staff lines are clear (to find them).
# clefs: one letter a staff, top to bottom: t treble, 8 treble an octave down (tenor), b bass.
# sharps: the key's sharps as letters (default "FC", D major).
import sys
sys.path.append('/Users/hillel/Library/Python/3.14/lib/python/site-packages')
from PIL import Image

path, lx0, lx1, clefs = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
sharps = sys.argv[5] if len(sys.argv) > 5 else 'FC'
im = Image.open(path).convert('L')
W, H = im.size
px = im.load()
dark = [[px[x, y] < 140 for x in range(W)] for y in range(H)]

# staff lines
hits = [y for y in range(H) if sum(dark[y][lx0:lx1]) > 0.7 * (lx1 - lx0)]
lines = []
for y in hits:
    if lines and y - lines[-1][-1] <= 2:
        lines[-1].append(y)
    else:
        lines.append([y])
centres = [sum(l) / len(l) for l in lines]
# remove staff lines: keep a line pixel only where something crosses it
for l in lines:
    a, b = l[0], l[-1]
    if a - 2 < 0 or b + 2 >= H:
        continue
    for x in range(W):
        if not (dark[a - 2][x] and dark[b + 2][x]):
            for y in range(a, b + 1):
                dark[y][x] = False
        else:
            for y in range(a, b + 1):
                dark[y][x] = True
groups, cur = [], []
for c in centres:
    if cur and c - cur[-1] > 60:
        groups.append(cur)
        cur = []
    cur.append(c)
groups.append(cur)
staves = []
for g in groups:
    if len(g) < 3:
        continue
    gaps = sorted(g[i + 1] - g[i] for i in range(len(g) - 1))
    s = gaps[0] if gaps[0] > 15 else gaps[len(gaps) // 2]
    # rebuild five lines from the top and the spacing (fill a missed line)
    top = g[0]
    five = [top + i * s for i in range(5)]
    if abs(five[4] - g[-1]) > s / 2:
        # first detected line may not be the top: anchor on the bottom
        bottom = g[-1]
        five = [bottom - (4 - i) * s for i in range(5)]
    staves.append((five, s))

if len(staves) != len(clefs):
    print('staves found', len(staves), [round(f[0][0]) for f in staves])

# vertical and horizontal dark run lengths
vrun = [[0] * W for _ in range(H)]
for x in range(W):
    y = 0
    while y < H:
        if dark[y][x]:
            y2 = y
            while y2 < H and dark[y2][x]:
                y2 += 1
            for k in range(y, y2):
                vrun[k][x] = y2 - y
            y = y2
        else:
            y += 1
hrun = [[0] * W for _ in range(H)]
for y in range(H):
    row = dark[y]
    x = 0
    while x < W:
        if row[x]:
            x2 = x
            while x2 < W and row[x2]:
                x2 += 1
            for k in range(x, x2):
                hrun[y][k] = x2 - x
            x = x2
        else:
            x += 1

NAMES = 'CDEFGAB'
BASE = {'t': (2, 4), '8': (2, 3), 'b': (4, 2)}  # bottom line: E4 (index 2), E3 sung; G2 for bass


def name(step, clef):
    idx, octv = BASE[clef]
    n = idx + step
    octv += n // 7
    letter = NAMES[n % 7]
    acc = '#' if letter in sharps else ''
    return f'{letter}{acc}{octv}'


for si, (five, s) in enumerate(staves):
    clef = clefs[si] if si < len(clefs) else 't'
    ylo, yhi = int(five[0] - 3.2 * s), int(five[4] + 3.2 * s)
    ylo, yhi = max(ylo, 0), min(yhi, H - 1)
    mask = set()
    for y in range(ylo, yhi):
        for x in range(W):
            if dark[y][x] and vrun[y][x] >= 0.62 * s and vrun[y][x] <= 1.6 * s and 0.8 * s <= hrun[y][x] <= 2.4 * s:
                mask.add((x, y))
    # blobs
    seen = set()
    blobs = []
    for p in mask:
        if p in seen:
            continue
        stack = [p]
        seen.add(p)
        pts = []
        while stack:
            q = stack.pop()
            pts.append(q)
            for d in ((1, 0), (-1, 0), (0, 1), (0, -1), (0, 2), (0, -2), (0, 3), (0, -3), (0, 4), (0, -4)):
                r = (q[0] + d[0], q[1] + d[1])
                if r in mask and r not in seen:
                    seen.add(r)
                    stack.append(r)
        if len(pts) < 0.25 * s * s:
            continue
        xs = [a for a, _ in pts]
        ys = [b for _, b in pts]
        bw, bh = max(xs) - min(xs), max(ys) - min(ys)
        if bh < 0.45 * s or bw < 0.7 * s:
            continue
        blobs.append((sum(xs) / len(xs), sum(ys) / len(ys), bw, bh))
    blobs.sort()
    out = []
    for bx, by, bw, bh in blobs:
        step = round((five[4] - by) / (s / 2))
        out.append(f'{round(bx)}:{name(step, clef)}')
    print(f'staff {si + 1} ({clef}) lines {[round(v) for v in five]}:', ' '.join(out))
