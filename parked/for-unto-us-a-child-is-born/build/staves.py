# Lists the staves on a page (in the 1400-tall frame) with how much text sits under each (lyrics).
import sys, subprocess, struct, os
img = sys.argv[1]
bmp = img + '.s.bmp'
subprocess.run(['sips', '-s', 'format', 'bmp', img, '--out', bmp], capture_output=True)
d = open(bmp, 'rb').read(); os.remove(bmp)
off = struct.unpack_from('<I', d, 10)[0]; W, H = struct.unpack_from('<ii', d, 18); bp = struct.unpack_from('<H', d, 28)[0] // 8
flip = H > 0; H = abs(H); row = (W * bp + 3) & ~3
def rowdark(y, x0, x1):
    base = off + ((H - 1 - y) if flip else y) * row
    r = d[base + x0 * bp:base + x1 * bp]
    return sum(1 for i in range(0, len(r), bp * 2) if r[i] + r[i + 1] + r[i + 2] < 380) / ((x1 - x0) / 2)
x0, x1 = int(W * 0.12), int(W * 0.30)
prof = [rowdark(y, x0, x1) for y in range(H)]
cand = [y for y in range(H) if prof[y] > 0.5 and prof[y] >= prof[y - 1] and prof[y] >= prof[min(H - 1, y + 1)]]
peaks = []
for y in cand:
    if peaks and y - peaks[-1] < 4:
        if prof[y] > prof[peaks[-1]]: peaks[-1] = y
    else: peaks.append(y)
i = 0; f = H / 1400
while i + 4 < len(peaks):
    g = peaks[i:i + 5]; dd = [g[k + 1] - g[k] for k in range(4)]
    if max(dd) - min(dd) <= 3:
        sp = (g[4] - g[0]) / 4
        text = sum(rowdark(y, int(W * 0.1), int(W * 0.9)) for y in range(int(g[4] + 1.3 * sp), int(g[4] + 3.3 * sp))) / (2 * sp)
        print(f'staff y {g[0] / f:.0f}-{g[4] / f:.0f}  text {text:.3f}')
        i += 5
    else: i += 1
