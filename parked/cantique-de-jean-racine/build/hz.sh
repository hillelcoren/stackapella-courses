#!/bin/sh
# hz.sh page top x0 x1 name [above below] : one staff, enlarged 8 times, from (above) px over its top line to (below) px under it
S=/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine-scans/bnf
case $1 in 3) o=28;; 4) o=30;; 5) o=32;; 6) o=34;; 7) o=36;; 8) o=38;; 9) o=40;; esac
a=${6:-8}; b=${7:-28}
/Users/hillel/Code/arranger-keep/new/cantique-de-jean-racine/parked/cantique-de-jean-racine/build/crop.sh $S/img/obj$o.jpg $S/crops/$5.png $(($2-a)) $3 $((a+b)) $(($4-$3)) 8
