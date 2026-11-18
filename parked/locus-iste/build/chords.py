"""Name the chord the four parts sound at each change, as a first draft of the template's `chords`
(each then checked by hand against the score; overrides in CHORD_FIX in this file).

    python3 -I parked/locus-iste/build/chords.py templates/library/locus-iste.json [--json]
"""
import json
import sys

QUAL = {
    "maj": (0, 4, 7), "min": (0, 3, 7), "dim": (0, 3, 6), "aug": (0, 4, 8), "sus4": (0, 5, 7), "sus2": (0, 2, 7),
    "dom7": (0, 4, 7, 10), "maj7": (0, 4, 7, 11), "min7": (0, 3, 7, 10), "dim7": (0, 3, 6, 9), "hdim7": (0, 3, 6, 10),
    "maj6": (0, 4, 7, 9), "min6": (0, 3, 7, 9),
}
NAME = ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"]


def best(pcs, bass):
    """The chord that covers the most sounding pitch classes with the fewest extras, preferring triads,
    the bass as root, and complete chords."""
    out = []
    for root in range(12):
        for q, iv in QUAL.items():
            tones = {(root + i) % 12 for i in iv}
            covered = len(pcs & tones)
            missing = len(tones - pcs)
            extra = len(pcs - tones)
            score = covered * 3 - extra * 4 - missing * 2 + (1 if root == bass else 0) - (0.5 if len(iv) == 4 else 0)
            if root not in pcs:
                score -= 3
            out.append((score, root, q))
    out.sort(reverse=True)
    return out[0]


def main():
    song = json.loads(open(sys.argv[1]).read())
    parts = {p["key"]: p["guide"]["notes"] for p in song["parts"]}

    def at(notes, beat):
        for n in notes:
            if n["beat"] <= beat + 1e-6 < n["beat"] + n["length"]:
                return n["pitch"]
        return None

    beats = sorted({n["beat"] for ns in parts.values() for n in ns})
    rows, last = [], None
    for b in beats:
        sounding = {k: at(ns, b) for k, ns in parts.items()}
        ps = [p for p in sounding.values() if p is not None]
        if not ps:
            continue
        pcs = {p % 12 for p in ps}
        bass = min(ps) % 12
        score, root, q = best(pcs, bass)
        chord = (root, q, None if bass == root else bass)
        names = " ".join(f"{k[0]}{NAME[v % 12]}{v // 12 - 1}" if v is not None else f"{k[0]}-" for k, v in sounding.items())
        if chord != last:
            rows.append({"beat": b, "root": root, "quality": q, "bass": chord[2]})
            if "--json" not in sys.argv:
                bar, beat_in = int(b // 4) + 1, b % 4 + 1
                print(f"{b:7g}  bar {bar:2} b{beat_in:<5g} {NAME[root]:>2}{q:<5} {('/' + NAME[bass]) if chord[2] is not None else '':4}  {names}  ({score:g})")
            last = chord
    if "--json" in sys.argv:
        print(json.dumps(rows))


if __name__ == "__main__":
    main()
