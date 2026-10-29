"""Builds course/plus/improvising-harmony/course.json, Improvising a harmony, from the app's own
checked song templates (templates/free and templates/library), so every note and chord is the
arranger's. Steps are semitones from the learner's comfortable note. The course file is generated:
fix this script, then regenerate, never the JSON by hand (it would be overwritten).

    python3 -I tools/imp_course.py && python3 -I tools/coursefmt.py course/plus/improvising-harmony/course.json
"""
import json
import sys

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "course/plus/improvising-harmony/course.json"
EN = lambda s: {"en": s}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual, listen=None):
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards]}
    if listen:
        step["listen"] = listen
    step["visual"] = visual
    step["reviewed"] = False
    return step


def template(name, folder):
    data = json.load(open(f"{folder}/{name}.json"))
    key = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}[data["key"]]
    return data, key


# ---- Michael, Row the Boat Ashore, from the app's free template (traditional; the 1867 words) ----
MICHAEL, KEY = template("michael-row", REPO / "templates/free")
TONIC = 65  # F4, the template's do
TUNE = [{"beat": n["beat"], "length": n["length"], "step": n["pitch"] - TONIC, "lyric": n.get("lyric")} for n in MICHAEL["parts"][0]["guide"]["notes"]]
CHORDS = [{"beat": c["beat"], "rel": (c["root"] - KEY) % 12, "quality": c["quality"]} for c in MICHAEL["chords"]]
SPAN = 32
assert TUNE[-1]["beat"] + TUNE[-1]["length"] == SPAN

# The next chord tone up from each tune note: a third, but a fourth over so (do', never ti), and the
# seventh (fa) over re when the chord is V. Line 1 (beats 0 to 16), line 2 (16 to 32).
ABOVE = {0: 4, 2: 5, 4: 7, 5: 9, 7: 12, 9: 12}
HARMONY = [{**n, "step": ABOVE[n["step"]]} for n in TUNE]


def placed(notes, do, start=0, lyrics=True):
    out = []
    for n in notes:
        note = {"beat": n["beat"] + start, "length": n["length"], "step": n["step"] + do}
        if lyrics and n.get("lyric"):
            note["lyric"] = n["lyric"]
        out.append(note)
    return out


def chords(do, start=0, until=SPAN, quality_v="dom7"):
    out = []
    for c in CHORDS:
        if c["beat"] >= until:
            continue
        quality = quality_v if c["rel"] == 7 else c["quality"]
        out.append({"beat": c["beat"] + start, "root": (c["rel"] + do) % 12, "quality": quality, "bass": None})
    return out


DO = -7  # the tune 0 to +9 becomes -7 to +2; the part above, +4 to +12, becomes -3 to +5
BAR = 4


def chords_window(do, frm, to, start):
    """The chords from beat `frm` to `to`, the one already sounding at `frm` included, moved to `start`."""
    sounding = [c for c in CHORDS if c["beat"] <= frm][-1]
    inside = [c for c in CHORDS if frm < c["beat"] < to]
    return [{"beat": c["beat"] - frm + start, "root": (c["rel"] + do) % 12, "quality": "dom7" if c["rel"] == 7 else c["quality"], "bass": None}
            for c in [dict(sounding, beat=frm)] + inside]


def line(notes, frm, to):
    return [n for n in notes if frm <= n["beat"] < to]


# ---- Any library tune: its melody and chords, and the harmony worked out from them ----

LIBRARY = REPO / "templates/library"
KEYS = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
TONES = {"maj": [0, 4, 7], "min": [0, 3, 7], "dom7": [0, 4, 7, 10], "min7": [0, 3, 7, 10], "maj7": [0, 4, 7, 11], "dim": [0, 3, 6]}
SCALE = [0, 2, 4, 5, 7, 9, 11]


# Corrections to a template's chords, until the template itself is fixed: none now (Red River Valley's
# early dominant was fixed in its template, version 5).
CHORD_FIXES = {}


def tune(name, frm=0, to=None):
    """A library tune's melody (steps from its do) and chords (roots from its do), from beat `frm`, re-timed to start at 0."""
    data = json.load(open(f"{LIBRARY}/{name}.json"))
    key = KEYS[data["key"]]
    tonic = min(p for p in range(48, 84) if p % 12 == key and p >= min(n["pitch"] for n in data["parts"][0]["guide"]["notes"]) - 11)
    to = to if to is not None else 10 ** 6
    mel = [{"beat": n["beat"] - frm, "length": n["length"], "step": n["pitch"] - tonic, "lyric": n.get("lyric")} for n in data["parts"][0]["guide"]["notes"] if frm <= n["beat"] < to]
    source = CHORD_FIXES.get(name, data["chords"])
    chords = [{"beat": c["beat"] - frm, "rel": (c["root"] - key) % 12, "quality": c["quality"]} for c in source]
    before = [c for c in chords if c["beat"] <= 0]
    chords = ([dict(before[-1], beat=0)] if before else []) + [c for c in chords if 0 < c["beat"] < to - frm]
    return mel, chords


def chord_at(chords, beat):
    now = [c for c in chords if c["beat"] <= beat]
    return now[-1] if now else chords[0]


def tones_of(chord):
    return {(chord["rel"] + t) % 12 for t in TONES.get(chord["quality"], TONES["maj"])}


