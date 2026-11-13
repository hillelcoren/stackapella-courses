"""Build templates/library/good-christian-men-rejoice.json.

Tune and words: Helmore and Neale, The Condensed Vocal Parts to the Carols for Christmas-tide (1854), No. VI,
pp. 20 and 21 (verse by verse as printed). Chords checked against Bramley and Stainer, Christmas Carols New
and Old, first series, No. VIII, pp. 16 and 17 (unsigned). The alto, tenor and bass are our own.
Times are in eighths from each verse's start (the pickup); a verse is 102 eighths (34 dotted-quarter beats).
"""
import json
import sys
from fractions import Fraction as Fr
from pathlib import Path

OUT = Path(sys.argv[1])
NAMES = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def p(name):
    letter, rest = name[0], name[1:]
    acc = 0
    if rest.startswith("b"):
        acc, rest = -1, rest[1:]
    elif rest.startswith("#"):
        acc, rest = 1, rest[1:]
    return 12 * (int(rest) + 1) + NAMES[letter] + acc


# One verse: (eighth, eighths, soprano notes [(pitch, eighths)...], alto, tenor, bass, chord, line start).
# The soprano's list splits a melisma; the lower parts hold one note a syllable.
# Lengths here are as printed; breaths are cut afterwards.
F, BB, C, C7, AM, DM = (5, "maj", None), (10, "maj", None), (0, "maj", None), (0, "dom7", None), (9, "min", None), (2, "min", None)
BB_F = (10, "maj", 5)
F_C = (5, "maj", 0)
C7_E = (0, "dom7", 4)
GM_BB = (7, "min", 10)
GM7_D = (7, "min7", 2)
GM = (7, "min", None)
GM7 = (7, "min7", None)
AM_C = (9, "min", 0)
BB_D = (10, "maj", 2)

