# Seconds out of each part's beginner range for every transposition (at the given tempo).
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parse import load

RANGES = {'S': (62, 76), 'A': (55, 72), 'T': (48, 67), 'B': (41, 58)}
tempo = float(sys.argv[1]) if len(sys.argv) > 1 else 72
parts, _ = load()
# Prout's small alternative D4 for the alto's D5 at bars 46 and 79 (beats 169, 300)
for shift in range(-7, 3):
    row = []
    total = 0
    for k, (lo, hi) in RANGES.items():
        out = sum(l for _, l, n, _ in parts[k] if not lo <= n + shift <= hi) * 60 / tempo
        notes = sum(1 for _, _, n, _ in parts[k] if not lo <= n + shift <= hi)
        lo_n = min(n for _, _, n, _ in parts[k]) + shift
        hi_n = max(n for _, _, n, _ in parts[k]) + shift
        row.append(f'{k} {lo_n}-{hi_n} out {notes} notes {out:.1f}s')
        total += out
    print(f'{shift:+d}: total {total:.1f}s | ' + ' | '.join(row))
