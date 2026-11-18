"""stafftops.py page.pgm x0 x1 : the staves found in one window (top line, spacing)."""
import sys
sys.argv += []
exec(open(sys.argv[0].replace('stafftops.py', 'heads.py')).read().split('def main():')[0])
w, h, px = load(sys.argv[1])
for g in lines_in(px, w, h, int(sys.argv[2]), int(sys.argv[3])):
    print('%.0f %.0f %.1f' % (g[0], g[4], (g[4] - g[0]) / 4))