VERSE = [
    # Good Christian men, rejoice With heart, and soul, and voice;
    (0, 1, [("F4", 1)], "C4", "A3", "F3", F, True),
    (1, 2, [("F4", 2)], "D4", "Bb3", "F3", BB_F, False),
    (3, 1, [("F4", 1)], "C4", "C4", "F3", F, False),
    (4, 2, [("A4", 2)], "C4", "C4", "F3", F, False),
    (6, 1, [("Bb4", 1)], "D4", "Bb3", "F3", BB_F, False),
    (7, 5, [("C5", 2), ("D5", 1), ("C5", 2)], "E4", "G3", "C3", C, False),
    (12, 1, [("C5", 1)], "E4", "G3", "C3", C, False),
    (13, 2, [("F4", 2)], "D4", "Bb3", "F3", BB_F, False),
    (15, 1, [("F4", 1)], "C4", "C4", "F3", F, False),
    (16, 2, [("A4", 2)], "C4", "C4", "F3", F, False),
    (18, 1, [("Bb4", 1)], "D4", "Bb3", "F3", BB_F, False),
    (19, 5, [("C5", 2), ("D5", 1), ("C5", 2)], "E4", "G3", "C3", C, False),  # then a quaver rest
    # Give ye heed to what we say:
    (25, 2, [("C5", 2)], "E4", "C4", "A2", AM, True),
    (27, 1, [("D5", 1)], "F4", "Bb3", "G2", GM7, False),
    (28, 2, [("C5", 2)], "E4", "G3", "C3", C, False),
    (30, 1, [("Bb4", 1)], "E4", "G3", "C3", C7, False),
    (31, 2, [("A4", 2)], "F4", "A3", "F3", F, False),
    (33, 1, [("G4", 1)], "E4", "Bb3", "C3", C7, False),
    (34, 2, [("F4", 2)], "C4", "A3", "F3", F, False),  # then a quaver rest (verse 3: a dotted crotchet)
    # News! News! Jesus Christ is born to-day:
    (37, 2, [("F4", 2)], "D4", "Bb3", "Bb2", BB, True),  # then a quaver rest (verse 3: a dotted crotchet)
    (40, 3, [("F4", 3)], "D4", "A3", "D3", DM, False),
    (43, 2, [("G4", 2)], "Bb3", "F3", "D3", GM7_D, False),
    (45, 1, [("G4", 1)], "Bb3", "F3", "D3", GM7_D, False),
    (46, 2, [("A4", 2)], "C4", "A3", "C3", F_C, False),
    (48, 1, [("G4", 1)], "E4", "Bb3", "C3", C7, False),
    (49, 2, [("F4", 2)], "D4", "A3", "D3", DM, False),
    (51, 1, [("G4", 1)], "C4", "Bb3", "E3", C7_E, False),
    (52, 2, [("A4", 2)], "C4", "A3", "F3", F, False),  # then a quaver rest
    # Ox and ass before him bow, And He is in the manger now.
    (55, 2, [("C5", 2)], "E4", "C4", "A2", AM, True),
    (57, 1, [("D5", 1)], "F4", "Bb3", "G2", GM7, False),
    (58, 2, [("C5", 2)], "E4", "G3", "C3", C, False),
    (60, 1, [("Bb4", 1)], "E4", "G3", "C3", C7, False),
    (61, 2, [("A4", 2)], "F4", "A3", "F3", F, False),
    (63, 1, [("G4", 1)], "E4", "Bb3", "C3", C7, False),
    (64, 2, [("F4", 2)], "D4", "A3", "D3", DM, False),
    (66, 1, [("F4", 1)], "C4", "A3", "F3", F, False),
    (67, 2, [("G4", 2)], "Bb3", "F3", "D3", GM7_D, False),
    (69, 1, [("G4", 1)], "Bb3", "F3", "D3", GM7_D, False),
    (70, 2, [("A4", 2)], "C4", "A3", "C3", F_C, False),
    (72, 1, [("G4", 1)], "E4", "Bb3", "C3", C7, False),
    (73, 2, [("F4", 2)], "D4", "A3", "D3", DM, False),
    (75, 1, [("G4", 1)], "C4", "Bb3", "E3", C7_E, False),
    (76, 2, [("A4", 2)], "C4", "A3", "F3", F, False),  # then a quaver rest
    # Christ is born to-day! Christ is born to-day!
    (79, 2, [("D4", 2)], "Bb3", "F3", "D3", BB_D, True),
    (81, 1, [("D4", 1)], "Bb3", "F3", "D3", BB_D, False),
    (82, 2, [("E4", 2)], "C4", "G3", "C3", C, False),
    (84, 1, [("E4", 1)], "Bb3", "G3", "C3", C7, False),
    (85, 6, [("F4", 3), ("C5", 3)], "A3", "F3", "F3", F, False),
    (91, 2, [("A4", 2)], "C4", "A3", "F3", F, False),
    (93, 1, [("A4", 1)], "D4", "F3", "D3", DM, False),
    (94, 2, [("G4", 2)], "Bb3", "F3", "D3", GM7_D, False),
    (96, 1, [("G4", 1)], "Bb3", "E3", "C3", C7, False),
    (97, 3, [("F4", 3)], "A3", "F3", "F3", F, False),  # then a crotchet rest to the verse's end (102)
]

WORDS = {
    1: ["Good", "Christ-", "ian", "men,", "re-", "joice", "With", "heart,", "and", "soul,", "and", "voice;",
        "Give", "ye", "heed", "to", "what", "we", "say:", "News!", "News!", "Je-", "sus", "Christ", "is",
        "born", "to-", "day:", "Ox", "and", "ass", "be-", "fore", "him", "bow,", "And", "He", "is", "in", "the",
        "man-", "ger", "now.", "Christ", "is", "born", "to-", "day!", "Christ", "is", "born", "to-", "day!"],
    2: ["Good", "Christ-", "ian", "men,", "re-", "joice", "With", "heart,", "and", "soul,", "and", "voice;",
        "Now", "ye", "hear", "of", "end-", "less", "bliss;", "Joy!", "Joy!", "Je-", "sus", "Christ", "was",
        "born", "for", "this!", "He", "hath", "oped", "the", "heav'n-", "ly", "door,", "And", "man", "is",
        "bless-", "ed", "ev-", "er-", "more.", "Christ", "was", "born", "for", "this!", "Christ", "was", "born",
        "for", "this!"],
    3: ["Good", "Christ-", "ian", "men,", "re-", "joice", "With", "heart,", "and", "soul,", "and", "voice;",
        "Now", "ye", "need", "not", "fear", "the", "grave:", "Peace", "Peace!", "Je-", "sus", "Christ", "was",
        "born", "to", "save!", "Calls", "you", "one,", "and", "calls", "you", "all,", "To", "gain", "His", "e-",
        "ver-", "last-", "ing", "hall:", "Christ", "was", "born", "to", "save!", "Christ", "was", "born", "to",
        "save!"],
}

