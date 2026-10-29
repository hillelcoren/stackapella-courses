"""An original canon at the octave, a bar behind: 4 bars of quarters in major, the follower singing
the leader's line one bar later and an octave lower. Each beat with both voices sounding must be
consonant on strong beats (1 and 3), consonant or a passing step on weak ones; no parallel fifths or
octaves between beats; a singable line (steps, small leaps); learner range -5..+5; starts and ends on do."""
import random
SCALE = [-5, -3, -1, 0, 2, 4, 5]  # so, la, ti, do, re, mi, fa (+ later so, la)
SCALE = [-8, -7, -5, -3, -1, 0, 2, 4, 5]
CONS = {0, 3, 4, 7, 8, 9}
def ok(line):
    n = len(line)
    for t in range(4, n):
        up, low = line[t], line[t - 4] - 12
        iv = (up - low) % 12
        strong = t % 2 == 0
        if strong and iv not in CONS: return False
        if not strong and iv not in CONS:
            # a weak-beat dissonance must be a passing step in the leader
            if t + 1 >= n: return False
            a, b, c = line[t - 1], line[t], line[t + 1] if t + 1 < n else None
            if c is None or not (0 < abs(b - a) <= 2 and 0 < abs(c - b) <= 2 and (b - a) * (c - b) > 0): return False
        if t > 4:
            pu, pl = line[t - 1], line[t - 5] - 12
            piv = (pu - pl) % 12
            if iv == piv and iv in (0, 7) and (up - pu) * (low - pl) > 0: return False
    return True
random.seed(7)
best = []
for _ in range(400000):
    line = [0]
    while len(line) < 16:
        moves = [s for s in SCALE if abs(s - line[-1]) <= 4 and s != line[-1] or (s == line[-1] and random.random() < 0.15)]
        line.append(random.choice(moves))
    if line[-1] != 0 or line[-2] not in (-1, 2): continue
    if max(line) > 5 or min(line) < -8: continue
    leaps = sum(abs(line[i] - line[i - 1]) > 2 for i in range(1, 16))
    if leaps > 4: continue
    if ok(line + [None] * 0):
        best.append((leaps, line))
best.sort()
seen = set()
for leaps, line in best[:12]:
    if tuple(line) in seen: continue
    seen.add(tuple(line)); print(leaps, line)
