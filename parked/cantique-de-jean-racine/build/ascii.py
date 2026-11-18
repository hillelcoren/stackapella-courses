"""ascii.py page.pgm x0 x1 y0 y1 : print a region as characters by darkness (' .:-=+*#%@')."""
import sys
d = open(sys.argv[1], 'rb').read(); p = d.split(b'\n', 3); w, h = map(int, p[1].split()); px = p[3]
x0, x1, y0, y1 = map(int, sys.argv[2:6])
ramp = ' .:-=+*#%@'
print('      ' + ''.join(str((x // 10) % 10) if x % 10 == 0 else ' ' for x in range(x0, x1)))
for y in range(y0, y1):
    print('%5d ' % y + ''.join(ramp[min(9, (255 - px[y * w + x]) * 10 // 200)] for x in range(x0, x1)))
