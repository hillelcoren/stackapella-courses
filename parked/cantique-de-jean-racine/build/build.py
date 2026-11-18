"""build.py : write templates/library/cantique-de-jean-racine.json from transcription.txt (the Schoen print's choir
parts as read), breaths.py and meta.json. Run from anywhere: python3 -I build.py"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import parse, breaths

TEMPO = 60
END = 272  # the last chord is held three beats (the print ties two bars under a fermata); the song ends a pickup short of a bar line
KEYS = {'S': 'soprano', 'A': 'alto', 'T': 'tenor', 'B': 'bass'}
NAMES = {'S': 'Soprano', 'A': 'Alto', 'T': 'Tenor', 'B': 'Bass'}
EPS = 1e-9

def downbeat(beat):
    return abs((beat - 1) % 4) < EPS

def make_breaths(v, notes, log):
    brs = breaths.BR[v]
    idx = {}
    for i, n in enumerate(notes):
        idx[round(n['beat'], 6)] = i
    starts = []
    for b in brs:
        if round(b, 6) not in idx:
            raise ValueError('%s: no note at breath beat %s' % (v, b))
        starts.append(idx[round(b, 6)])
    for k, i in enumerate(starts):
        n = notes[i]
        n['br'] = True
        if k == 0:
            continue
        p = notes[i - 1]
        line_start = notes[starts[k - 1]]['beat']
        d = breaths.DELAY.get((v, brs[k]), 0)
        if d:
            n['beat'] = round(n['beat'] + d, 6)
            n['length'] = round(n['length'] - d, 6)
            log.append('%s: "%s" starts %g beat later, at %g (now %g beats), with the other parts' % (v, n.get('lyric', '~'), d, n['beat'], n['length']))
        gap = n['beat'] - (p['beat'] + p['length'])
        # the gap this line needs depends on the line's length once it is shortened: try half a beat first
        for need in (0.5, 1.0):
            give = max(0.0, need - gap)
            line_len = p['beat'] + p['length'] - give - line_start
            if line_len < 8 - EPS or need == 1.0:
                break
        if gap >= need - EPS:
            continue
        give = need - gap
        take = min(give, p['length'] - 0.5)
        if take > EPS:
            p['length'] = round(p['length'] - take, 6)
            log.append('%s %g: "%s" before the breath %g -> %g beats' % (v, p['beat'], p.get('lyric', '~'), p['length'] + take, p['length']))
        rest = give - max(take, 0)
        if rest > EPS:
            if downbeat(n['beat']):
                raise ValueError('%s %g: no room for a breath before a downbeat' % (v, n['beat']))
            n['beat'] = round(n['beat'] + rest, 6)
            n['length'] = round(n['length'] - rest, 6)
            log.append('%s: "%s" starts %g beat later, at %g (now %g beats)' % (v, n.get('lyric', '~'), rest, n['beat'], n['length']))

def main():
    meta = json.load(open(os.path.join(HERE, 'meta.json'), encoding='utf-8'))
    P = parse.read()
    log = []
    parts = []
    for v in 'SATB':
        notes = P[v]
        # the last chord: one bar
        last = notes[-1]
        if last['beat'] + last['length'] > END:
            log.append('%s: last note %g -> %g beats' % (v, last['length'], END - last['beat']))
            last['length'] = END - last['beat']
        make_breaths(v, notes, log)
        out = []
        for n in notes:
            o = {'beat': round(n['beat'], 6), 'length': round(n['length'], 6), 'pitch': n['pitch']}
            if 'lyric' in n:
                o['lyric'] = n['lyric']
            if n.get('br'):
                o['br'] = True
            out.append(o)
        pitches = [n['pitch'] for n in out]
        part = {'key': KEYS[v], 'name': NAMES[v], 'range': {'low': min(pitches), 'high': max(pitches)}}
        if v == 'S':
            part['melody'] = True
        part['guide'] = {'type': 'notes', 'notes': out}
        parts.append(part)
    t = dict(meta['head'])
    t['tempo'] = TEMPO
    t['sections'] = meta['sections']
    t['chords'] = chords(parts)
    t['parts'] = parts
    path = os.path.join(HERE, '..', '..', '..', 'templates', 'library', 'cantique-de-jean-racine.json')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(json.dumps(t, indent=1, ensure_ascii=False) + '\n')
    for l in log:
        print(l)
    print('wrote', os.path.normpath(path))

QUAL = {'maj': (0, 4, 7), 'min': (0, 3, 7), 'dim': (0, 3, 6), 'aug': (0, 4, 8), 'sus4': (0, 5, 7),
        'dom7': (0, 4, 7, 10), 'min7': (0, 3, 7, 10), 'maj7': (0, 4, 7, 11), 'hdim7': (0, 3, 6, 10), 'dim7': (0, 3, 6, 9)}
# D-flat major's own triad on each degree, for a beat where one part sings alone (the organ's harmony there)
DIATONIC = {1: 'maj', 3: 'min', 5: 'min', 6: 'maj', 8: 'maj', 10: 'min', 0: 'dim'}
# Where only the bass sings, the chord the organ plays, read from the print (bars 13 to 15, 59 to 61)
CHORD_AT = {
    0: (1, 'maj', 5), 1: (8, 'dom7', 6), 5: (1, 'maj', 5), 7: (1, 'maj7', 0),
    156: (5, 'maj', None), 157: (1, 'maj', 5), 159: (6, 'maj7', 5), 161: (1, 'maj', 5),
    246: (1, 'add9', 8),  # bar 82: D-flat with the soprano's E-flat over the bass's A-flat
}

def name_chord(pcs, bass):
    best = None
    for r in range(12):
        for q, iv in QUAL.items():
            Q = {(r + i) % 12 for i in iv}
            for pedal in (False, True):
                P = (pcs - {bass}) if pedal else pcs
                if pedal and bass in Q:
                    continue
                miss = len(P - Q)
                unused = len(Q - P)
                cost = 10 * miss + len(Q) + unused * 0.6 + (0 if (r == bass or pedal) else 0.4) + (0.3 if q in ('aug', 'sus4', 'dim') else 0) + (1.5 if pedal else 0)
                if best is None or cost < best[0]:
                    best = (cost, r, q)
    return best[1], best[2]

def chords(parts):
    """The harmony on each beat as the four parts sound it (passing notes between beats left out); where one part sings
    alone, the organ's chord (CHORD_AT) or the key's own triad on the sung note."""
    out = []
    for beat in range(0, END):
        sounding = []
        for p in parts:
            for n in p['guide']['notes']:
                if n['beat'] <= beat + EPS and beat < n['beat'] + n['length'] - EPS:
                    sounding.append(n['pitch'])
        pcs = {x % 12 for x in sounding}
        if beat in CHORD_AT:
            r, q, b = CHORD_AT[beat]
        elif not sounding:
            continue
        elif len(pcs) == 1:
            r = sounding[0] % 12
            q, b = DIATONIC.get(r, 'maj'), None
        else:
            bass = min(sounding) % 12
            r, q = name_chord(pcs, bass)
            b = None if bass == r else bass
        c = {'beat': float(beat), 'root': r, 'quality': q, 'bass': b}
        if out and (out[-1]['root'], out[-1]['quality'], out[-1]['bass']) == (r, q, b):
            continue
        out.append(c)
    return out

main()