def third_above(step):
    deg = max(i for i, sc in enumerate(SCALE) if sc <= step % 12)
    return step - step % 12 + SCALE[(deg + 2) % 7] + (12 if deg + 2 >= 7 else 0)


def part_above(mel, chords):
    """The next chord tone up from each tune note; over a note outside the chord (a passing note), a
    third above it in the key. On a note of a beat or more, never one or two semitones above the tune
    (the arranger's guard: over a chord's seventh the next chord tone sits a step away and sounds
    wrong); there too, the third above in the key."""
    out = []
    for n in mel:
        tones = tones_of(chord_at(chords, n["beat"] + 0.01))
        if n["step"] % 12 in tones:
            up = next(n["step"] + d for d in range(1, 13) if (n["step"] + d) % 12 in tones)
            if up - n["step"] <= 2 and n["length"] >= 1:
                up = third_above(n["step"])
        else:
            up = third_above(n["step"])
        out.append({**n, "step": up})
    return out


RUBS = {1, 2, 6, 10, 11}  # a second, a tritone or a seventh
FALLBACKS = []  # notes left as rests, reported when the file is built


def chord_choices(mel, chords, do, lo=-9, hi=5, above=None, below=False, tune=None, only=None, bass=False):
    """At each note, every chord tone in the learner's range, never a pitch class the tune sounds during
    it (so a lit note is never a copy), and over a tune note outside the chord (a passing note) nothing
    that rubs with it: a second, a tritone or a seventh. `only` keeps some chord degrees (0 the root,
    7 the fifth); `above` keeps notes above every tune note it sounds against."""
    out = []
    tune = tune if tune is not None else mel
    for n in mel:
        chord = chord_at(chords, n["beat"] + 0.01)
        tones = tones_of(chord)
        if only is not None:
            tones = {(chord["rel"] + d) % 12 for d in only}
        during = [t for t in tune if t["beat"] < n["beat"] + n["length"] - 0.01 and t["beat"] + t["length"] > n["beat"] + 0.01]
        sounding = set() if bass else {(t["step"] + do) % 12 for t in during}  # a bass on the tune's root is a bass, not a copy
        passing = [t["step"] + do for t in during if t["step"] % 12 not in tones_of(chord_at(chords, t["beat"] + 0.01))]
        own = (n["step"] + do) % 12
        span = [s for s in range(lo, hi + 1) if (s - do) % 12 in tones]
        if above is not None:
            span = [s for s in span if all(s > t["step"] + do for t in during)]
        if below:
            span = [s for s in span if all(s < t["step"] + do for t in during)] or span
        # The strictest first; relaxed only when nothing is left: no rubs and no tune notes, then no rubs, then not the tune's own note.
        ok = ([s for s in span if s % 12 not in sounding and not any(abs(s - p) % 12 in RUBS for p in passing)]
              or [s for s in span if s % 12 != own and not any(abs(s - p) % 12 in RUBS for p in passing)]
              or [s for s in span if bass or s % 12 != own])
        if not ok:
            FALLBACKS.append(n["beat"])
            continue  # nothing fits (a tenor note with no chord tone above it in reach): a rest for you
        out.append({"beat": n["beat"], "length": n["length"], "step": ok[0], "choices": ok, "lyric": n.get("lyric")})
    return out


def place_do(lines, lo=-9, hi=5):
    """The do that puts every line within the learner's window, as centred as it goes."""
    steps = [n["step"] for line in lines for n in line]
    low, high = min(steps), max(steps)
    best = (lo + hi) // 2 - (low + high) // 2
    return max(lo - low, min(hi - high, best))


def lib_chords(chords, do, start=0):
    return [{"beat": c["beat"] + start, "root": (c["rel"] + do) % 12, "quality": c["quality"], "bass": None} for c in chords]


def imp_1_third():
    first = line(HARMONY, 0, 16)
    long_ones = [n for n in first if n["length"] >= 1.5]
    return {
        "id": "imp-1-third", "title": EN("A part above"), "strictness": "relaxed",
        "steps": [
            learn("The simplest harmony: sing two scale notes above the tune, a third. Where that clashes with the chord, go one note higher.",
                  [("Hear it first", "One line, the tune and the part above together"),
                   ("Above a loud tune, go lighter", "Never louder; stop if anything tightens or hurts"),
                   ("Best with headphones", "You'll hear the tune as you sing")], "harmony",
                  {"tempo": 92, "notes": placed(first, DO), "turn": False, "with": [{"notes": placed(line(TUNE, 0, 16), DO)}], "chords": chords(DO, until=16)}),
            {"kind": "play", "text": EN("First sing the tune itself, once through, so it's yours."),
             "exercise": {"tempo": 92, "notes": placed(TUNE, DO, BAR), "turn": False, "chords": chords(DO, BAR)}},
            {"kind": "play", "text": EN("Now hold the harmony on the long notes while the tune moves. Hear the chord ring."),
             "exercise": {"tempo": 92, "notes": placed(long_ones, DO, BAR), "turn": False,
                          "with": [{"notes": placed(line(TUNE, 0, 16), DO, BAR)}], "chords": chords(DO, BAR, 16)}},
            {"kind": "play", "text": EN("Now the part above, the whole verse, every note lit, while the guide sings the tune."),
             "exercise": {"tempo": 92, "notes": placed(HARMONY, DO, BAR), "turn": False, "generous": True,
                          "with": [{"notes": placed(TUNE, DO, BAR)}], "chords": chords(DO, BAR)},
             "measures": EN("Scored on your harmony's notes on pitch. Did you know? Medieval English singers called two voices moving mostly in thirds \"gymel\", from the Latin for twin.")},
        ],
    }


