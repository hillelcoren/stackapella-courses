#!/bin/bash
# usage: sys.sh page.jpg name y0 y1 [xsplit] [scale]
# Crops one vocal system of a scan page into a left and right half (in crops/), then finds noteheads.
B=/Users/hillel/Code/arranger-keep/new/hallelujah-chorus/parked/hallelujah-chorus/build
cd /Users/hillel/Code/arranger-keep/new/hallelujah-chorus-scans || exit 1
P=$1; N=$2; Y0=$3; Y1=$4; XS=${5:-1120}; SC=${6:-1.4}
W=$(sips -g pixelWidth "$P" | awk '/pixelWidth/{print $2}')
python3 -I $B/crop.py "$P" crops/$N-L.png 100 $Y0 $((XS + 60)) $Y1 $SC >/dev/null
python3 -I $B/crop.py "$P" crops/$N-R.png $((XS - 60)) $Y0 $W $Y1 $SC >/dev/null
for h in L R; do echo "== $N-$h"; python3 -I $B/heads.py crops/$N-$h.png 700 820 ${CLEFS:-tt8b} ${SHARPS:-FC}; done
