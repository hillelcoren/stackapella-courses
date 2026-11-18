#!/bin/sh
# usage: voices.sh page.jpg outprefix : crops the four voice staves (most lyrics) in two halves and runs heads.py
B=$(dirname "$0")
python3 -I "$B/staves.py" "$1" > "$2.staves"
python3 -I - "$2.staves" > "$2.range" <<'PY'
import sys, re
rows = [tuple(map(float, re.findall(r'[\d.]+', l)[:3])) for l in open(sys.argv[1])]
best = max(range(len(rows) - 3), key=lambda i: sum(r[2] for r in rows[i:i + 4]) if 550 < rows[i][0] < 1150 else -1)
print(int(rows[best][0] - 38), int(rows[best + 3][1] + 42))
PY
read Y0 Y1 < "$2.range"
python3 -I "$B/crop.py" "$1" "$2a.jpg" $Y0 $Y1 30 480 1.0 >/dev/null
python3 -I "$B/crop.py" "$1" "$2b.jpg" $Y0 $Y1 460 915 1.0 >/dev/null
echo "range $Y0-$Y1"
for h in a b; do echo "-- $h"; python3 -I "$B/heads.py" "$2$h.jpg" TTCB; done