def imp_1_switch():
    scale = [0, 2, 4, 5, 7]
    under = {0: (0, "maj"), 2: (7, "dom7"), 4: (0, "maj"), 5: (5, "maj"), 7: (7, "dom7")}
    thirds = {0: 4, 2: 5, 4: 7, 5: 9, 7: 11}
    sung = [{"beat": BAR + 2 * k, "length": 2, "step": thirds[s] + DO, "lyric": "ah"} for k, s in enumerate(scale)]
    guide = [{"beat": BAR + 2 * k, "length": 2, "step": s + DO} for k, s in enumerate(scale)]
    harm = [{"beat": BAR + 2 * k, "root": (under[s][0] + DO) % 12, "quality": under[s][1], "bass": None} for k, s in enumerate(scale)]

    def clip(low, high, root, quality):
        return {"notes": [{"beat": 0, "length": 3, "step": low + DO}, {"beat": 0, "length": 3, "step": high + DO}],
                "chords": [{"beat": 0, "root": (root + DO) % 12, "quality": quality, "bass": None}]}
    rounds = [
        {"prompt": EN("Over do, which third fits the key?"), "clips": [clip(0, 4, 0, "maj"), clip(0, 3, 0, "maj")], "answer": 0,
         "why": EN("A, do to mi, is a major third, in the key. B's note is a half step (the smallest step on a piano) low: it clashes with the chord.")},
        {"prompt": EN("Over re, which third fits the key?"), "clips": [clip(2, 6, 7, "dom7"), clip(2, 5, 7, "dom7")], "answer": 1,
         "why": EN("B, re to fa, is a minor third: smaller, but in the key. A's note is outside it.")},
        {"prompt": EN("Over mi, which third fits the key?"), "clips": [clip(4, 7, 0, "maj"), clip(4, 8, 0, "maj")], "answer": 0,
         "why": EN("A, mi to so, a minor third, stays in the key. A third above isn't always the same size.")},
        {"prompt": EN("Over fa, which third fits the key?"), "clips": [clip(5, 8, 5, "maj"), clip(5, 9, 5, "maj")], "answer": 1,
         "why": EN("B, fa to la, a major third. The key decides: you just follow the scale.")},
    ]
    return {
        "id": "imp-1-switch", "title": EN("Major and minor thirds"),
        "steps": [
            learn("A third above switches between major and minor to stay in the key. You don't count it: you follow the scale, two notes up.",
                  [("Major thirds", "Do to mi, fa to la, so to ti"),
                   ("Minor thirds", "Re to fa, mi to so"),
                   ("The chords decide", "Listen to them under you")], "harmony",
                  {"tempo": 72, "notes": [dict(n, beat=n["beat"] - BAR) for n in sung], "turn": False,
                   "with": [{"notes": [dict(n, beat=n["beat"] - BAR) for n in guide]}], "chords": [dict(c, beat=c["beat"] - BAR) for c in harm]}),
            {"kind": "choose", "text": EN("Listen to each, as often as you like, then choose the third that fits."), "exercise": {"tempo": 72, "rounds": rounds}},
            {"kind": "play", "text": EN("The guide climbs do re mi fa so; you sing a third above each, over the chords."),
             "exercise": {"tempo": 72, "notes": sung, "turn": False, "with": [{"notes": guide}], "chords": harm},
             "measures": EN("Scored on your thirds on pitch, major and minor.")},
        ],
    }


def imp_1_fourth():
    def clip(top):
        return {"notes": [{"beat": 0, "length": 3, "step": 7 + DO}, {"beat": 0, "length": 3, "step": top + DO}],
                "chords": [{"beat": 0, "root": DO % 12, "quality": "maj", "bass": None}]}
    rounds = [
        {"prompt": EN("Over so, which harmony rubs?"), "clips": [clip(11), clip(12)], "answer": 0,
         "why": EN("A puts ti over the chord of do: a seventh against do, and it rubs. B's do rings.")},
        {"prompt": EN("Over so, which harmony rubs?"), "clips": [clip(12), clip(11)], "answer": 1,
         "why": EN("B's ti rubs again. Over so, take do: a fourth up, in the chord.")},
    ]
    first = line(HARMONY, 0, 16)
    return {
        "id": "imp-1-fourth", "title": EN("Third or fourth?"),
        "steps": [
            learn("Hear why the part goes one note higher over so: with the chord of do under it, the third above so (ti) rubs, and do rings.",
                  [("Over so", "Not ti, but do"),
                   ("A fourth, not a third", "The next note in the chord"),
                   ("Every so in the tune", "Row, boat, shore, jah")], "harmony"),
            {"kind": "choose", "text": EN("Listen to each, then choose the one that rubs."), "exercise": {"tempo": 72, "rounds": rounds}},
            {"kind": "play", "text": EN("The first line again, the part above: do over every so."),
             "exercise": {"tempo": 92, "notes": placed(first, DO, BAR), "turn": False,
                          "with": [{"notes": placed(line(TUNE, 0, 16), DO, BAR)}], "chords": chords(DO, BAR, 16)},
             "measures": EN("Scored on your harmony's notes on pitch, every so answered with do.")},
        ],
    }


