#!/bin/sh
# zoom.sh page x0 x1 y0 y1 scale name clefs : coloured staff zoom of a page (pgm in the scans folder) as png
S=/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine-scans/bnf
T=/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine-tools
B=/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine/parked/cantique-de-jean-racine/build
python3 -I $B/staffzoom.py $S/pgm/p$1.pgm $2 $3 $4 $5 $6 $S/crops/$7.ppm $8 && $T/ppm2png $S/crops/$7.ppm $S/crops/$7.png && rm $S/crops/$7.ppm
