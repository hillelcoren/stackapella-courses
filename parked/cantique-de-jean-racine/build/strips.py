"""strips.py : print crop commands for every vocal system: two strips (S+A, T+B) per system."""
import subprocess, sys
B = '/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine/parked/cantique-de-jean-racine/build'
S = '/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine-scans/bnf'
obj = {3: 28, 4: 30, 5: 32, 6: 34, 7: 36, 8: 38, 9: 40}
for p in range(3, 10):
    out = subprocess.run(['python3', '-I', B + '/stafftops.py', S + '/pgm/p%d.pgm' % p, '420', '560'], capture_output=True, text=True).stdout.split('\n')
    st = [tuple(map(float, l.split())) for l in out if l.strip()]
    voc = [s for s in st if s[2] < 5.6]
    # systems: runs of vocal staves separated by piano staves
    systems, cur = [], []
    for s in st:
        if s[2] < 5.6:
            cur.append(s)
        elif cur:
            systems.append(cur); cur = []
    if cur:
        systems.append(cur)
    x0, x1 = (60, 905) if p % 2 else (140, 945)
    for k, sy in enumerate(systems):
        for j in range(0, len(sy), 2):
            pair = sy[j:j + 2]
            y0 = int(pair[0][0] - 16); y1 = int(pair[-1][1] + 28)
            name = 'p%ds%d%s' % (p, k + 1, 'ab'[j // 2] if len(sy) == 4 else chr(ord('a') + j // 2))
            print(name, len(sy), y0, y1)
            subprocess.run([B + '/crop.sh', S + '/img/obj%d.jpg' % obj[p], S + '/strips/%s.png' % name, str(y0), str(x0), str(y1 - y0), str(x1 - x0), '3'])