def imp_1_ear():
    tune1, harm1 = line(TUNE, 0, 16), line(HARMONY, 0, 16)
    bare = lambda notes: [{"beat": n["beat"], "length": n["length"], "step": n["step"] + DO} for n in notes]
    harmony = {"notes": bare(tune1) + bare(harm1)}
    copied = {"notes": bare(tune1) + [dict(n, step=n["step"] + 12) for n in bare(tune1)]}
    lowcopy = {"notes": bare(tune1) + [dict(n, step=n["step"] - 12) for n in bare(tune1)]}
    below = {"notes": bare(tune1) + [dict(n, step=n["step"] - 12) for n in bare(harm1)]}
    two = [EN("A harmony"), EN("The same tune")]
    rounds = [
        {"prompt": EN("Is the second voice singing a harmony, or the same tune?"), "clips": [harmony], "options": two, "answer": 0,
         "why": EN("A harmony: the second voice moved with the tune but on its own notes, a chord tone above.")},
        {"prompt": EN("Is the second voice singing a harmony, or the same tune?"), "clips": [copied], "options": two, "answer": 1,
         "why": EN("The same tune, an octave up. It's fuller, but it isn't a harmony: every note is the tune's own.")},
        {"prompt": EN("Which one copied the tune?"), "clips": [harmony, copied], "answer": 1,
         "why": EN("B copied: the second voice sang the tune's own notes. A made chords.")},
        {"prompt": EN("Which one copied the tune?"), "clips": [lowcopy, below], "answer": 0,
         "why": EN("A copied, an octave down: the same notes, so it adds no chords. B sang its own part below.")},
    ]
    return {
        "id": "imp-1-ear", "title": EN("Harmony or the tune?"),
        "steps": [
            learn("A harmony makes chords with the tune; a copy just doubles it. Learn to hear the difference, then keep your part as the lights fade.",
                  [("Listen first", "Harmony, or the same tune?"),
                   ("Then sing the part above", "The whole verse"),
                   ("The lights fade", "The second half is yours, by ear")], "harmony"),
            {"kind": "choose", "text": EN("Listen to each, as often as you like, then choose."), "exercise": {"tempo": 92, "rounds": rounds}},
            {"kind": "play", "text": EN("The part above, the whole verse. Halfway through, the lights fade: keep going by ear."),
             "exercise": {"tempo": 92, "notes": placed(HARMONY, DO, BAR), "turn": False, "lights": "fade",
                          "with": [{"notes": placed(TUNE, DO, BAR)}], "chords": chords(DO, BAR)},
             "measures": EN("Scored on your harmony's notes on pitch, the second half sung with only faint outlines to follow.")},
        ],
    }


def cue(step):
    return [{"beat": 0, "length": 2, "step": step, "listenOnly": True}]


def sung(notes_, do, start):
    return [{"beat": n["beat"] + start, "length": n["length"], "step": n["step"] + do, **({"lyric": n["lyric"]} if n.get("lyric") else {})} for n in notes_]


def shifted(picks, start):
    """Chosen-note lines (already placed from home), moved to start at `start`, their choices kept."""
    return [dict(p, beat=p["beat"] + start) for p in picks]


def guide_line(mel, do, start, volume=None):
    line = {"notes": [{"beat": n["beat"] + start, "length": n["length"], "step": n["step"] + do} for n in mel]}
    if volume:
        line["volume"] = volume
    return line


def imp_1_challenge():
    mel, chs = tune("home-on-the-range", 49, 96)
    above = part_above(mel, chs)
    do = place_do([above])
    return {
        "id": "imp-1-challenge", "title": EN("A new tune"), "challenge": True,
        "steps": [
            learn("A tune you know less: Home on the Range's refrain. The same rule: the next chord tone up, a third over passing notes.",
                  [("Listen to the refrain", "Home, home on the range"),
                   ("Lights where the chord changes", "Between them, by ear"),
                   ("Light and easy", "Above a loud tune, go lighter, never louder")], "harmony",
                  {"tempo": 100, "notes": sung(above, do, 0), "turn": False, "with": [guide_line(mel, do, 0)], "chords": lib_chords(chs, do)}),
            {"kind": "play", "text": EN("The part above the refrain. The lights show only where the chord changes."),
             "exercise": {"tempo": 100, "notes": cue(do + above[0]["step"]) + sung(above, do, 4), "turn": False, "lights": "changes",
                          "with": [guide_line(mel, do, 4)], "chords": lib_chords(chs, do, 4)},
             "measures": EN("Scored on your part's notes on pitch, most of them sung with no light to follow. Did you know? Home on the Range began as a Kansas doctor's poem, printed in 1873, and became Kansas's state song in 1947.")},
        ],
    }


# ---- Unit 2: Below, and holding on ----

