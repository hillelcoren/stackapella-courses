"""Read transcription.txt (the choir parts as read from the Schoen print) into notes on the template's beat line.
Beat 0 is bar 13's last beat (the bass's 'Ver-'): pickupBeats 1. The organ's bars 32 to 38 are left out, so
bar 39 follows bar 31 straight on. Pitches are MIDI numbers, sounding (the tenor as sung)."""
import os, re

HERE = os.path.dirname(os.path.abspath(__file__))
LETTER = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}
KEY_FLATS = set('BEADG')  # D-flat major

def midi(name):
    m = re.fullmatch(r'([A-G])(b?)(\d)(n?)', name)
    if not m or (m.group(2) and m.group(4)):
        raise ValueError('bad pitch ' + name)
    letter, octave = m.group(1), int(m.group(3))
    acc = 'b' if m.group(2) else 'n' if m.group(4) else None
    if acc is None and letter in KEY_FLATS:
        raise ValueError('pitch %s: say b or n (the key has its flat)' % name)
    return 12 * (octave + 1) + LETTER[letter] + (-1 if acc == 'b' else 0)

def bar_start(b):
    if b == 13:
        return -3
    if 14 <= b <= 31:
        return 1 + (b - 14) * 4
    if 32 <= b <= 38:
        return None  # the organ's bars, left out
    return 73 + (b - 39) * 4

def read():
    parts = {v: [] for v in 'SATB'}
    for line in open(os.path.join(HERE, 'transcription.txt'), encoding='utf-8'):
        line = line.split('#')[0].strip()
        if not line:
            continue
        head, toks = line.split(':', 1)
        bar, voices = head.split()
        bar = int(bar)
        start = bar_start(bar)
        if start is None:
            continue
        for v in voices:
            t = start
            for tok in toks.split():
                bits = tok.split(':')
                if bits[0] == 'r':
                    t += float(bits[1]); continue
                pitch, length, lyric = bits[0], float(bits[1]), ':'.join(bits[2:])
                note = {'beat': t, 'length': length, 'pitch': midi(pitch), 'bar': bar}
                if lyric and lyric != '_':
                    note['lyric'] = lyric.replace('_', ' ')
                if t >= 0:
                    parts[v].append(note)
                t += length
            want = 8 if bar == 88 else 4
            if abs(t - start - want) > 1e-9 and bar != 13:
                raise ValueError('bar %d %s: %s beats' % (bar, v, t - start))
    for v in parts:
        parts[v].sort(key=lambda n: n['beat'])
        for a, b in zip(parts[v], parts[v][1:]):
            if b['beat'] < a['beat'] + a['length'] - 1e-9:
                raise ValueError('overlap %s bar %d' % (v, a['bar']))
    return parts

if __name__ == '__main__':
    import sys
    P = read()
    tempo = float(sys.argv[1]) if len(sys.argv) > 1 else 66
    for v, notes in P.items():
        print('==', v, len(notes), 'notes, range', min(n['pitch'] for n in notes), max(n['pitch'] for n in notes))
        line, start = [], None
        prev_end = None
        for n in notes:
            if prev_end is not None and n['beat'] - prev_end > 1e-9:
                print('  [%6.2f-%6.2f %4.1fs] %s' % (start, prev_end, (prev_end - start) * 60 / tempo, ' '.join(line)))
                line, start = [], None
            if start is None:
                start = n['beat']
            line.append('%s%s' % (n.get('lyric', '~'), '' ))
            prev_end = n['beat'] + n['length']
        print('  [%6.2f-%6.2f %4.1fs] %s' % (start, prev_end, (prev_end - start) * 60 / tempo, ' '.join(line)))
