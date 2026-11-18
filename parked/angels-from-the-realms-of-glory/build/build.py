"""Builds angels-from-the-realms-of-glory.json from Henry Smart's four parts to Regent Square as printed
in C. L. Hutchins, The Church Hymnal (Boston: The Parish Choir, 1894), No. 60, p. 82, read from the scan,
in C as printed; written out a tone lower, in B-flat. Prints the changes from Smart's lower parts.
Run: python3 -I build.py <out.json>

Time is counted in quavers (e) from the start of a verse; 4/4, a crotchet is one beat, so beat = e / 2."""
import json
import sys

STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
SHIFT = -2  # printed in C, written in B-flat


def midi(n):
    acc = n[1:-1]
    return 12 * (int(n[-1]) + 1) + STEP[n[0]] + {"": 0, "#": 1, "b": -1}[acc] + SHIFT


# The tune as printed: (quaver, quavers long, pitch). One verse is 12 bars, 96 quavers.
TUNE = [
    (0, 2, "G4"), (2, 2, "E4"), (4, 2, "C5"), (6, 2, "G4"),
    (8, 3, "E5"), (11, 1, "D5"), (12, 2, "C5"), (14, 2, "G4"),
    (16, 2, "A4"), (18, 2, "A4"), (20, 2, "G4"), (22, 2, "C5"),
    (24, 2, "G4"), (26, 2, "F4"), (28, 4, "E4"),
    (32, 2, "G4"), (34, 2, "E4"), (36, 2, "C5"), (38, 2, "G4"),
    (40, 3, "E5"), (43, 1, "D5"), (44, 2, "C5"), (46, 2, "B4"),
    (48, 2, "C5"), (50, 2, "B4"), (52, 2, "A4"), (54, 1, "B4"), (55, 1, "C5"),
    (56, 2, "B4"), (58, 2, "A4"), (60, 4, "G4"),
    (64, 3, "D5"), (67, 1, "D5"), (68, 2, "B4"), (70, 2, "G4"),
    (72, 3, "E5"), (75, 1, "D5"), (76, 2, "C5"), (78, 2, "A4"),
    (80, 2, "F5"), (82, 2, "E5"), (84, 2, "D5"), (86, 2, "C5"),
    (88, 2, "C5"), (90, 2, "B4"), (92, 4, "C5"),
]
SLOTS = [0, 2, 4, 6, 8, 11, 12, 14, 16, 18, 20, 22, 24, 26, 28,
         32, 34, 36, 38, 40, 43, 44, 46, 48, 50, 52, 54, 56, 58, 60,
         64, 67, 68, 70, 72, 75, 76, 78, 80, 82, 84, 86, 88, 90, 92]
HELD = {28: 32, 60: 64, 92: 96}  # the half notes

# Words: verse 1 as printed under the music; verses 2 and 3 as printed below it, with the refrain's
# "Come and worship" sung twice as verse 1 prints it under the notes.
V1 = "An- gels from the realms of glo- ry, Wing your flight o'er all the earth; " \
     "Ye, who sang cre- a- tion's sto- ry, Now pro- claim Mes- si- ah's birth: " \
     "Come and wor- ship, Come and wor- ship, Wor- ship Christ the new- born King."
V2 = "Shep- herds in the field a- bid- ing, Watch- ing o'er your flocks by night; " \
     "God with man is now re- sid- ing, Yon- der shines the in- fant- light: " \
     "Come and wor- ship, Come and wor- ship, Wor- ship Christ, the new- born King."
V3 = "Sa- ges, leave your con- tem- pla- tions; Bright- er vi- sions beam a- far: " \
     "Seek the great De- sire of na- tions, Ye have seen His na- tal star: " \
     "Come and wor- ship, Come and wor- ship, Wor- ship Christ, the new- born King."
VERSES = [V1, V2, V3]