def imp_2_below():
    below = [{**n, "step": n["step"] - 12} for n in HARMONY]
    do = 3  # the part below, -8 to 0 from do, becomes -5 to +3
    return {
        "id": "imp-2-below", "title": EN("A part below"),
        "steps": [
            learn("A third above, an octave down, is a sixth below. Under so, sing do, not ti: the same fix, upside down.",
                  [("The tune above you", "Michael, Row again"),
                   ("Your part below", "The same notes as the part above, an octave down"),
                   ("Every note lit", "Listen up to the tune")], "harmony",
                  {"tempo": 92, "notes": sung(line(below, 0, 16), do, 0), "turn": False, "with": [guide_line(line(TUNE, 0, 16), do, 0)], "chords": chords(do, until=16)}),
            {"kind": "play", "text": EN("The part below, the whole verse, while the guide sings the tune above you."),
             "exercise": {"tempo": 92, "notes": cue(do) + sung(below, do, BAR), "turn": False, "with": [guide_line(TUNE, do, BAR)], "chords": chords(do, BAR)},
             "measures": EN("Scored on your part's notes on pitch, under the tune. Did you know? Michael, Row the Boat Ashore was written down in 1863 from freed people on St. Helena Island, South Carolina, and printed in 1867.")},
        ],
    }


def imp_2_hold():
    do = DO
    holds = [(16, 5.5, 0), (22, 2, -1), (24, 3.5, 0), (28, 2, -1), (30, 2, 0)]
    notes_ = [{"beat": b - 16 + BAR, "length": l, "step": st + 12 + do, "lyric": "oo"} for b, l, st in holds]
    second = line(TUNE, 16, 32)

    def hold_chords(start):
        """Line 2's chords from its first beat (the chord sounding at beat 16 starts it)."""
        line2 = [c for c in CHORDS if 16 <= c["beat"] < 32]
        first = [c for c in CHORDS if c["beat"] <= 16][-1]
        return [{"beat": (c["beat"] - 16) + start, "root": (c["rel"] + do) % 12, "quality": c["quality"], "bass": None} for c in ([dict(first, beat=16)] if first["beat"] < 16 else []) + line2]
    return {
        "id": "imp-2-hold", "title": EN("Hold, then step off"),
        "steps": [
            learn("Lost? Hold your note until it rubs, then step. A rub usually steps, most often down: over the chord of so, do steps to ti.",
                  [("Hold do", "Under Michael's second line"),
                   ("When it rubs", "The chord changes to so: step down to ti"),
                   ("Then home", "Back to do when the chord comes home")], "drone",
                  {"tempo": 92, "notes": [dict(n, beat=n["beat"] - BAR) for n in notes_], "turn": False,
                   "with": [guide_line([dict(n, beat=n["beat"] - 16) for n in second], do, 0)], "chords": hold_chords(0)}),
            {"kind": "play", "text": EN("Hold do under the tune; where the chord changes and it rubs, step to ti, then back home."),
             "exercise": {"tempo": 92, "notes": cue(12 + do) + notes_, "turn": False,
                          "with": [guide_line([dict(n, beat=n["beat"] - 16) for n in second], do, BAR)], "chords": hold_chords(BAR)},
             "measures": EN("Scored on your held notes on pitch, and the step to ti where the chord changed.")},
        ],
    }


def imp_2_echo():
    def round_(frm, to, text):
        call = line(TUNE, frm, to)
        call0 = [dict(n, beat=n["beat"] - frm) for n in call]
        part = [dict(n, beat=n["beat"] - frm) for n in line(HARMONY, frm, to)]
        span = max(n["beat"] + n["length"] for n in call0)
        return {"kind": "play", "text": EN(text),
                "exercise": {"tempo": 92, "notes": sung(call0, DO, 0), "answer": sung(part, DO, 0), "turn": True,
                             "with": [guide_line(call0, DO, span + 1)], "chords": chords_window(DO, frm, to, span + 1)}}
    first = round_(0, 16, "Hear the line; then the guide sings it again and you sing the part above.")
    second = round_(16, 32, "The second line: hear it, then harmonise it as it comes round again.")
    second["measures"] = EN("Scored on your part's notes on pitch as the line came round again.")
    return {
        "id": "imp-2-echo", "title": EN("Answer in harmony"),
        "steps": [
            learn("Hear a line once, then harmonise it as it comes round again: the first step to harmonising a tune you've never heard.",
                  [("Listen", "The guide sings a line"),
                   ("Then harmonise", "The line again, you above it"),
                   ("The next chord tone up", "Lit for you, as before")], "echo"),
            first, second,
        ],
    }


def imp_2_challenge():
    mel, chs = tune("steal-away", 0, 32)
    above = part_above(mel, chs)
    below = [{**n, "step": n["step"] - 12} for n in above]
    do_low = place_do([below])
    do_high = place_do([above])
    return {
        "id": "imp-2-challenge", "title": EN("Under and over"), "challenge": True,
        "steps": [
            learn("Steal Away, the spiritual's refrain: once with your part below the tune, then once above it.",
                  [("First, below", "Your part under the tune"),
                   ("Then, above", "The same notes; now the tune is under you"),
                   ("Lost?", "Hold your note until it rubs, then step")], "harmony",
                  {"tempo": 66, "notes": sung(mel, do_low, 0), "turn": False, "chords": lib_chords(chs, do_low)}),
            {"kind": "play", "text": EN("The refrain, your part below the tune."),
             "exercise": {"tempo": 66, "notes": cue(do_low + below[0]["step"]) + sung(below, do_low, 4), "turn": False, "with": [guide_line(mel, do_low, 4)], "chords": lib_chords(chs, do_low, 4)}},
            {"kind": "play", "text": EN("Again, your part above the tune."),
             "exercise": {"tempo": 66, "notes": cue(do_high + above[0]["step"]) + sung(above, do_high, 4), "turn": False, "with": [guide_line(mel, do_high, 4)], "chords": lib_chords(chs, do_high, 4)},
             "measures": EN("Scored on your part above on pitch. Could you hear the tune under you? Did you know? Steal Away was sung at a Choctaw Nation school in Indian Territory, in today's Oklahoma.")},
        ],
    }


