#!/bin/sh
# sc.sh page name x0 y0 x1 y1 [width]: plain crop of the native page scan, upscaled
S=/Users/hillel/Code/arranger-keep/new/locus-iste-scans
D=$S/sc; mkdir -p $D
W=${7:-1600}
sips -s format png -c $(( $6 - $4 )) $(( $5 - $3 )) --cropOffset $4 $3 $S/p$1.jpg --out $D/$2.png >/dev/null
sips --resampleWidth $W $D/$2.png >/dev/null