# Smart's lower parts as printed (alto, tenor, bass) at each syllable; where a part moves within a
# syllable, its first note (the second is in SMART_MOVES).
SMART = {
    0: ("E4", "C4", "C3"), 2: ("C4", "G3", "C3"), 4: ("G4", "G3", "E3"), 6: ("E4", "C4", "C3"),
    8: ("G4", "C4", "G3"), 11: ("G4", "B3", "F3"), 12: ("G4", "C4", "E3"), 14: ("G4", "C4", "E3"),
    16: ("C4", "A3", "F3"), 18: ("C4", "C4", "F3"), 20: ("C4", "G3", "E3"), 22: ("C4", "A3", "A2"),
    24: ("D4", "G3", "B2"), 26: ("B3", "G3", "G2"), 28: ("C4", "G3", "C3"),
    32: ("E4", "C4", "C4"), 34: ("C4", "C4", "G3"), 36: ("G4", "G3", "E3"), 38: ("G4", "G3", "E3"),
    40: ("E4", "C4", "C3"), 43: ("F4", "B3", "D3"), 44: ("E4", "A3", "E3"), 46: ("E4", "G#3", "E3"),
    48: ("E4", "A3", "A3"), 50: ("E4", "G#3", "E3"), 52: ("E4", "E4", "C3"), 54: ("E4", "D4", "A2"),
    56: ("G4", "D4", "D3"), 58: ("F#4", "C4", "D3"), 60: ("G4", "B3", "G2"),
    64: ("G4", "B3", "G3"), 67: ("G4", "B3", "G3"), 68: ("G4", "D4", "G3"), 70: ("G4", "B3", "G3"),
    72: ("G4", "C4", "C3"), 75: ("E4", "Bb3", "C3"), 76: ("F4", "A3", "F3"), 78: ("F4", "C4", "F3"),
    80: ("A4", "D4", "D3"), 82: ("G4", "G3", "E3"), 84: ("F4", "A3", "F3"), 86: ("E4", "C4", "A3"),
    88: ("G4", "D4", "G3"), 90: ("G4", "D4", "G2"), 92: ("E4", "C4", "C3"),
}
# Smart's moves within a syllable (part, quaver): the second note.
SMART_MOVES = {("alto", 39): "F4", ("bass", 39): "D3", ("tenor", 55): "C4", ("tenor", 85): "B3",
               ("bass", 85): "G3", ("alto", 87): "F4", ("alto", 91): "F4 (G4 held from 88)"}

OURS = dict(SMART)
WHY = {}


def change(e, parts, why):
    OURS[e] = parts
    WHY[e] = why