# ---- Unit 3: Any chord tone ----

def in_chord_rounds_v(do):
    """Unit 4's own rounds, in Steal Away's key, two of them harder: the seventh of the chord of so is in
    it; la over the chord of so rubs."""
    def clip(note, root, quality="maj"):
        return {"notes": [{"beat": 0, "length": 3, "step": note + do}], "chords": [{"beat": 0, "root": (root + do) % 12, "quality": quality, "bass": None}]}
    two = [EN("In the chord"), EN("It clashes")]
    return [
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(5, 7, "dom7")], "options": two, "answer": 0, "why": EN("Fa over the chord of so with its seventh: fa is that seventh, so it belongs, leaning toward mi.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(9, 7, "dom7")], "options": two, "answer": 1, "why": EN("La over the chord of so: a step above so, and it rubs.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(7, 0)], "options": two, "answer": 0, "why": EN("So over the chord of do: its fifth, open and in.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(2, 5)], "options": two, "answer": 1, "why": EN("Re over the chord of fa: a step from do, and it rubs.")},
    ]

def in_chord_rounds():
    """Listen and choose: a held note over a chord, in it or clashing (the tune's chords, in the course key)."""
    def clip(note, root, quality="maj"):
        return {"notes": [{"beat": 0, "length": 3, "step": note + DO}], "chords": [{"beat": 0, "root": (root + DO) % 12, "quality": quality, "bass": None}]}
    two = [EN("In the chord"), EN("It clashes")]
    return [
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(4, 0)], "options": two, "answer": 0, "why": EN("Mi over the chord of do: in it, so it rings.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(5, 0)], "options": two, "answer": 1, "why": EN("Fa over the chord of do: a half step from mi, and it rubs.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(9, 5)], "options": two, "answer": 0, "why": EN("La over the chord of fa: its third, in it.")},
        {"prompt": EN("Over this chord, is the held note in it?"), "clips": [clip(0, 7, "dom7")], "options": two, "answer": 1, "why": EN("Do over the chord of so: not in it, and it wants to step down to ti.")},
    ]

def imp_3_chord():
    first = line(TUNE, 0, 16)
    arps = []
    beat = BAR
    for c in [cc for cc in CHORDS if cc["beat"] < 16]:
        root = c["rel"]
        for k, t in enumerate([0, 4, 7, 4] if c["quality"] != "min" else [0, 3, 7, 3]):
            arps.append({"beat": beat + k, "length": 1, "step": root + t + DO - (12 if root + t + DO > 5 else 0), "lyric": "ah"})
        beat += 4
    end = max(n["beat"] + n["length"] for n in first)
    long_ = [{"beat": BAR + c["beat"], "length": min(([x["beat"] for x in CHORDS if x["beat"] > c["beat"]] + [end])[0], end) - c["beat"]} for c in CHORDS if c["beat"] < 16]
    picks = chord_choices([{"beat": x["beat"] - BAR, "length": x["length"], "step": next(n["step"] for n in first if n["beat"] <= x["beat"] - BAR + 0.01 and n["beat"] + n["length"] > x["beat"] - BAR)} for x in long_], CHORDS, DO, tune=first)
    return {
        "id": "imp-3-chord", "title": EN("Sing the chord"),
        "steps": [
            learn("A basic chord, a triad, has three notes, and any of them is a harmony, except the tune's own.",
                  [("Sing each chord", "Its three notes, up and back"),
                   ("Then choose", "One long note to each chord"),
                   ("Every lit note works", "The tune's own note never lights")], "harmony"),
            {"kind": "choose", "text": EN("First, ears only: in the chord, or not?"), "exercise": {"tempo": 72, "rounds": in_chord_rounds()}},
            {"kind": "play", "text": EN("Sing each chord's notes, up and back, over its chord."),
             "exercise": {"tempo": 92, "notes": cue(DO) + arps, "turn": False, "chords": [dict(c, beat=BAR + 4 * k) for k, c in enumerate(chords(DO, 0, 16))]}},
            {"kind": "play", "text": EN("One long note to each chord: any lit note, under or over the tune."),
             "exercise": {"tempo": 92, "notes": cue(DO) + [dict(p, beat=p["beat"] + BAR) for p in picks], "turn": False,
                          "with": [guide_line(first, DO, BAR)], "chords": chords(DO, BAR, 16)},
             "measures": EN("Scored on landing on a lit note at each chord, held while the tune moves. Did you know? In barbershop the lead sings the tune, the tenor above it, the bass below, and the baritone fills in the chord.")},
        ],
    }


