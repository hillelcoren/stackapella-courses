"""Reads trans.txt (the voice parts as read from Prout's 1902 full score) into bars of notes.
read() -> {voice: {bar: [(midi or None, beats, lyric or None, tie)]}} for bars 1..138, rests filled in."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
BARS = 138
VOICES = 'SATB'
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def midi(p):
    m = re.fullmatch(r'([A-G])(#|b|n)?(\d)', p)
    if not m:
        raise ValueError(p)
    v = NAMES[m.group(1)] + {'#': 1, 'b': -1, 'n': 0, None: 0}[m.group(2)]
    return 12 * (int(m.group(3)) + 1) + v


def read(path=os.path.join(HERE, 'trans.txt')):
    out = {v: {} for v in VOICES}
    for ln, line in enumerate(open(path, encoding='utf-8'), 1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        m = re.fullmatch(r'([SATB]) (\d+): (.*)', line)
        if not m:
            raise ValueError(f'line {ln}: {line}')
        v, bar = m.group(1), int(m.group(2))
        if bar in out[v]:
            raise ValueError(f'line {ln}: {v} bar {bar} given twice')
        notes = []
        for tok in m.group(3).split('|'):
            parts = tok.split()
            tie = parts[-1] == '~'
            if tie:
                parts = parts[:-1]
            p, d = parts[0], float(parts[1])
            lyr = ' '.join(parts[2:]).replace('~', ' ') or None
            notes.append((None if p == 'r' else midi(p), d, lyr, tie))
        if abs(sum(n[1] for n in notes) - 3) > 1e-9:
            raise ValueError(f'line {ln}: {v} bar {bar} sums to {sum(n[1] for n in notes)}')
        out[v][bar] = notes
    for v in VOICES:
        for b in range(1, BARS + 1):
            out[v].setdefault(b, [(None, 3.0, None, False)])
    return out


if __name__ == '__main__':
    d = read()
    for v in VOICES:
        ps = [n[0] for b in d[v] for n in d[v][b] if n[0] is not None]
        print(v, 'notes', len(ps), 'range', min(ps), max(ps))
    allrest = [b for b in range(1, BARS + 1) if all(all(n[0] is None for n in d[v][b]) for v in VOICES)]
    print('bars where every voice rests:', allrest)