change(12, ("E4", "C4", "E3"), "\"glo-\": the alto E4 (Smart's G4, a bare fourth under the tune's C5)")
change(14, ("E4", "C4", "E3"), "\"ry,\": the alto E4 (Smart's G4, a unison with the tune)")
change(16, ("C4", "C4", "F3"), "\"Wing\": the tenor holds C4 (Smart's A3, doubling the tune's A, the F chord's third), so the third isn't doubled and the tenor holds instead of leaping")
change(20, ("E4", "C4", "E3"), "\"flight\": the alto E4 and the tenor C4 (Smart's C4 and G3), so the duet sings a third, not a fifth")
change(22, ("E4", "C4", "A2"), "\"o'er\": the alto E4 and the tenor C4 (Smart's C4 and A3), so the duet has no octave; Smart's A3 under the alto's E4 would move in fifths with it into \"all\"")
change(24, ("D4", "D4", "B2"), "\"all\": the tenor D4 (Smart's G3), stepping up, with no parallel octaves with the tune")
change(44, ("A4", "C4", "E3"), "\"sto-\": the alto A4 and the tenor C4 (Smart's E4 and A3), so the duet sings a third")
change(46, ("G#4", "E4", "E3"), "\"ry,\": the alto G-sharp 4 and the tenor E4 (Smart's E4 and G-sharp 3), so the duet and trio have the E chord's third, not a bare fifth")
change(48, ("A4", "E4", "A3"), "\"Now\": the alto A4 and the tenor E4 (Smart's E4 and A3)")
change(50, ("G#4", "E4", "E3"), "\"pro-\": the alto G-sharp 4 and the tenor E4 (Smart's E4 and G-sharp 3), as at \"ry,\"")
change(64, ("B4", "D4", "G3"), "\"Come\": the alto B4 and the tenor D4 (Smart's G4 and B3), so the duet and trio have a third, not a bare fifth")
change(67, ("B4", "D4", "G3"), "\"and\": as \"Come\"")
change(36, ("E4", "C4", "E3"), "\"sang\": the alto E4 and the tenor C4 (Smart's G4 and G3), so the duet sings a sixth, not a bare fourth")
change(38, ("G4", "B3", "D3"), "\"cre-\": one note a syllable, the alto on Smart's first quaver (G4; his F4 after it is a second under the tune that would rise to G4 on \"a-\"), the bass on his second (D3), and the tenor B3 (Smart's G3), so the passing G chord on D has its third")
change(43, ("G4", "B3", "D3"), "\"tion's\": the alto holds G4 (Smart's F4, a seventh that would rise to the alto's A on \"sto-\"), a passing G chord on D")
change(40, ("G4", "C4", "C3"), "\"a-\": the alto G4 (Smart's E4, an octave under the tune's E5)")
change(54, ("E4", "C4", "A2"), "\"Mes-\": the tenor C4 for the syllable (Smart's D4 then C4)")
change(75, ("Bb4", "E4", "C3"), "\"and\": the alto B-flat 4 and the tenor E4 (Smart's E4 and B-flat 3, exchanged), so the duet sings a third and each falls or rises a step into the F chord")
change(76, ("A4", "F4", "F3"), "\"wor-\": the alto A4 and the tenor F4 (Smart's F4 and A3), so the duet has the F chord's third, not a bare fifth, the alto's seventh falls and the tenor's E rises")
change(84, ("F4", "A3", "F3"), "\"Christ\": one note a syllable, Smart's first quaver (tenor A3, bass F3)")
change(86, ("E4", "C4", "A3"), "\"the\": the alto E4 for the syllable (Smart's E4 then F4)")
change(88, ("E4", "C4", "G3"), "\"new-\": the alto E4 and the tenor C4 (Smart's G4 and D4, the tune's C suspended over a G chord), a C chord over the bass's G, so the duet has no bare fourth")
change(90, ("F4", "D4", "G2"), "\"born\": the alto F4 on the beat (Smart holds G4 and moves to F4 halfway)")

ROOT = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "Bb": 10, "B": 11}
CHORDS = {  # quaver: (root, quality, bass or None), in C as printed
    0: ("C", "maj", None), 4: ("C", "maj", "E"), 6: ("C", "maj", None),
    8: ("C", "maj", "G"), 11: ("G", "dom7", "F"), 12: ("C", "maj", "E"),
    16: ("F", "maj", None), 20: ("C", "maj", "E"), 22: ("A", "min", None),
    24: ("G", "maj", "B"), 26: ("G", "dom7", None), 28: ("C", "maj", None),
    32: ("C", "maj", None), 34: ("C", "maj", "G"), 36: ("C", "maj", "E"), 38: ("G", "maj", "D"),
    40: ("C", "maj", None), 43: ("G", "maj", "D"), 44: ("A", "min", "E"), 46: ("E", "maj", None),
    48: ("A", "min", None), 50: ("E", "maj", None), 52: ("A", "min", "C"), 54: ("A", "min", None),
    56: ("G", "maj", "D"), 58: ("D", "dom7", None), 60: ("G", "maj", None),
    64: ("G", "maj", None), 72: ("C", "maj", None), 75: ("C", "dom7", None), 76: ("F", "maj", None),
    80: ("D", "min", None), 82: ("C", "maj", "E"), 84: ("D", "min", "F"), 86: ("A", "min", None),
    88: ("C", "maj", "G"), 90: ("G", "dom7", None), 92: ("C", "maj", None),
}

