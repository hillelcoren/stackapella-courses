"""Build templates/library/shema-yisrael.json from the 1926 Goldfarb page (No. 18 and 19, p. 17), read from the scan.

Tune: G major, 3/4, unison congregation line, printed "Traditional":
  B4 G4 A4 | B4 G4 G4 | C5 G4 A4 | B4 A4(fermata) G4 A4 | B4 A4 | G4(fermata)
Verse 1 Shema Yisrael, verse 2 Baruch shem (the print: "On Yom Kippur add").
Fermatas realised: "nu," and its twin hold into an added bar (the pickup "A-do-" stays an upbeat); the end of verse 1
holds into an added bar before Baruch shem. Breath rests 0.75 beat (half a second at 72).
Harmony: our own SATB under the printed tune.
"""
import json
import os
import sys

OUT = sys.argv[1]
B = 0.75  # breath rest at 72 bpm: half a second, rounded up to a quarter beat

G3, A3, B3, C4, D4, E4, F4s, G4, A4, B4, C5 = 55, 57, 59, 60, 62, 64, 66, 67, 69, 71, 72
G2, A2, C3, D3, E3, F3s = 43, 45, 48, 50, 52, 54

def n(beat, length, pitch, lyric=None, br=False):
    d = {"beat": beat, "length": length, "pitch": pitch}
    if lyric is not None:
        d["lyric"] = lyric
    if br:
        d["br"] = True
    return d


V1 = ["Sh'ma", "Yis-", "ra-", "el,", "A-", "do-", "shem", "E-", "lo-", "kei-", "nu,", "A-", "do-", "shem", "e-", "chad."]
# Verse 1 rhythm and tune, beats from 0
S1 = [(0, 2, B4), (2, .5, G4), (2.5, .5, A4), (3, 2 - B, B4), (5, .5, G4), (5.5, .5, G4), (6, 2, C5), (8, .5, G4),
      (8.5, .5, A4), (9, 1, B4), (10, 4 - B, A4), (14, .5, G4), (14.5, .5, A4), (15, 2, B4), (17, 1, A4), (18, 6 - B, G4)]
BR1 = {0, 5, 14}
A1 = [G4, E4, F4s, G4, E4, E4, E4, E4, F4s, G4, F4s, E4, F4s, D4, C4, B3]
T1 = [D4, D4, D4, D4, B3, B3, C4, C4, C4, D4, A3, B3, A3, G3, F3s, G3]
BS1 = [G3, G3, G3, E3, E3, E3, C3, A2, A2, D3, D3, D3, D3, D3, D3, G2]

# Verse 2 (offset 24): Ba-(B) ruch(G, A slurred) shem(B) | ke-(G, the print's two G eighths as one) vod(C) mal-(G) chu-(A)
# | to(B, A slurred and held) le-(G) o-(A) | lam(B) va-(A) | ed.(G)
O = 24
S2 = [(0, 2, B4, "Ba-", True), (2, .5, G4, "ruch", False), (2.5, .5, A4, None, False), (3, 2 - B, B4, "shem", False),
      (5, 1, G4, "ke-", True), (6, 2, C5, "vod", False), (8, .5, G4, "mal-", False), (8.5, .5, A4, "chu-", False),
      (9, 1, B4, "to", False), (10, 4 - B, A4, None, False), (14, .5, G4, "le'-", True), (14.5, .5, A4, "o-", False),
      (15, 2, B4, "lam", False), (17, 1, A4, "va'-", False), (18, 3, G4, "ed.", False)]
LY2 = ["Ba-", "ruch", "shem", "ke-", "vod", "mal-", "chu-", "to", "le'-", "o-", "lam", "va'-", "ed."]
# harmony rhythm in verse 2: one note a syllable (the alto's "to" slurs with the tune, F-sharp under its held A)
H2 = [(0, 2), (2, 1), (3, 2 - B), (5, 1), (6, 2), (8, .5), (8.5, .5), (9, 5 - B), (14, .5), (14.5, .5), (15, 2), (17, 1), (18, 3)]
A2n = [D4, E4, G4, E4, E4, E4, F4s, G4, E4, F4s, D4, C4, B3]
T2 = [D4, D4, D4, B3, C4, C4, C4, D4, B3, A3, G3, F3s, D3]
BS2 = [G3, G3, E3, E3, C3, A2, A2, D3, D3, D3, D3, D3, G2]


def part1(pitches):
    out = []
    for i, (b, l, _) in enumerate(S1):
        out.append(n(b, l, pitches[i], V1[i], b in BR1))
    return out


def sop():
    notes = part1([p for _, _, p in S1])
    for b, l, p, ly, br in S2:
        notes.append(n(O + b, l, p, ly, br))
    return notes


def harm(p1, p2, alto=False):
    notes = part1(p1)
    lyr = iter(LY2)
    for i, (b, l) in enumerate(H2):
        ly = next(lyr)
        if alto and b == 9:  # "to": G4 under the tune's B, then F-sharp slurred under its held A
            notes.append(n(O + 9, 1, G4, "to"))
            notes.append(n(O + 10, 4 - B, F4s))
            continue
        notes.append(n(O + b, l, p2[i], ly, b in (0, 5, 14)))
    return notes


def rng(notes):
    ps = [x["pitch"] for x in notes]
    return {"low": min(ps), "high": max(ps)}


CH = [(0, 7, "maj", None), (3, 4, "min7", None), (6, 0, "maj", None), (8, 9, "min7", None), (9, 7, "maj", 2),
      (10, 2, "maj", None), (14, 4, "min7", 2), (14.5, 2, "maj", None), (15, 7, "maj", 2), (17, 2, "dom7", None), (18, 7, "maj", None)]
chords = [{"beat": o + b, "root": r, "quality": q, "bass": bs} for o in (0, O) for b, r, q, bs in CH]
# verse 2: "ruch" is E minor 7 over G (the alto holds E a whole beat under the tune G, A)
chords.insert(len(CH) + 1, {"beat": O + 2, "root": 4, "quality": "min7", "bass": 7})

parts_notes = {
    "soprano": sop(),
    "alto": harm(A1, A2n, alto=True),
    "tenor": harm(T1, T2),
    "bass": harm(BS1, BS2),
}
NAMES = {"soprano": "Soprano", "alto": "Alto", "tenor": "Tenor", "bass": "Bass"}
parts = []
for k in ["soprano", "alto", "tenor", "bass"]:
    p = {"key": k, "name": NAMES[k]}
    if k == "soprano":
        p["melody"] = True
    p["range"] = rng(parts_notes[k])
    p["guide"] = {"type": "notes", "notes": parts_notes[k]}
    parts.append(p)

meta = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "meta.json"), encoding="utf-8"))
t = dict(meta)
t["chords"] = chords
t["sections"] = [
    {"name": "Shema Yisrael", "startBeat": 0, "endBeat": 24, "phrases": [[0, 5], [5, 14], [14, 24]]},
    {"name": "Baruch shem", "startBeat": 24, "endBeat": 45, "phrases": [[24, 29], [29, 38], [38, 45]]},
]
t["parts"] = parts
with open(OUT, "w", encoding="utf-8") as f:
    f.write(json.dumps(t, indent=1, ensure_ascii=False) + "\n")
print("wrote", OUT)
