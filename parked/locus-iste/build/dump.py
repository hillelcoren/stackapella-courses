"""ASCII dump of a page region (2 columns per character): # dark, + mid, . light."""
import sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
import staves
p, y0, y1, x0, x1 = sys.argv[1], *map(int, sys.argv[2:6])
_, _, g = staves.load(p)
print('     ' + ''.join(str((x // 10) % 10) if x % 10 == 0 else ' ' for x in range(x0, x1, 2)))
for y in range(y0, y1):
    print(y, ''.join('#' if g[y][x] < 100 else ('+' if g[y][x] < 150 else ('.' if g[y][x] < 190 else ' ')) for x in range(x0, x1, 2)))
