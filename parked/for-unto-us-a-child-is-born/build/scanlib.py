# Shared by heads.py and measure.py: load a crop as a binary image and straighten its slight tilt
# (the shear that makes the staff lines' row profile sharpest).
import subprocess, struct, os
def load(img):
    bmp = img + '.tmp.bmp'
    subprocess.run(['sips', '-s', 'format', 'bmp', img, '--out', bmp], capture_output=True)
    d = open(bmp, 'rb').read(); os.remove(bmp)
    off = struct.unpack_from('<I', d, 10)[0]; W, H = struct.unpack_from('<ii', d, 18); bp = struct.unpack_from('<H', d, 28)[0] // 8
    flip = H > 0; H = abs(H); row = (W * bp + 3) & ~3
    D = []
    for y in range(H):
        base = off + ((H - 1 - y) if flip else y) * row
        r = d[base:base + W * bp]
        D.append(bytes(1 if r[i] + r[i + 1] + r[i + 2] < 380 else 0 for i in range(0, W * bp, bp)))
    best = (None, 0.0)
    for k in range(-40, 41):
        t = k / 4000  # up to 1 % slope
        prof = [0] * H
        for x in range(0, W, 4):
            s = round(t * x)
            for y in range(max(0, -s), min(H, H - s)):
                if D[y + s][x]: prof[y] += 1
        score = sum(p * p for p in prof)
        if best[0] is None or score > best[0]: best = (score, t)
    t = best[1]
    if t:
        S = []
        for y in range(H):
            S.append(bytes(D[y + round(t * x)][x] if 0 <= y + round(t * x) < H else 0 for x in range(W)))
        D = S
    return W, H, D, t
