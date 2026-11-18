"""Build templates/library/locus-iste.json from score.txt (Bruckner's four parts as read from the 1886 first
edition) and meta.json (the song's fields), writing in the breaths listed in BREATHS below.

    python3 -I parked/locus-iste/build/build.py          # from the content worktree's root

Prints every part's lines (seconds on one breath at the tempo) so the breaths can be checked.
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "templates" / "library" / "locus-iste.json"
STEP = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}
NAMES = ["soprano", "alto", "tenor", "bass"]
TITLES = {"soprano": "Soprano", "alto": "Alto", "tenor": "Tenor", "bass": "Bass"}

# Breaths written in (singable rule 1: a quick breath is half a beat and half a second at 60), each
# taken from the end of the note before the new line, which keeps at least half a beat. Each entry:
# part, the beat where the new line starts, and the lyric it sings when the breath falls inside a
# held syllable (the vowel sung again, as Ave verum's "(o)-"), else None.
BREATHS = [
    # Bars 14 and 18 ("ma-bi-le | sa-cra-men-tum"): the slurred last note of "le" gives up half a beat.
    *[(p, 56, None) for p in ("soprano", "alto", "tenor")],
    *[(p, 72, None) for p in ("soprano", "alto", "tenor")],
    # Bars 26 to 29, "ir-re-pre-hen-si-bi-lis est": the soprano and alto breathe before the mf "pre-" (bar 27),
    # and with the tenor before "est" (bar 29).
    ("soprano", 104, None), ("alto", 104, None),
    *[(p, 112, None) for p in ("soprano", "alto", "tenor")],
    # The bass sings bars 1 to 4 and 5 to 20 (and their return) without a printed rest: it breathes before "a" (bars 6 and 35), at the
    # printed comma "est, a" (bars 8 and 37), before the second "De-o" (bars 10 and 39), before "fac-tus"
    # (bar 11), before "in-æ-sti-ma-bi-le" (bars 12 and 16, the second at the printed comma "tum,"), and
    # before "sa-" and "men-" of each "sa-cra-men-tum" (bars 14, 15, 18 and 19).
    ("bass", 7, None), ("bass", 123, None),  # bars 2 and 31, before "a De-o"
    ("bass", 23, None), ("bass", 31, None), ("bass", 36, None), ("bass", 40, None), ("bass", 45, None),
    ("bass", 52, None), ("bass", 56, None), ("bass", 61, None), ("bass", 68, None), ("bass", 72, None),
    ("bass", 139, None), ("bass", 147, None), ("bass", 152, None),
    # Bars 40 to 42, "De- - - o", twelve beats on one syllable: everyone breathes at bar 41 and sings the
    # vowel again (the alto's tied B-flat and the bass's held line re-struck on the bar line).
    *[(p, 160, "(e)-") for p in NAMES],
    # Bars 44 to 48, "a De-o fac-tus est.": a breath before "fac-" (bar 46) and before "est." (bar 48).
    *[(p, 180, None) for p in NAMES],
    *[(p, 188, None) for p in NAMES],
]


def midi(name):
    m = re.fullmatch(r"([A-G])(#|b)?(\d)", name)
    if not m:
        raise ValueError(name)
    return 12 * (int(m.group(3)) + 1) + STEP[m.group(1)] + {"#": 1, "b": -1, None: 0}[m.group(2)]


def parse():
    parts, current = {}, None
    for raw in (HERE / "score.txt").read_text().splitlines():
        line = "" if raw.lstrip().startswith("#") else raw.strip()
        if not line:
            continue
        if line.startswith("["):
            current = line.strip("[]")
            parts[current] = ""
            continue
        parts[current] += " " + line
    out = {}
    for name, text in parts.items():
        bars = [b.split() for b in text.split("|") if b.strip()]
        if len(bars) != 48:
            sys.exit(f"{name}: {len(bars)} bars, not 48")
        events, beat = [], 0.0
        for i, bar in enumerate(bars):
            total = 0.0
            for tok in bar:
                m = re.fullmatch(r"([A-Gr][#b]?\d?)/([\d.]+)(=)?(?::(.+))?", tok)
                if not m:
                    sys.exit(f"{name} bar {i + 1}: can't read {tok}")
                length = float(m.group(2))
                if m.group(1) != "r":
                    events.append({"beat": beat + total, "length": length, "pitch": midi(m.group(1)),
                                   "tie": bool(m.group(3)), "lyric": m.group(4)})
                total += length
            if abs(total - 4) > 1e-9:
                sys.exit(f"{name} bar {i + 1}: {total} beats")
            beat += 4
        # ties: a tied note and the next (same pitch, no lyric of its own) become one
        notes = []
        for e in events:
            if notes and notes[-1]["tie"]:
                prev = notes[-1]
                if prev["pitch"] != e["pitch"] or e["lyric"] or abs(prev["beat"] + prev["length"] - e["beat"]) > 1e-9:
                    sys.exit(f"{name}: a tie at {prev['beat']} that doesn't join")
                prev["length"] += e["length"]
                prev["tie"] = e["tie"]
                continue
            notes.append(dict(e))
        out[name] = notes
    return out


def breathe(parts, tempo):
    for part, beat, lyric in BREATHS:
        notes = parts[part]
        i = next((k for k, n in enumerate(notes) if n["beat"] <= beat + 1e-9 < n["beat"] + n["length"] - 1e-9), None)
        if i is None:
            sys.exit(f"{part}: nothing sounding at {beat}")
        n = notes[i]
        if abs(n["beat"] - beat) > 1e-9:
            # a held note across the breath: split it, the second half sings the vowel again
            if not lyric:
                sys.exit(f"{part}: a breath at {beat} inside a held note needs a lyric")
            tail = {**n, "beat": beat, "length": n["beat"] + n["length"] - beat, "lyric": lyric}
            n["length"] = beat - n["beat"]
            notes.insert(i + 1, tail)
            i += 1
        elif lyric:
            notes[i]["lyric"] = lyric
        prev = notes[i - 1]
        if abs(prev["beat"] + prev["length"] - beat) > 1e-9:
            sys.exit(f"{part}: no note runs into the breath at {beat}")
        if prev["length"] < 1 - 1e-9:
            sys.exit(f"{part}: the note before {beat} is under a beat; a breath would leave less than half")
        prev["length"] -= 0.5
        notes[i]["br"] = True
    for notes in parts.values():
        notes[0]["br"] = True
        for prev, n in zip(notes, notes[1:]):
            if n["beat"] - (prev["beat"] + prev["length"]) >= 0.5 - 1e-9:
                n["br"] = True


def lines(notes, tempo):
    out, start = [], notes[0]["beat"]
    for prev, n in zip(notes, notes[1:]):
        if n.get("br"):
            out.append((start, prev["beat"] + prev["length"]))
            start = n["beat"]
    out.append((start, notes[-1]["beat"] + notes[-1]["length"]))
    return out


def main():
    meta = json.loads((HERE / "meta.json").read_text())
    parts = parse()
    breathe(parts, meta["tempo"])
    sec = 60 / meta["tempo"]
    for name in NAMES:
        ls = lines(parts[name], meta["tempo"])
        longest = max(ls, key=lambda ab: ab[1] - ab[0])
        print(f"{name:8} {len(ls):2} lines, longest {(longest[1] - longest[0]) * sec:4.1f} s from beat {longest[0]:g}")
        if "-v" in sys.argv:
            print("   ", ", ".join(f"{a:g}-{b:g}" for a, b in ls))
    song = {k: v for k, v in meta.items() if k not in ("sections", "chords", "melody")}
    song["sections"] = meta["sections"]
    song["chords"] = meta["chords"]
    song["parts"] = []
    for name in NAMES:
        notes = []
        for n in parts[name]:
            out = {"beat": round(n["beat"], 6), "length": round(n["length"], 6), "pitch": n["pitch"]}
            if n.get("lyric"):
                out["lyric"] = n["lyric"]
            if n.get("br"):
                out["br"] = True
            notes.append(out)
        pitches = [n["pitch"] for n in notes]
        part = {"key": name, "name": TITLES[name], "range": {"low": min(pitches), "high": max(pitches)},
                "guide": {"type": "notes", "notes": notes}}
        if name == meta["melody"]:
            part["melody"] = True
        song["parts"].append(part)
    OUT.write_text(json.dumps(song, indent=1, ensure_ascii=False) + "\n")
    print("wrote", OUT.relative_to(ROOT))


if __name__ == "__main__":
    main()
