"""sanity.py : the transcription's sonority on every beat, flagging what no chord explains (a misreading to check)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse
QUAL = {'maj': (0, 4, 7), 'min': (0, 3, 7), 'dim': (0, 3, 6), 'aug': (0, 4, 8), 'dom7': (0, 4, 7, 10), 'min7': (0, 3, 7, 10),
        'maj7': (0, 4, 7, 11), 'hdim7': (0, 3, 6, 10), 'dim7': (0, 3, 6, 9), 'sus4': (0, 5, 7), '7b9': (0, 4, 7, 10, 1), 'add6': (0, 4, 7, 9)}
N = ['C', 'Db', 'D', 'Eb', 'E', 'F', 'Gb', 'G', 'Ab', 'A', 'Bb', 'B']
P = parse.read()
def bar_of(beat):
    if beat < 1: return 13
    if beat < 73: return 14 + int((beat - 1) // 4)
    return 39 + int((beat - 73) // 4)
for beat in [x / 2 for x in range(0, 546)]:
    s = {}
    for v, notes in P.items():
        for n in notes:
            if n['beat'] <= beat < n['beat'] + n['length']:
                s[v] = n['pitch']
    if len(s) < 3:
        continue
    pcs = {p % 12 for p in s.values()}
    ok = any(pcs <= {(r + i) % 12 for i in iv} for r in range(12) for iv in QUAL.values())
    if not ok:
        print('bar %d beat %.1f (t%g): %s' % (bar_of(beat), (beat - 1) % 4 + 1, beat, ' '.join('%s=%s%d' % (v, N[s[v] % 12], s[v] // 12 - 1) for v in 'SATB' if v in s)))