# Breaths (rule 1, at 60 a half beat = 1.5 quavers): the note before each new line gives up time so
# every part rests a half beat; (eighth of the syllable, its new length in eighths).
CUT = {19: Fr(9, 2), 34: Fr(3, 2), 52: Fr(3, 2), 76: Fr(3, 2)}
VERSE_LEN = 102
FINAL_LEN = 5  # the last "day!"/"save!" holds through the printed crotchet rest to the song's end


def r6(x):
    return round(float(x), 6)


def build():
    parts = {k: [] for k in ("soprano", "alto", "tenor", "bass")}
    chords = []
    phrases = []
    sections = []
    for v in (1, 2, 3):
        base = (v - 1) * VERSE_LEN
        words = WORDS[v]
        assert len(words) == len(VERSE), (v, len(words), len(VERSE))
        starts = []
        for i, (e, n, sop, a, t, b, chord, br) in enumerate(VERSE):
            length = Fr(n)
            sop = list(sop)
            # Verses 1 and 2: "News!"/"Joy!" is a crotchet and a quaver rest; verse 3's "Peace" a dotted crotchet.
            if e == 37 and v == 3:
                length, sop = Fr(3), [("F4", 3)]
            if e in CUT:
                cut = n - CUT[e]
                length = CUT[e]
                sop = sop[:-1] + [(sop[-1][0], sop[-1][1] - cut)]
            if e == 97 and v == 3:
                length, sop = Fr(FINAL_LEN), [("F4", FINAL_LEN)]
                t, b = "C3", "F2"  # the song's last chord complete: root, third and fifth
            start = Fr(base + e, 3)
            end = start + length / 3
            if br:
                starts.append(start)
            lyric = words[i]
            # soprano, split for melismas
            s = start
            for j, (name, m) in enumerate(sop):
                ns = s + Fr(m) / 3
                note = {"beat": r6(s), "length": r6(r6(ns) - r6(s)), "pitch": p(name)}
                if j == 0:
                    note["lyric"] = lyric
                    if br:
                        note["br"] = True
                parts["soprano"].append(note)
                s = ns
            assert s == end, (v, e)
            for key, name in (("alto", a), ("tenor", t), ("bass", b)):
                note = {"beat": r6(start), "length": r6(r6(end) - r6(start)), "pitch": p(name), "lyric": lyric}
                if br:
                    note["br"] = True
                parts[key].append(note)
            root, quality, bass = chord
            if not chords or (chords[-1]["root"], chords[-1]["quality"], chords[-1]["bass"]) != (root, quality, bass):
                chords.append({"beat": r6(start), "root": root, "quality": quality, "bass": bass})
        vend = Fr(base + VERSE_LEN, 3)
        bounds = starts + [vend]
        ph = [[r6(x), r6(y)] for x, y in zip(bounds, bounds[1:])]
        sections.append({"name": f"Verse {v}", "startBeat": r6(Fr(base, 3)), "endBeat": r6(vend), "phrases": ph})
    return parts, chords, sections


def main():
    parts, chords, sections = build()
    meta = json.loads((Path(__file__).parent / "meta.json").read_text())
    names = {"soprano": "Soprano", "alto": "Alto", "tenor": "Tenor", "bass": "Bass"}
    song = dict(meta)
    song["chords"] = chords
    song["sections"] = sections
    song["parts"] = []
    for key in ("soprano", "alto", "tenor", "bass"):
        notes = parts[key]
        part = {"key": key, "name": names[key]}
        if key == "soprano":
            part["melody"] = True
        part["range"] = {"low": min(n["pitch"] for n in notes), "high": max(n["pitch"] for n in notes)}
        part["guide"] = {"type": "notes", "notes": notes}
        song["parts"].append(part)
    OUT.write_text(json.dumps(song, indent=4, ensure_ascii=False) + "\n")
    print("wrote", OUT, "notes", {k: len(v) for k, v in parts.items()}, "end", sections[-1]["endBeat"])


main()
