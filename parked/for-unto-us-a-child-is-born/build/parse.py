"""Reads notes.txt (the bar-by-bar reading of Prout's 1902 edition) into four parts of notes.
Bars 7 to 91 are sung (1 to 6 are the orchestra's introduction, 92 on its ending); beat 0 is bar 7's downbeat."""
import re
from pathlib import Path

FIRST, LAST = 7, 91
PC = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEYS = {'S': 'soprano', 'A': 'alto', 'T': 'tenor', 'B': 'bass'}


def midi(name):
    m = re.fullmatch(r'([A-G])([#b]?)(\d)', name)
    return 12 * (int(m[3]) + 1) + PC[m[1]] + {'#': 1, 'b': -1, '': 0}[m[2]]


def read(path=Path(__file__).with_name('notes.txt')):
    bars = {k: {} for k in KEYS.values()}
    for line in path.read_text().splitlines():
        line = line.split('??')[0].strip()
        if not line or line.startswith('#'):
            continue
        head, body = line.split(':', 1)
        m = re.fullmatch(r'([SATB])(\d+)(?:-(\d+))?', head.strip())
        part, a, b = KEYS[m[1]], int(m[2]), int(m[3] or m[2])
        tokens = body.split()
        if b > a:  # a run of whole-bar rests
            assert tokens == [f'r:{4 * (b - a + 1)}'], line
            for bar in range(a, b + 1):
                assert bar not in bars[part], (part, bar)
                bars[part][bar] = [('r', 4.0, None, False)]
            continue
        assert a not in bars[part], (part, a)
        notes = []
        for t in tokens:
            bits = t.split(':', 2)
            tie = bits[1].endswith('~')
            length = float(bits[1].rstrip('~'))
            lyric = bits[2] if len(bits) > 2 else None
            notes.append((bits[0], length, lyric, tie))
        total = sum(n[1] for n in notes)
        assert abs(total - 4) < 1e-9, f'{part} bar {a} has {total} beats'
        bars[part][a] = notes
    parts = {}
    for part, got in bars.items():
        missing = [b for b in range(FIRST, LAST + 1) if b not in got]
        assert not missing, (part, missing)
        out, beat, tie = [], 0.0, False
        for bar in range(FIRST, LAST + 1):
            for name, length, lyric, tied in got[bar]:
                if name != 'r':
                    pitch = midi(name)
                    if tie:
                        assert out[-1]['pitch'] == pitch and lyric is None
                        out[-1]['length'] += length
                    else:
                        n = {'beat': beat, 'length': length, 'pitch': pitch, 'bar': bar}
                        if lyric:
                            n['lyric'] = lyric
                        out.append(n)
                    tie = tied
                beat += length
        parts[part] = out
    return parts


if __name__ == '__main__':
    ps = read()
    for k, ns in ps.items():
        print(k, len(ns), 'notes', min(n['pitch'] for n in ns), max(n['pitch'] for n in ns))
