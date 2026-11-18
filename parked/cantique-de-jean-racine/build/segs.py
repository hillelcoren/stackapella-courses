"""segs.py [tempo] : each part's lines as the words' punctuation and the rests divide them (for placing breaths)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import parse
P = parse.read()
T = float(sys.argv[1]) if len(sys.argv) > 1 else 72
for v, notes in P.items():
    print('==', v)
    starts, prev = [], None
    for i, n in enumerate(notes):
        gap = n['beat'] - (prev['beat'] + prev['length']) if prev else 99
        punct = prev is not None and prev.get('lyric', '') and prev['lyric'][-1] in ',!.;:'
        if gap > 1e-9 or punct:
            starts.append(i)
        prev = n
    starts.append(len(notes))
    for a, b in zip(starts, starts[1:]):
        seg = notes[a:b]
        s, e = seg[0]['beat'], seg[-1]['beat'] + seg[-1]['length']
        gapafter = notes[b]['beat'] - e if b < len(notes) else 0
        print('  %6.2f-%6.2f %5.1fb %4.1fs last %.2f gap %.2f | %s' % (s, e, e - s, (e - s) * 60 / T, seg[-1]['length'], gapafter, ' '.join('%s@%g' % (n.get('lyric', '~'), n['beat']) for n in seg)))
