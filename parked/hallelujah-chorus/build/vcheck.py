# Flags onsets where the sounding notes don't make a triad or a seventh chord (likely misreadings,
# or passing notes to look at against the scan). Prints score bar and beat.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse import load, FIRST_BAR

parts, problems = load()
for p in problems:
    print('PROBLEM', p)

onsets = sorted({b for v in parts.values() for b, _, _, _ in v})
SHAPES = []
for root in range(12):
    for ints in ((0, 4, 7), (0, 3, 7), (0, 3, 6), (0, 4, 7, 10), (0, 3, 7, 10), (0, 4, 7, 11), (0, 3, 6, 9), (0, 3, 6, 10)):
        SHAPES.append({(root + i) % 12 for i in ints})
NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
strong_only = '--all' not in sys.argv
for t in onsets:
    if strong_only and abs(t - round(t)) > 1e-9:
        continue
    sounding = {}
    for k, v in parts.items():
        for b, l, n, _ in v:
            if b <= t < b + l:
                sounding[k] = n
    pcs = {n % 12 for n in sounding.values()}
    if len(pcs) >= 2 and not any(pcs <= s for s in SHAPES):
        bar = int(t // 4) + FIRST_BAR
        beat = t - (bar - FIRST_BAR) * 4
        print(f'bar {bar} beat {beat + 1:g}:', ' '.join(f'{k}={NAMES[n % 12]}{n // 12 - 1}' for k, n in sounding.items()))