LINE_STARTS = [0, 32, 64]          # a breath before each (Smart's couplets)
CUT = {28: 2, 60: 2}               # "earth" and "birth" give up a beat for the breath
VERSE_E = 96
REST_E = 8                         # a bar's rest between verses
TEMPO = 100


def b(e):
    return round(e / 2, 6)


def syllables(text):
    out = text.split()
    assert len(out) == len(SLOTS), (len(out), len(SLOTS))
    return [w[:-1] + "-" if w.endswith("-") else w for w in out]


def build():
    parts = {k: [] for k in ("soprano", "alto", "tenor", "bass")}
    chords = []
    for v, text in enumerate(VERSES):
        off = v * (VERSE_E + REST_E)
        words = dict(zip(SLOTS, syllables(text)))
        for e, n, p in TUNE:
            end = e + n - CUT.get(e, 0)
            note = {"beat": b(off + e), "length": round(b(off + end) - b(off + e), 6), "pitch": midi(p)}
            if e in words:
                note["lyric"] = words[e]
            if e in LINE_STARTS:
                note["br"] = True
            parts["soprano"].append(note)
        for i, e in enumerate(SLOTS):
            nxt = HELD.get(e, SLOTS[i + 1] if i + 1 < len(SLOTS) else VERSE_E)
            end = nxt - CUT.get(e, 0)
            for k, p in zip(("alto", "tenor", "bass"), OURS[e]):
                note = {"beat": b(off + e), "length": round(b(off + end) - b(off + e), 6), "pitch": midi(p),
                        "lyric": words[e]}
                if e in LINE_STARTS:
                    note["br"] = True
                parts[k].append(note)
        for e, (r, q, bass) in sorted(CHORDS.items()):
            chords.append({"beat": b(off + e), "root": (ROOT[r] + SHIFT) % 12, "quality": q,
                           "bass": (ROOT[bass] + SHIFT) % 12 if bass else None})
    return parts, chords


def report():
    for e in SLOTS:
        if OURS[e] != SMART[e]:
            print(f"q{e:>3} {SMART[e]} -> {OURS[e]}  {WHY.get(e, '')}")
    for (k, e), p in SMART_MOVES.items():
        print(f"q{e:>3} {k}: Smart moves on to {p} within the syllable")


def main(out):
    meta = json.load(open(__file__.rsplit("/", 1)[0] + "/meta.json"))
    parts, chords = build()
    total = b((VERSE_E + REST_E) * (len(VERSES) - 1) + VERSE_E)
    sections = []
    for v in range(len(VERSES)):
        o = b(v * (VERSE_E + REST_E))
        end = o + (48 if v == len(VERSES) - 1 else 52)
        sections.append({"name": f"Verse {v + 1}", "startBeat": o, "endBeat": end,
                         "phrases": [[o, o + 16], [o + 16, o + 32], [o + 32, end]]})
    assert sections[-1]["endBeat"] == total
    song = dict(meta)
    song["tempo"] = TEMPO
    song["chords"] = chords
    song["sections"] = sections
    names = {"soprano": "Soprano", "alto": "Alto", "tenor": "Tenor", "bass": "Bass"}
    song["parts"] = []
    for k in ("soprano", "alto", "tenor", "bass"):
        ns = parts[k]
        end = max(n["beat"] + n["length"] for n in ns)
        assert abs(end - total) < 1e-6, (k, end, total)
        part = {"key": k, "name": names[k]}
        if k == "soprano":
            part["melody"] = True
        part["range"] = {"low": min(n["pitch"] for n in ns), "high": max(n["pitch"] for n in ns)}
        part["guide"] = {"type": "notes", "notes": ns}
        song["parts"].append(part)
    with open(out, "w") as f:
        json.dump(song, f, indent=4, ensure_ascii=False)
        f.write("\n")
    report()


if __name__ == "__main__":
    main(sys.argv[1])