def imp_3_two_ways():
    picks = chord_choices(TUNE, CHORDS, DO)
    ex = lambda rules: {"tempo": 92, "notes": cue(DO) + [dict(p, beat=p["beat"] + BAR) for p in picks], "turn": False,
                        "with": [guide_line(TUNE, DO, BAR)], "chords": chords(DO, BAR), "score": "species", "rules": rules}
    return {
        "id": "imp-3-two-ways", "title": EN("Close, then against"),
        "steps": [
            learn("Two ways to make a part your own: barely move, or move against the tune.",
                  [("Take 1: stay close", "Hold, or move to the nearest lit note"),
                   ("Take 2: move against it", "When the tune climbs, fall"),
                   ("Compare them", "Hear both together")], "harmony"),
            {"kind": "play", "text": EN("Take 1: any lit note, moving as little as you can: hold, or take the nearest."), "exercise": ex("close"),
             "measures": EN("Scored on landing on lit notes; the top score needs four moves in five to be a step or a third, and some real moving: not one held note.")},
            {"kind": "play", "text": EN("Take 2: any lit note, moving against the tune."), "exercise": ex("against"),
             "measures": EN("Scored on landing on lit notes; the top score needs half your moves, of the ones that move, against the tune.")},
        ],
    }


def imp_3_challenge():
    mel, chs = tune("swing-low", 0, 31)
    do = place_do([[{"step": 0}], [{"step": 7}]])
    picks = chord_choices(mel, chs, do)
    return {
        "id": "imp-3-challenge", "title": EN("Your harmony"), "challenge": True,
        "steps": [
            learn("Swing Low, Sweet Chariot's chorus, your own harmony: any lit note, the tune's own never.",
                  [("Every chord tone lights", "Choose as you go"),
                   ("Stay close", "Small moves make a part easy to sing"),
                   ("Listen", "Hear it together afterwards")], "harmony",
                  {"tempo": 76, "notes": sung(mel, do, 0), "turn": False, "chords": lib_chords(chs, do)}),
            {"kind": "play", "text": EN("The chorus: at each note, any lit note. Make your own harmony."),
             "exercise": {"tempo": 76, "notes": cue(do) + shifted(picks, 4), "turn": False, "with": [guide_line(mel, do, 4)], "chords": lib_chords(chs, do, 4), "score": "species", "rules": "close"},
             "measures": EN("Scored on landing on lit notes, and the top score needs four moves in five to be a step or a third. Did you know? In shape-note singing from The Sacred Harp (1844), the tune is in the tenor, with parts sung above and below it.")},
        ],
    }


# ---- Unit 4: No lights ----

def imp_4_hints():
    mel, chs = tune("steal-away", 32, 64)
    do = place_do([[{"step": 0}], [{"step": 9}]])
    picks = chord_choices(mel, chs, do)
    return {
        "id": "imp-4-hints", "title": EN("Lights when you need them"),
        "steps": [
            learn("Fewer lights: a note shows only once you've been off it for a beat. Find it by ear first.",
                  [("Listen to the verse", "Steal Away's verse, with its chords"),
                   ("Lost?", "Hold your note until it rubs, then step"),
                   ("A light comes late", "Only if you need it")], "harmony",
                  {"tempo": 66, "notes": sung(mel, do, 0), "turn": False, "chords": lib_chords(chs, do)}),
            {"kind": "choose", "text": EN("Ears only: in the chord, or not?"), "exercise": {"tempo": 72, "rounds": in_chord_rounds_v(do)}},
            {"kind": "play", "text": EN("Steal Away's verse, any chord tone; a light shows only once you've been off for a beat."),
             "exercise": {"tempo": 66, "notes": cue(do) + shifted(picks, 4), "turn": False, "lights": "late",
                          "with": [guide_line(mel, do, 4)], "chords": lib_chords(chs, do, 4), "score": "species", "rules": "close"},
             "measures": EN("Scored on your notes landing in the chord, most of them before any light showed, and the top score needs small moves, a step or a third, and some real moving.")},
        ],
    }


def imp_4_free():
    picks = chord_choices(TUNE, CHORDS, DO)
    return {
        "id": "imp-4-free", "title": EN("Lights off"),
        "steps": [
            learn("No lights at all. The chords sound under you: any note in the chord, except the tune's own, is a harmony.",
                  [("Listen to the chords", "They tell you where you are"),
                   ("Lost?", "Hold a note until it rubs, then step"),
                   ("Afterwards", "Hear what you made")], "harmony",
                  {"tempo": 92, "notes": placed(TUNE, DO), "turn": False, "chords": chords(DO)}),
            {"kind": "play", "text": EN("Michael, Row, lights off. Sing a harmony by ear."),
             "exercise": {"tempo": 92, "notes": cue(DO) + [dict(p, beat=p["beat"] + BAR) for p in picks], "turn": False, "lights": "off",
                          "with": [guide_line(TUNE, DO, BAR)], "chords": chords(DO, BAR), "score": "species", "rules": "close"},
             "measures": EN("Scored on your notes landing in the chord, by ear, and the top score needs small moves, a step or a third, and some real moving.")},
        ],
    }


