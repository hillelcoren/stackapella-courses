# Reads trans.txt (the transcription) into notes per part: (beat, length, midi, lyric or None).
# Bar 4 of the score is beat 0 here (bars 1 to 3 are the orchestra alone).
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
NAMES = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
FIRST_BAR = 4


def midi(name):
    m = re.fullmatch(r'([A-G])(#|b|n)?(\d)', name)
    if not m:
        raise ValueError(name)
    v = NAMES[m.group(1)] + 12 * (int(m.group(3)) + 1)
    if m.group(2) == '#':
        v += 1
    elif m.group(2) == 'b':
        v -= 1
    return v


def load(path=os.path.join(HERE, 'trans.txt')):
    parts = {p: [] for p in 'SATB'}
    pos = {p: 0.0 for p in 'SATB'}
    problems = []
    for line in open(path, encoding='utf-8'):
        line = line.rstrip('\n')
        if not line.strip() or line.startswith('#'):
            continue
        m = re.fullmatch(r'(\d+) ([SATB]):(.*)', line)
        if not m:
            problems.append(f'bad line: {line}')
            continue
        bar, part, rest = int(m.group(1)), m.group(2), m.group(3).strip()
        start = (bar - FIRST_BAR) * 4.0
        if not rest:
            if pos[part] <= start:
                problems.append(f'bar {bar} {part}: empty but nothing carries into it')
            continue
        if abs(pos[part] - start) > 1e-9:
            # a note held over from an earlier bar may end inside this one
            if pos[part] > start and pos[part] < start + 4:
                pass
            else:
                problems.append(f'bar {bar} {part}: starts at {pos[part] - (bar - FIRST_BAR) * 4} into the bar')
        for tok in rest.split():
            pm = re.fullmatch(r'([^/]+)/([\d.]+)(?::(.*))?', tok)
            if not pm:
                problems.append(f'bar {bar} {part}: bad token {tok}')
                continue
            name, length, lyric = pm.group(1), float(pm.group(2)), pm.group(3)
            if lyric is not None:
                lyric = lyric.replace('~', ' ')
            if name != 'r':
                parts[part].append((pos[part], length, midi(name), lyric))
            pos[part] += length
        end = (bar - FIRST_BAR + 1) * 4.0
        if pos[part] < end - 1e-9:
            problems.append(f'bar {bar} {part}: only {pos[part] - start} beats')
    return parts, problems


if __name__ == '__main__':
    parts, problems = load()
    for p in problems:
        print(p)
    for k, v in parts.items():
        print(k, len(v), 'notes, ends', max(b + l for b, l, _, _ in v), 'range', min(n for _, _, n, _ in v), max(n for _, _, n, _ in v))
