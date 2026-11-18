"""voicecrops.py : one crop per voice staff and half system (scale 4), named p<page>s<system><voice><half>."""
import subprocess
B = '/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine/parked/cantique-de-jean-racine/build'
S = '/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine-scans/bnf'
obj = {3: 28, 4: 30, 5: 32, 6: 34, 7: 36, 8: 38, 9: 40}
extra = {9: {2: [(502, 522, 4.9), (556, 576, 4.9), (610, 630, 4.9), (664, 683, 4.8)]}}
for p in range(3, 10):
    out = subprocess.run(['python3', '-I', B + '/stafftops.py', S + '/pgm/p%d.pgm' % p, '420', '560'], capture_output=True, text=True).stdout.split('\n')
    st = [tuple(map(float, l.split())) for l in out if l.strip()]
    systems, cur = [], []
    for s in st:
        if s[2] < 5.6:
            cur.append(s)
        elif cur:
            systems.append(cur); cur = []
    if cur:
        systems.append(cur)
    x0, x1 = (60, 905) if p % 2 else (140, 945)
    mid = (x0 + x1) // 2
    for k, sy in enumerate(systems):
        sy = extra.get(p, {}).get(k + 1, sy)
        if len(sy) != 4:
            print('page', p, 'system', k + 1, 'has', len(sy), 'staves'); continue
        for v, s in zip('SATB', sy):
            y0 = int(s[0] - 3 * s[2]); y1 = int(s[1] + 7 * s[2])
            for hname, a, b in (('1', x0, mid + 15), ('2', mid - 15, x1)):
                name = 'p%ds%d%s%s' % (p, k + 1, v, hname)
                subprocess.run([B + '/crop.sh', S + '/img/obj%d.jpg' % obj[p], S + '/voices/%s.png' % name, str(y0), str(a), str(y1 - y0), str(b - a), '4'])