def imp_4_high():
    mel, chs = tune("simple-gifts", 0, 34)
    do = 1 - max(n["step"] for n in mel)  # the tune's top at +1, so the part above it has room up to +5
    picks = chord_choices(mel, chs, do, above=0)
    return {
        "id": "imp-4-high", "title": EN("The tenor above"),
        "steps": [
            learn("The tenor, a part above the lead, is part of bluegrass's high lonesome sound. Light and easy, never the pressed edge.",
                  [("Above the tune", "Every lit note is higher than the tune's"),
                   ("Hear it first", "Simple Gifts, then lights off"),
                   ("Light and easy", "Never pushed; stop if anything tightens")], "harmony",
                  {"tempo": 84, "notes": sung(mel, do, 0), "turn": False, "chords": lib_chords(chs, do)}),
            {"kind": "play", "text": EN("Simple Gifts: a part above the tune, lights off."),
             "exercise": {"tempo": 84, "notes": cue(picks[0]["step"]) + shifted(picks, 4), "turn": False, "lights": "off", "with": [guide_line(mel, do, 4)], "chords": lib_chords(chs, do, 4)},
             "measures": EN("Scored on landing on the chord tones above the tune, by ear. Did you know? Bluegrass is named after Bill Monroe's Blue Grass Boys, and Monroe often sang the high tenor above the lead.")},
        ],
    }


def imp_4_challenge():
    mel, chs = tune("red-river-valley")
    do = place_do([[{"step": 0}], [{"step": 9}]])
    above = chord_choices(mel, chs, do)
    below = chord_choices(mel, chs, do, lo=-9, hi=-2, only=[0, 7], bass=True)  # roots and fifths, low: a bass under your own harmony
    ex = lambda picks, extra=None: {"tempo": 90, "notes": cue(do) + shifted(picks, 4), "turn": False, "lights": "off",
                                    "with": [guide_line(mel, do, 4)], "chords": lib_chords(chs, do, 4), **(extra or {})}
    return {
        "id": "imp-4-challenge", "title": EN("A trio of you"), "challenge": True,
        "keepSong": {"title": EN("Red River Valley, a trio of me"), "takes": [{"step": 2, "name": EN("My harmony")}, {"step": 3, "name": EN("My bass")}], "from": 3, "partners": [EN("The tune")], "chords": EN("Chords")},
        "steps": [
            learn("Red River Valley, a tune new to this course. Hear it once; then harmonise it by ear, again, and then a part under your own.",
                  [("Hear it once", "Just the tune"),
                   ("Harmonise it twice", "Lights off; the second time you know it"),
                   ("Then a bass under yourself", "Roots and fifths: three of you")], "harmony",
                  {"tempo": 90, "notes": sung(mel, do, 0), "turn": False, "chords": lib_chords(chs, do)}),
            {"kind": "play", "text": EN("First listen: a harmony by ear, lights off."), "exercise": ex(above)},
            {"kind": "play", "text": EN("Again: now you know the tune."), "exercise": ex(above)},
            {"kind": "play", "text": EN("Last: a bass under it all, roots and fifths, with your second take singing too. A trio of you."),
             "exercise": ex(below, {"under": {"step": 2}}),
             "measures": EN("Scored on the bass you sang under your own harmony: roots and fifths, landing in the chord. Hear it together plays the tune, your second take and this one.")},
        ],
    }


course = {
    "id": "improvising-harmony", "version": 1, "reviewed": False, "title": EN("Improvising a harmony"),
    "units": [
        {"id": "imp-a-part-above", "title": EN("A part above"), "colour": 2,
         "lessons": [imp_1_third(), imp_1_switch(), imp_1_fourth(), imp_1_ear(), imp_1_challenge()]},
        {"id": "imp-below-and-holding", "title": EN("Below, and holding on"), "colour": 2,
         "lessons": [imp_2_below(), imp_2_hold(), imp_2_echo(), imp_2_challenge()]},
        {"id": "imp-any-chord-tone", "title": EN("Any chord tone"), "colour": 2,
         "lessons": [imp_3_chord(), imp_3_two_ways(), imp_3_challenge()]},
        {"id": "imp-no-lights", "title": EN("No lights"), "colour": 2,
         "lessons": [imp_4_hints(), imp_4_free(), imp_4_high(), imp_4_challenge()]},
    ],
}
def hold_or_nearest(notes):
    """The line a singer makes doing what a close step asks: hold where the held note is still lit,
    else the nearest lit note."""
    line = []
    for n in notes:
        choices = n.get("choices") or [n["step"]]
        line.append(line[-1] if line and line[-1] in choices else min(choices, key=lambda c: (abs(c - line[-1]) if line else abs(c), c)))
    return line


for unit in course["units"]:
    for lesson in unit["lessons"]:
        for step in lesson["steps"]:
            ex = step.get("exercise") or {}
            if ex.get("rules") != "close":
                continue
            line = hold_or_nearest([n for n in ex["notes"] if not n.get("listenOnly")])
            moves = [abs(b - a) for a, b in zip(line, line[1:])]
            close, moving = sum(m <= 4 for m in moves), sum(m > 0 for m in moves)
            assert close >= 0.8 * len(moves) and moving >= 0.3 * len(moves), f"{lesson['id']}: a singer holding or taking the nearest note can't keep 'close' ({close}/{len(moves)} close, {moving} moving)"

# Every choose step says what it scored (the house pattern).
for unit in course["units"]:
    for lesson in unit["lessons"]:
        for step in lesson["steps"]:
            if step["kind"] == "choose":
                step.setdefault("measures", EN("Scored on the rounds you got right first time."))

# Each "Did you know?" goes into its lesson's fact, the lesson end's card (tools/facts.py).
sys.path.insert(0, str(Path(__file__).resolve().parent))
from facts import move_facts  # noqa: E402
move_facts(course)
json.dump(course, open(OUT, "w"))
if FALLBACKS:
    print("rests where nothing fits:", len(FALLBACKS))
