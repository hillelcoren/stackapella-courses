# usage: python3 -I crop.py in.jpg out.jpg y0 y1 x0 x1 [scale]  (coords in the 1400-tall reduced frame)
import sys, subprocess
inp, out = sys.argv[1], sys.argv[2]
y0, y1, x0, x1 = map(float, sys.argv[3:7])
scale = float(sys.argv[7]) if len(sys.argv) > 7 else 1.0
info = subprocess.run(['sips', '-g', 'pixelWidth', '-g', 'pixelHeight', inp], capture_output=True, text=True).stdout.split()
W, H = int(info[-3]), int(info[-1])
f = H / 1400
h, w = int((y1 - y0) * f), int((x1 - x0) * f)
subprocess.run(['sips', '-c', str(h), str(w), '--cropOffset', str(int(y0 * f)), str(int(x0 * f)), inp, '--out', out], capture_output=True)
if scale != 1.0:
    subprocess.run(['sips', '-z', str(int(h * scale)), str(int(w * scale)), out], capture_output=True)
print(out, int(w * scale), int(h * scale))
