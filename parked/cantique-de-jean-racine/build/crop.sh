#!/bin/sh
# crop.sh in.jpg out.png y x h w scale : crop a region of a page scan and enlarge it (sips, macOS)
in=$1; out=$2; y=$3; x=$4; h=$5; w=$6; s=${7:-3}
sips -s format png --cropOffset "$y" "$x" -c "$h" "$w" "$in" --out "$out.tmp.png" >/dev/null 2>&1 || exit 1
sips -z $((h*s)) $((w*s)) "$out.tmp.png" --out "$out" >/dev/null 2>&1
rm -f "$out.tmp.png"
