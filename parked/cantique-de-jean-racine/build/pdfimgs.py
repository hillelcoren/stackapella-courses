# Extract the embedded page images (DCT/JPX/Flate) from a scanned PDF, no libraries.
import re, sys, zlib, os
src, out = sys.argv[1], sys.argv[2]
data = open(src, 'rb').read()
os.makedirs(out, exist_ok=True)
n = 0
for m in re.finditer(rb'(\d+) 0 obj\s*<<(.*?)>>\s*stream\r?\n', data, re.S):
    d = m.group(2)
    if b'/Image' not in d:
        continue
    L = re.search(rb'/Length (\d+)( 0 R)?', d)
    start = m.end()
    if L and not L.group(2):
        ln = int(L.group(1))
    else:
        ln = data.index(b'endstream', start) - start
    s = data[start:start+ln]
    w = re.search(rb'/Width (\d+)', d); h = re.search(rb'/Height (\d+)', d)
    filt = re.search(rb'/Filter\s*/(\w+)', d) or re.search(rb'/Filter\s*\[\s*/(\w+)', d)
    f = filt.group(1).decode() if filt else 'none'
    n += 1
    ext = {'DCTDecode': 'jpg', 'JPXDecode': 'jp2'}.get(f, 'bin')
    fn = os.path.join(out, 'obj%s.%s' % (m.group(1).decode(), ext))
    open(fn, 'wb').write(s)
    print(fn, f, w.group(1).decode() if w else '?', h.group(1).decode() if h else '?', len(s), d[:200])
print(n, 'images')
