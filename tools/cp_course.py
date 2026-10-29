"""Builds course/plus/counterpoint/course.json, the Counterpoint course. Steps are semitones from the
learner's comfortable note. The course file is generated: fix this script, then regenerate, never the
JSON by hand (it would be overwritten).

    python3 -I tools/cp_course.py && python3 -I tools/coursefmt.py course/plus/counterpoint/course.json
"""
import json
import sys

from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "course/plus/counterpoint/course.json"
OCOME_TEMPLATE = REPO / "templates/library/o-come-all-ye-faithful.json"
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


def notes(seq, start=0, shift=0, lyrics=None):
    """(length, step) pairs, or (length, step, lyric), from `start`, every step moved by `shift`."""
    out, beat = [], start
    for item in seq:
        length, step = item[0], item[1]
        n = {"beat": beat, "length": length, "step": step + shift}
        if len(item) > 2 and item[2]:
            n["lyric"] = item[2]
        out.append(n)
        beat += length
    return out


# ---- The tunes, do = 0 ----

# Row, Row, Row Your Boat in 6/8, a beat to an eighth (tempo 150 is a dotted quarter at 50).
ROW = [
    (3, 0, "Row,"), (3, 0, "row,"),
    (2, 0, "row"), (1, 2, "your"), (3, 4, "boat"),
    (2, 4, "gent-"), (1, 2, "ly"), (2, 4, "down"), (1, 5, "the"),
    (6, 7, "stream."),
    (1, 12, "Mer-"), (1, 12, "ri-"), (1, 12, "ly,"), (1, 7, "mer-"), (1, 7, "ri-"), (1, 7, "ly,"),
    (1, 4, "mer-"), (1, 4, "ri-"), (1, 4, "ly,"), (1, 0, "mer-"), (1, 0, "ri-"), (1, 0, "ly,"),
    (2, 7, "life"), (1, 5, "is"), (2, 4, "but"), (1, 2, "a"),
    (6, 0, "dream."),
]
assert sum(n[0] for n in ROW) == 48
ROW_DO, BAR68 = -7, 6

# Ode to Joy's opening (Beethoven, 1824), in quarters.
ODE = [(1, 4), (1, 4), (1, 5), (1, 7), (1, 7), (1, 5), (1, 4), (1, 2), (1, 0), (1, 0), (1, 2), (1, 4), (1.5, 4), (0.5, 2), (2, 2)]
assert sum(n[0] for n in ODE) == 16
# Its second phrase, which comes home: ... mi, re, re do do.
ODE_HOME = ODE[:12] + [(1.5, 2), (0.5, 0), (2, 0)]

# ---- Unit 1: Hold your own ----

def cp_1_round():
    listen = {"tempo": 150, "notes": notes(ROW, BAR68, ROW_DO), "turn": False, "drone": {"step": ROW_DO}}
    tryit = {"tempo": 150, "notes": notes(ROW[10:], 0, ROW_DO), "drone": {"step": ROW_DO}}
    play = {"tempo": 150, "notes": notes(ROW * 2, BAR68, ROW_DO), "turn": False, "drone": {"step": ROW_DO}, "generous": True,
            "with": [{"delay": 2 * BAR68, "steps": 12}, {"delay": 4 * BAR68}, {"delay": 6 * BAR68, "steps": -12}]}
    return {
        "id": "cp-1-round", "title": EN("Be a round"), "strictness": "relaxed",
        "steps": [
            learn("A round is one tune that fits itself when it starts at different times. You start it.",
                  [("Sing Row, Row, Row", "Twice through, at an easy volume"),
                   ("Three voices join you", "Two bars apart. Listen to them: never sing louder to hear yourself"),
                   ("Best with headphones", "And stop if anything tightens or hurts")], "round", listen),
            {"kind": "try", "text": EN("The quick half, \"merrily\" to \"dream\", at your own pace."), "exercise": tryit},
            {"kind": "play", "text": EN("After a bar of the drone, sing it twice through. Keep your own line while the voices come in."),
             "exercise": play,
             "measures": EN("Scored on your notes on pitch. Did you know? Row, Row, Row Your Boat was in print by 1852, though its early tune differs from today's.")},
        ],
    }


def two(high, low, tempo=80):
    """A clip of two voices at once: (length, step) lines from beat 0."""
    return {"notes": notes(high) + notes(low)}


def cp_1_hear():
    held = lambda step, beats=4: [(beats, step)]
    which = [EN("The high one"), EN("The low one"), EN("Both moved")]
    rounds = [
        {"prompt": EN("Which voice held still?"), "clips": [two([(1, 7), (1, 5), (1, 4), (1, 2)], held(-5))], "options": which, "answer": 1,
         "why": EN("The low voice held one note, like a drone, while the high one stepped down.")},
        {"prompt": EN("Which voice held still?"), "clips": [two(held(4), [(1, -5), (1, -3), (1, -1), (1, 0)])], "options": which, "answer": 0,
         "why": EN("The high voice stayed on one note while the low one climbed underneath.")},
        {"prompt": EN("Which voice held still?"), "clips": [two([(1, 4), (1, 5), (1, 7), (1, 9)], [(1, 0), (1, -1), (1, -3), (1, -5)])], "options": which, "answer": 2,
         "why": EN("Neither held: the high voice climbed while the low one fell. Two lines moving at once.")},
        {"prompt": EN("Which voice held still?"), "clips": [two([(1, 4), (1, 5), (1, 7), (1, 9)], held(0))], "options": which, "answer": 1,
         "why": EN("The low voice held do while the high one climbed away from it.")},
        {"prompt": EN("Same tune, or a different one?"),
         "clips": [{"notes": notes([(1, 0), (1, 2), (1, 4), (1, 0)] * 2) + notes([(2, -5), (2, -3), (2, -5), (2, -8)])}],
         "options": [EN("The same tune"), EN("Different tunes")], "answer": 1,
         "why": EN("The low voice sang its own, slower line. Two different tunes that fit: that's counterpoint.")},
        {"prompt": EN("Same tune, or a different one?"),
         "clips": [{"notes": notes([(1, 0), (1, 2), (1, 4), (1, 0)] * 2) + notes([(1, 0), (1, 2), (1, 4), (1, 0)] * 2, start=2, shift=-12)}],
         "options": [EN("The same tune"), EN("Different tunes")], "answer": 0,
         "why": EN("The low voice sang the same tune two beats later: a little round.")},
    ]
    return {
        "id": "cp-1-hear", "title": EN("Which voice moved?"),
        "steps": [
            learn("Your ear can follow two voices at once. Listen for which one moves.",
                  [("Two voices", "One high, one low, at the same time"),
                   ("Which one moves?", "One may hold, both may move, or sing their own tune"),
                   ("Hear it as often as you like", "Then choose")], "harmony"),
            {"kind": "choose", "text": EN("Listen to each, as often as you like, then choose."),
             "exercise": {"tempo": 80, "rounds": rounds},
             "measures": EN("Scored on the rounds you got right first time.")},
        ],
    }


def cp_1_pedal():
    def pedal(step):
        """A cue, then four holds of `step`, each 3.5 beats with half a beat to breathe, under Ode to Joy."""
        cue = [{"beat": 0, "length": 2, "step": step, "listenOnly": True}]
        holds = [{"beat": 2 + 4 * k, "length": 3.5, "step": step, "lyric": "oo"} for k in range(4)]
        return {"tempo": 72, "notes": cue + holds, "turn": False, "score": "holds",
                "with": [{"notes": notes(ODE_HOME, start=2, shift=0)}]}
    return {
        "id": "cp-1-pedal", "title": EN("Be the drone"),
        "steps": [
            learn("A note held under a moving tune is a pedal, after the organ's pedals, which hold a low note as long as it's pressed.",
                  [("Hold one note", "Do, on \"oo\", easy and steady"),
                   ("The tune moves above", "Ode to Joy, leaning on your note"),
                   ("Breathe between", "Four holds of three and a half beats, a quick breath each time")], "drone",
                  {"tempo": 72, "notes": [{"beat": 0, "length": 16, "step": 0, "lyric": "oo"}] + notes(ODE_HOME), "turn": False}),
            {"kind": "try", "text": EN("Find your do, and your so below it."), "exercise": {"tempo": 72, "notes": [{"beat": 0, "length": 2, "step": 0, "lyric": "oo"}, {"beat": 2, "length": 2, "step": -5, "lyric": "oo"}]}},
            {"kind": "play", "text": EN("The guide gives you do. Hold it four times while the tune moves above you."),
             "exercise": pedal(0)},
            {"kind": "play", "text": EN("Now be the floor on so, below your do. The same tune, a new pedal."),
             "exercise": pedal(-5),
             "measures": EN("Scored on how long and how steadily you held your note while the tune moved.")},
        ],
    }


# Shchedryk's four-note motif in the minor key: 3-2-3-1, here do ti do la, in 3/4.
MOTIF = [(1, 0), (0.5, -1), (0.5, 0), (1, -3)]


def cp_1_ostinato():
    cue = [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}]
    pattern = notes(MOTIF * 8, start=3) + [{"beat": 27, "length": 3, "step": -3}]
    above = notes([(6, 9), (6, 7), (6, 5), (6, 4), (6, 4)])  # an original line falling slowly over the pattern
    return {
        "id": "cp-1-ostinato", "title": EN("A pattern that repeats"),
        "steps": [
            learn("A pattern sung over and over is an ostinato. Once you know it, it keeps itself going.",
                  [("Four notes", "Do ti do la: a darker colour you'll meet properly in unit 2"),
                   ("Over and over", "Eight times through"),
                   ("A line falls above it", "Let it pass; keep your pattern")], "echo",
                  {"tempo": 84, "notes": notes(MOTIF * 4, start=3), "turn": False, "with": [{"notes": notes([(6, 9), (6, 7)])}]}),
            {"kind": "try", "text": EN("The pattern, at your own pace."), "exercise": {"tempo": 84, "notes": notes(MOTIF)}},
            {"kind": "play", "text": EN("The guide gives you do. After a bar, sing the pattern eight times under the line, then hold the last note."),
             "exercise": {"tempo": 84, "notes": cue + pattern, "turn": False, "with": [{"notes": above}]},
             "measures": EN("Scored on your pattern's notes on pitch while the other line moved.")},
        ],
    }


def cp_1_challenge():
    cue = [{"beat": 0, "length": 3, "step": ROW_DO, "listenOnly": True}]
    floor = [{"beat": BAR68 + 3 * k, "length": 3, "step": ROW_DO if k % 2 == 0 else ROW_DO + 7, "lyric": "doo" if k % 2 == 0 else "bm"} for k in range(8)]
    hold = [{"beat": BAR68 + 24, "length": 11, "step": ROW_DO, "lyric": "oo"}, {"beat": BAR68 + 36, "length": 11, "step": ROW_DO, "lyric": "oo"}]
    return {
        "id": "cp-1-challenge", "title": EN("Hold the floor"), "challenge": True,
        "steps": [
            learn("Under a whole tune: a pattern first, then one long note.",
                  [("Do and so", "Two notes a bar, under the first half"),
                   ("Then hold do", "A pedal from \"merrily\" to the end, with one breath"),
                   ("Listen up", "Could you still hear the tune?")], "bass"),
            {"kind": "play", "text": EN("After a bar, sing do and so under the tune, then hold do to the end, with one quick breath."),
             "exercise": {"tempo": 150, "notes": cue + floor + hold, "turn": False,
                          "with": [{"notes": notes(ROW, start=BAR68, shift=ROW_DO + 12)}]},
             "measures": EN("Scored on your notes on pitch, the long ones too. Could you still hear the tune while you held the floor?")},
        ],
    }


# ---- Unit 2: Rounds and canons ----

# Are You Sleeping (traditional), in quarters, do = 0; and in minor, as Mahler set it in his First Symphony.
AYS = [(1, 0, "Are"), (1, 2, "you"), (1, 4, "sleep-"), (1, 0, "ing,"), (1, 0, "are"), (1, 2, "you"), (1, 4, "sleep-"), (1, 0, "ing,"),
       (1, 4, "Broth-"), (1, 5, "er"), (2, 7, "John?"), (1, 4, "Broth-"), (1, 5, "er"), (2, 7, "John?"),
       (0.5, 7, "Morn-"), (0.5, 9, "ing"), (0.5, 7, "bells"), (0.5, 5, "are"), (1, 4, "ring-"), (1, 0, "ing,"),
       (0.5, 7, "morn-"), (0.5, 9, "ing"), (0.5, 7, "bells"), (0.5, 5, "are"), (1, 4, "ring-"), (1, 0, "ing,"),
       (1, 0, "ding,"), (1, -5, "dang,"), (2, 0, "dong,"), (1, 0, "ding,"), (1, -5, "dang,"), (2, 0, "dong.")]
assert sum(n[0] for n in AYS) == 32
MINOR = {4: 3, 9: 8}  # mi and la a half step lower
AYS_MINOR = [(n[0], MINOR.get(n[1], n[1]), n[2]) for n in AYS]
AYS_DO = -4  # its span, -5 to +9, sits within -9 and +5


def until(line, end):
    """A line cut off at beat `end` (a round's voices stop when you do)."""
    return [n for n in line if n["beat"] < end]


def cp_2_follow():
    tune = notes(AYS, 0, AYS_DO)
    return {
        "id": "cp-2-follow", "title": EN("The second voice"),
        "steps": [
            learn("Now you come in second. The leader is already singing other notes when you start.",
                  [("Listen to the leader", "Are You Sleeping, from the top"),
                   ("Come in after two bars", "On \"Are you sleeping\""),
                   ("Keep your own tune", "Listen to both, never louder")], "round",
                  {"tempo": 100, "notes": tune, "turn": False, "with": [{"delay": 8, "steps": -12}]}),
            {"kind": "try", "text": EN("Your first two bars, at your own pace."), "exercise": {"tempo": 100, "notes": notes(AYS[:8], 0, AYS_DO)}},
            {"kind": "play", "text": EN("The guide leads. Come in two bars later and sing it through."),
             "exercise": {"tempo": 100, "notes": notes(AYS, 8, AYS_DO), "turn": False,
                          "with": [{"notes": until(notes(AYS * 2, 0, AYS_DO + 12), 40)}]},
             "measures": EN("Scored on your notes on pitch while the leader sang other notes.")},
        ],
    }


def cp_2_minor():
    return {
        "id": "cp-2-minor", "title": EN("A round in minor"),
        "steps": [
            learn("This tune in minor: its mi and la a half step lower (the smallest step on a piano), and it sounds darker.",
                  [("Listen to the minor tune", "The same shape, a darker colour"),
                   ("You're the third voice", "Two are singing before you come in"),
                   ("Your mi is lower now", "Listen for it against the others")], "round",
                  {"tempo": 80, "notes": notes(AYS_MINOR, 0, AYS_DO), "turn": False}),
            {"kind": "try", "text": EN("The minor tune's first four bars, at your own pace."), "exercise": {"tempo": 80, "notes": notes(AYS_MINOR[:14], 0, AYS_DO)}},
            {"kind": "play", "text": EN("Two voices start. Come in third, four bars in, and sing it through."),
             "exercise": {"tempo": 80, "notes": notes(AYS_MINOR, 16, AYS_DO), "turn": False,
                          "with": [{"notes": until(notes(AYS_MINOR * 2, 0, AYS_DO + 12), 48)},
                                   {"notes": until(notes(AYS_MINOR * 2, 8, AYS_DO), 48)}]},
             "measures": EN("Scored on your notes on pitch, in minor, with two voices already going.")},
        ],
    }


# An original canon at the octave, a bar behind (written for Stackapella): do re do la, so ti la do,
# re mi fa mi, fa mi re do. Against the follower an octave lower, every strong beat is consonant,
# the one weak fourth a passing step, and no fifths or octaves run in parallel.
CANON = [(1, 0), (1, 2), (1, 0), (1, -3), (1, -5), (1, -1), (1, -3), (1, 0), (1, 2), (1, 4), (1, 5), (1, 4), (1, 5), (1, 4), (1, 2), (1, 0)]
# The leader's last bar, over the follower's fa mi re do: la so ti do (a third, a third, a sixth, an
# octave above them), a cadence instead of a held do that would make a seventh over re.
CODA = [(1, -3), (1, -5), (1, -1), (1, 0)]


def cp_2_canon():
    cue = [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}]
    lead = notes(CANON + CODA, 4)
    return {
        "id": "cp-2-canon", "title": EN("Lead, then follow"),
        "steps": [
            learn("A round is a canon that loops back to the start. A canon can begin at any distance or pitch: here, a bar behind and an octave away.",
                  [("First you lead", "The guide follows a bar later, an octave down"),
                   ("Then you follow", "The guide leads, an octave up"),
                   ("Same line, both times", "Do re do la, so ti la do...")], "round",
                  {"tempo": 72, "notes": notes(CANON + CODA), "turn": False, "with": [{"notes": notes(CANON, 4, -12)}]}),
            {"kind": "try", "text": EN("The canon's line, at your own pace."), "exercise": {"tempo": 72, "notes": notes(CANON)}},
            {"kind": "play", "text": EN("You lead. After the guide's do, sing the line, then la so ti do while the follower finishes."),
             "exercise": {"tempo": 72, "notes": cue + lead, "turn": False, "with": [{"notes": notes(CANON, 8, -12)}]}},
            {"kind": "play", "text": EN("Now you follow. The guide leads an octave up; come in a bar later."),
             "exercise": {"tempo": 72, "notes": notes(CANON, 4), "turn": False,
                          "with": [{"notes": notes(CANON + CODA, 0, 12)}]},
             "measures": EN("Scored on your notes on pitch as the follower, a bar behind the leader. Did you know? Pachelbel's Canon is a true canon: three violins two bars apart, over a bass that repeats.")},
        ],
    }


def cp_2_challenge():
    """In the middle of a four-voice round, then the floor under it: unit 1's pattern, in the round's own ding dang dong."""
    def clip(n):
        """n voices of the round, a bar apart, all still singing at the end."""
        out = []
        for k in range(n):
            out += until(notes(AYS, 4 * k, AYS_DO + (12 if k % 2 == 0 else 0)), 4 * (n - 1) + 8)
        return {"notes": [{"beat": x["beat"], "length": x["length"], "step": x["step"]} for x in out]}
    count = [EN("Two"), EN("Three"), EN("Four")]
    rounds = [
        {"prompt": EN("How many voices are singing by the end?"), "clips": [clip(3)], "options": count, "answer": 1,
         "why": EN("Three: each came in a bar after the one before.")},
        {"prompt": EN("How many voices are singing by the end?"), "clips": [clip(2)], "options": count, "answer": 0,
         "why": EN("Two: a leader and one follower.")},
        {"prompt": EN("How many voices are singing by the end?"), "clips": [clip(4)], "options": count, "answer": 2,
         "why": EN("Four: with entries two bars apart, every seat is filled. The oldest known round, Sumer is icumen in (about 1250), has four voices over two more.")},
    ]
    ding = [(1, 0, "ding,"), (1, -5, "dang,"), (2, 0, "dong,")]
    floor = notes(ding * 4, 48, AYS_DO)
    others = [{"notes": until(notes(AYS * 2, 0, AYS_DO + 12), 64), "volume": 0.35},
              {"notes": until(notes(AYS * 2, 8, AYS_DO - 12), 64), "volume": 0.35},
              {"notes": until(notes(AYS * 2, 24, AYS_DO - 12), 64), "volume": 0.35}]
    return {
        "id": "cp-2-challenge", "title": EN("In the middle"), "challenge": True,
        "steps": [
            learn("The hardest seat in a round: two voices are already singing when you start, and one more comes in after you. Then you become the floor.",
                  [("Voice 3 of 4", "Come in four bars in"),
                   ("Then the floor", "\"Ding, dang, dong\", over and over, like unit 1's pattern"),
                   ("Your own line", "Listen to them all, never louder")], "round"),
            {"kind": "choose", "text": EN("First, ears only: count the voices."), "exercise": {"tempo": 100, "rounds": rounds}},
            {"kind": "play", "text": EN("Come in third and sing it through, then keep \"ding, dang, dong\" going under the others."),
             "exercise": {"tempo": 100, "notes": notes(AYS, 16, AYS_DO) + floor, "turn": False, "with": others},
             "measures": EN("Scored on your notes on pitch, in the middle and then as the floor. Could you still hear the others while you sang?")},
        ],
    }


# ---- Unit 3: Two lines, one song ----

# O Come, All Ye Faithful (tune attributed to John Francis Wade, c. 1743), its first two lines and
# chords from the app's own template (server/database/templates/o-come-all-ye-faithful.json).
_OC = json.load(open(OCOME_TEMPLATE))
_OC_KEY = 7  # G
OCOME = [(n["length"], n["pitch"] - 67, n.get("lyric")) for n in [p for p in _OC["parts"] if p["key"] == "soprano"][0]["guide"]["notes"] if n["beat"] < 33]
OCOME_CHORDS = [(c["beat"], (c["root"] - _OC_KEY) % 12, c["quality"]) for c in _OC["chords"] if c["beat"] < 33]
assert sum(n[0] for n in OCOME) == 32
# An original descant (steps from the tune's do), written against those chords: every note a chord
# tone, consonant with the tune, ending on do' over I after a breath. "Come ye" takes la over the tune's
# do (a sixth, in contrary motion), never ti to do an octave above the tune's ti to do.
DESCANT_1 = [(1, 7, "Ah,"), (4, 12, "ah,"), (4, 11, "ah,"), (1, 12, "ah,"), (1, 11, "ah,"), (1, 12, "ah,"), (1, 9, "ah,"), (3, 7, "ah.")]
DESCANT_2 = [(1, 7, "Ah,"), (2, 9, "ah,"), (1, 11, "ah,"), (1, 12, "ah,"), (1, 11, "ah,"), (1, 9, "ah,"), (1, 11, "ah,"), (1, 12, "ah,"), (2, 7, "ah,"), (1.5, 9, "ah,"), (3.5, 11, "ah.")]
assert sum(n[0] for n in DESCANT_1) == 16 and sum(n[0] for n in DESCANT_2) == 16


def oc_chords(do, start=0, until=34):
    return [{"beat": b + start, "root": (r + do) % 12, "quality": q, "bass": None} for b, r, q in OCOME_CHORDS if b < until] + \
        ([{"beat": 33 + start, "root": do % 12, "quality": "maj", "bass": None}] if until > 33 else [])


def cp_3_call():
    pairs = [
        ([(1, 0, "do"), (1, 2, "re"), (2, 4, "mi")], [(1, 4, "mi"), (1, 2, "re"), (2, 0, "do")]),
        ([(1, 7, "so"), (1, 9, "la"), (1, 7, "so"), (1, 2, "re")], [(1, 2, "re"), (1, 4, "mi"), (1, 2, "re"), (1, 0, "do")]),
        ([(1, 0, "do"), (1, 4, "mi"), (1, 7, "so"), (1, 5, "fa")], [(1, 4, "mi"), (1, 2, "re"), (1, -1, "ti"), (1, 0, "do")]),
        ([(1, 4, "mi"), (1, 5, "fa"), (1, 7, "so"), (1, 9, "la")], [(1, 5, "fa"), (1, 4, "mi"), (1, 2, "re"), (1, 0, "do")]),
    ]
    first_call, first_answer = pairs[0]
    alternating, beat = [], 0
    for call, answer in pairs:
        alternating += [dict(n, listenOnly=True) for n in notes(call, beat)]
        alternating += notes(answer, beat + 5)
        beat += 10
    return {
        "id": "cp-3-call", "title": EN("Call and response"),
        "steps": [
            learn("In call and response, a leader sings and others answer. Here the call ends away from do, and the answer brings it home.",
                  [("The guide calls", "A short phrase, ending away from do"),
                   ("You answer", "A different phrase, landing on do"),
                   ("Rooted in West African singing", "Then work songs, spirituals, gospel and blues")], "echo",
                  {"tempo": 90, "notes": notes(first_call) + notes(first_answer, 5), "turn": False}),
            {"kind": "play", "text": EN("Hear the call, then sing the answer: mi re do."),
             "exercise": {"tempo": 90, "notes": notes(first_call), "answer": notes(first_answer), "turn": True}},
            {"kind": "play", "text": EN("Four calls, each with its answer. Sing each answer right after its call."),
             "exercise": {"tempo": 90, "notes": alternating, "turn": False},
             "measures": EN("Scored on your answers' notes on pitch.")},
        ],
    }


def cp_3_counter():
    cue = [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}]
    line = [{"beat": 4 + 4 * k, "length": 3.5, "step": step, "lyric": "oo"} for k, step in enumerate([0, -1, -3, -5])]
    return {
        "id": "cp-3-counter", "title": EN("A slow line under a tune"),
        "steps": [
            learn("Your line keeps falling while the tune turns, so the two never move the same way for long.",
                  [("Four long notes", "Do, ti, la, so"),
                   ("Ode to Joy above", "Its notes move four times faster"),
                   ("A third or a sixth", "Where each of your notes begins")], "harmony",
                  {"tempo": 72, "notes": line, "turn": False, "with": [{"notes": notes(ODE, start=4)}]}),
            {"kind": "try", "text": EN("Your four notes, at your own pace."), "exercise": {"tempo": 72, "notes": notes([(1, 0), (1, -1), (1, -3), (1, -5)])}},
            {"kind": "play", "text": EN("The guide gives you do. Then sing your slow line under Ode to Joy."),
             "exercise": {"tempo": 72, "notes": cue + line, "turn": False, "with": [{"notes": notes(ODE, start=4)}]},
             "measures": EN("Scored on your slow line's notes on pitch while the tune moved above.")},
        ],
    }


OCOME_DO = -7  # the tune under the descant, which sits from 0 to +5
OCOME_TUNE_DO = -2  # the tune itself, -5 to +5, becomes -7 to +3


def cp_3_descant():
    return {
        "id": "cp-3-descant", "title": EN("Float above it"),
        "steps": [
            learn("A descant floats above the tune, often in longer notes, so the tune still comes through. Choirs usually save one for a late verse.",
                  [("The tune below", "O Come, All Ye Faithful, with its chords"),
                   ("Your line above", "Long notes on \"ah\""),
                   ("Light, never loud", "Let the tune be heard through you")], "phrase",
                  {"tempo": 80, "notes": notes(DESCANT_1, 0, OCOME_DO), "turn": False, "with": [{"notes": notes(OCOME[:12], 0, OCOME_DO)}], "chords": oc_chords(OCOME_DO, 0, 16)}),
            {"kind": "try", "text": EN("The descant, at your own pace."), "exercise": {"tempo": 80, "notes": notes(DESCANT_1, 0, OCOME_DO)}},
            {"kind": "play", "text": EN("After a bar, sing the descant over the tune and its chords."),
             "exercise": {"tempo": 80, "notes": [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}] + notes(DESCANT_1, 4, OCOME_DO), "turn": False,
                          "with": [{"notes": notes(OCOME[:12], 4, OCOME_DO)}], "chords": oc_chords(OCOME_DO, 4, 16)},
             "measures": EN("Scored on the descant's notes on pitch over the tune. Did you know? The best-known descant to this carol, by David Willcocks, appeared in 1961, over the \"Sing, choirs of angels\" verse.")},
        ],
    }


# Are You Sleeping swung in 12/8, so it fits against Row, Row bar for bar: a quarter becomes three
# eighths and each pair of eighths a long and a short.
def _swing(seq):
    out, first = [], True
    for length, step, lyric in seq:
        if length == 0.5:
            out.append((2 if first else 1, step, lyric))
            first = not first
        else:
            out.append((int(length * 3), step, lyric))
            first = True
    return out


AYS_SWUNG = _swing(AYS)
assert sum(n[0] for n in AYS_SWUNG) == 96


def cp_3_partners():
    return {
        "id": "cp-3-partners", "title": EN("Two songs at once"),
        "steps": [
            learn("Songs on the same chords, in the same time, often fit together. Singing two at once is a quodlibet, Latin for \"whatever you please\".",
                  [("Row, Row, Row is yours", "Twice through"),
                   ("Are You Sleeping above", "Swung, so its bars line up with yours"),
                   ("Two tunes, one chord", "Both rest on do")], "harmony",
                  {"tempo": 150, "notes": notes(ROW * 2, 0, ROW_DO), "turn": False, "with": [{"notes": notes(AYS_SWUNG, 0, ROW_DO + 12)}]}),
            {"kind": "play", "text": EN("After a bar of the drone, sing Row, Row, Row twice through while the guide sings Are You Sleeping."),
             "exercise": {"tempo": 150, "notes": notes(ROW * 2, BAR68, ROW_DO), "turn": False, "drone": {"step": ROW_DO},
                          "with": [{"notes": notes(AYS_SWUNG, BAR68, ROW_DO + 12)}]},
             "measures": EN("Scored on your notes on pitch while a different song went on above you. Did you know? Bach titled the last of his Goldberg Variations, published in 1741, \"Quodlibet\".")},
        ],
    }


def cp_3_challenge():
    tune = notes(OCOME, 4, OCOME_TUNE_DO)
    descant_over_tune = notes(DESCANT_1 + DESCANT_2, 4, OCOME_TUNE_DO)
    last = notes(DESCANT_1 + DESCANT_2, 4, OCOME_DO) + [{"beat": 37, "length": 4, "step": 12 + OCOME_DO, "lyric": "ah."}]
    return {
        "id": "cp-3-challenge", "title": EN("The last verse"), "challenge": True,
        "steps": [
            learn("Two verses, two parts: the tune first, with a descant over you; then the descant yourself, over the tune.",
                  [("Verse one", "The tune, the guide's descant above"),
                   ("The last verse", "Your descant, two lines long"),
                   ("Hold the end", "Your last note rings over the home chord")], "phrase"),
            {"kind": "play", "text": EN("Verse one: sing the tune while the guide sings a descant above you."),
             "exercise": {"tempo": 80, "notes": [{"beat": 0, "length": 2, "step": OCOME_TUNE_DO, "listenOnly": True}] + tune, "turn": False,
                          "with": [{"notes": descant_over_tune}], "chords": oc_chords(OCOME_TUNE_DO, 4, 33)}},
            {"kind": "play", "text": EN("The last verse: your descant over the tune, two lines, and hold the last note."),
             "exercise": {"tempo": 80, "notes": [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}] + last, "turn": False,
                          "with": [{"notes": notes(OCOME, 4, OCOME_DO) + [{"beat": 37, "length": 4, "step": OCOME_DO}]}], "chords": oc_chords(OCOME_DO, 4)},
             "measures": EN("Scored on the descant's notes on pitch, the last long one too. Could you hear the tune under you?")},
        ],
    }


# ---- Unit 4: Note against note ----

# The cantus firmi are original, written for Stackapella, an octave below the learner.
CANTUS_1 = [-12, -10, -7, -8, -5, -7, -8, -10, -12]  # do re fa mi so fa mi re do
CANTUS_2 = [-12, -7, -8, -10, -5, -7, -8, -10, -12]  # do fa mi re so fa mi re do
CANTUS_3 = [-12, -10, -7, -8, -3, -5, -8, -7, -10, -12]  # do re fa mi la so mi fa re do
FIRST_1 = [0, -1, -3, 0, -1, 2, 0, -1, 0]  # checked: P8 M6 M3 m6 M3 M6 m6 M6 P8, six moves contrary
FIRST_2 = [0, -3, 0, 2, -1, 2, 0, -1, 0]  # checked: P8 M3 m6 P8 M3 M6 m6 M6 P8, six moves contrary
SECOND_1 = [-5, -3, -1, 0, 2, -3, -5, -3, -1, 0, 2, -3, 0, -5, -3, -1, 0]  # strong, weak, over each cantus note


def cantus(steps, start, beats=2):
    return [{"beat": start + beats * k, "length": beats, "step": s} for k, s in enumerate(steps)]


def line(steps, start, beats=2, lyric="ah"):
    return [{"beat": start + beats * k, "length": beats, "step": s, "lyric": lyric} for k, s in enumerate(steps)]


CUE = [{"beat": 0, "length": 2, "step": 0, "listenOnly": True}]


def cp_4_consonance():
    drone = {"step": -12}
    sung = [(2, -8), (2, -5), (2, -3), (2, 0), (2, 2), (2, 0), (2, -7), (2, -8)]
    return {
        "id": "cp-4-consonance", "title": EN("Smooth and rubbing"),
        "steps": [
            learn("Some notes sound smooth together, some rub. In this style unisons, thirds, fifths, sixths and octaves are smooth; seconds, fourths and sevenths rub, and a rub wants to move.",
                  [("A third", "Do to mi: skip one note"),
                   ("A fifth, a sixth, an octave", "Do to so, to la, to do"),
                   ("A rub", "Re over do, or fa: it leans, then steps home")], "drone",
                  {"tempo": 60, "notes": notes(sung), "turn": False, "drone": drone}),
            {"kind": "choose", "text": EN("Over the drone: smooth or rubbing?"), "exercise": {"tempo": 60, "rounds": [
                {"prompt": EN("Smooth or rubbing?"), "clips": [{"notes": [{"beat": 0, "length": 3, "step": s}], "drone": drone}], "options": [EN("Smooth"), EN("Rubbing")], "answer": a, "why": EN(w)}
                for s, a, w in [(-8, 0, "Mi over do, a third: smooth."), (2, 1, "Re over do, a ninth: it rubs and wants to step down."), (-5, 0, "So over do, a fifth: smooth and open."),
                                (-1, 1, "Ti over do, a seventh: it rubs and wants to rise to do."), (-3, 0, "La over do, a sixth: smooth."), (-7, 1, "Fa over do, a fourth: in this style it rubs, and steps down to mi.")]]}},
            {"kind": "try", "text": EN("The notes over the low drone, at your own pace."), "exercise": {"tempo": 60, "notes": notes(sung), "drone": drone}},
            {"kind": "play", "text": EN("Over a low do, sing a third, a fifth, a sixth and an octave; then re, rubbing, step home; then fa, rubbing, step to mi."),
             "exercise": {"tempo": 60, "notes": notes(sung, 2), "turn": False, "drone": drone},
             "measures": EN("Scored on each interval on pitch over the drone, the rubs too. Did you know? In 1863 Hermann von Helmholtz explained a rub as beating: overtones close in pitch wobbling against each other.")},
        ],
    }


def cp_4_motion():
    def pair(upper, lower):
        return {"notes": notes([(1, u) for u in upper]) + notes([(1, l) for l in lower])}
    opts = [EN("The same way"), EN("Opposite ways"), EN("One held")]
    rounds = [
        {"prompt": EN("How did the two voices move?"), "clips": [pair([4, 5, 7], [-12, -10, -8])], "options": opts, "answer": 0,
         "why": EN("Both climbed together: similar motion. When they keep the same distance, it's parallel.")},
        {"prompt": EN("How did the two voices move?"), "clips": [pair([7, 5, 4], [-12, -10, -8])], "options": opts, "answer": 1,
         "why": EN("One climbed while the other fell: contrary motion, the surest way to sound like two voices.")},
        {"prompt": EN("How did the two voices move?"), "clips": [pair([4, 4, 4], [-12, -10, -8])], "options": opts, "answer": 2,
         "why": EN("The top held while the bottom climbed: oblique motion.")},
        {"prompt": EN("How did the two voices move?"), "clips": [pair([0, 2, 4], [-8, -10, -12])], "options": opts, "answer": 1,
         "why": EN("Up against down again: contrary motion.")},
        {"prompt": EN("Which one moves in fifths?"),
         "clips": [pair([7, 9, 11, 12], [0, 2, 4, 5]), pair([4, 5, 7, 9], [0, 2, 4, 5])], "answer": 0,
         "why": EN("A moves in fifths: the two voices fuse into one hollow sound, B's thirds keep them two.")},
        {"prompt": EN("Which one moves in fifths?"),
         "clips": [pair([9, 11, 12, 11], [0, 2, 4, 2]), pair([7, 9, 11, 9], [0, 2, 4, 2])], "answer": 1,
         "why": EN("B moves in fifths and sounds bare. A moves in sixths, sweet and full. That's why counterpoint avoids parallel fifths.")},
    ]
    return {
        "id": "cp-4-motion", "title": EN("Ways to move"),
        "steps": [
            learn("Two voices can move the same way, opposite ways, or one can hold while the other moves. Opposite ways keeps them most independent.",
                  [("Similar", "The same way (parallel, if the distance stays)"),
                   ("Contrary", "Opposite ways"),
                   ("Oblique", "One holds, one moves")], "harmony"),
            {"kind": "choose", "text": EN("Listen, then choose how the voices moved."), "exercise": {"tempo": 80, "rounds": rounds}},
            {"kind": "play", "text": EN("Eight notes against the guide: opposite ways, then one held, then together in sixths, then home."),
             "exercise": {"tempo": 60, "notes": CUE + line([4, 2, 0, 4, 5, 4, 2, 0], 4, 2, "ah"), "turn": False, "with": [{"notes": cantus([12, 14, 16, 16, 14, 12, 11, 12], 4)}]},
             "measures": EN("Scored on your line on pitch. It moved opposite ways four times, once against a held note, and twice in parallel sixths.")},
        ],
    }


def cp_4_first():
    return {
        "id": "cp-4-first", "title": EN("First species"),
        "steps": [
            learn("In 1725 Johann Joseph Fux taught counterpoint in steps he called species. The first is note against note: one of your notes to each note of a cantus, a slow, fixed tune.",
                  [("Begin and end on a perfect interval", "Here an octave"),
                   ("Only smooth intervals", "Thirds, fifths, sixths and octaves"),
                   ("Mostly by step, against the cantus", "Opposite ways as often as you can")], "harmony",
                  {"tempo": 60, "notes": line(FIRST_1, 0), "turn": False, "with": [{"notes": cantus(CANTUS_1, 0)}]}),
            {"kind": "try", "text": EN("Your line, at your own pace."), "exercise": {"tempo": 60, "notes": line(FIRST_1, 0)}},
            {"kind": "play", "text": EN("After the guide's do, sing your line against the cantus."),
             "exercise": {"tempo": 60, "notes": CUE + line(FIRST_1, 4), "turn": False, "with": [{"notes": cantus(CANTUS_1, 4)}]},
             "measures": EN("Scored on your line's notes on pitch against the cantus. This line moves contrary six times of eight, with no parallel fifths or octaves. Did you know? Fux wrote his book as a dialogue: the teacher, Aloysius, stands for Palestrina, and the student, Josephus, for Fux himself.")},
        ],
    }


def cp_4_second():
    sung = [{"beat": 4 + k, "length": 1 if k < 16 else 2, "step": s, "lyric": "ah"} for k, s in enumerate(SECOND_1)]
    return {
        "id": "cp-4-second", "title": EN("Two against one"),
        "steps": [
            learn("Two notes to each cantus note. The first must sound smooth; the second may rub if it passes by step, in one direction, between smooth notes: a passing note.",
                  [("Strong beat", "A smooth interval"),
                   ("Weak beat", "Smooth, or a step passing through"),
                   ("The ending", "La, ti, do")], "harmony",
                  {"tempo": 66, "notes": [dict(n, beat=n["beat"] - 4) for n in sung], "turn": False, "with": [{"notes": cantus(CANTUS_1, 0)}]}),
            {"kind": "try", "text": EN("Your line, at your own pace."), "exercise": {"tempo": 66, "notes": [dict(n, beat=n["beat"] - 4) for n in sung]}},
            {"kind": "play", "text": EN("After the guide's do, sing two notes to each of the cantus's."),
             "exercise": {"tempo": 66, "notes": CUE + sung, "turn": False, "with": [{"notes": cantus(CANTUS_1, 4)}]},
             "measures": EN("Scored on your line's notes on pitch, the passing notes too.")},
        ],
    }


def cp_4_challenge():
    low = [c + 5 for c in CANTUS_2]  # the cantus, do at -7: -7 to 0
    high = [f + 5 for f in FIRST_2]  # its counterpoint, a sixth or so above you
    return {
        "id": "cp-4-challenge", "title": EN("Hold the cantus"), "challenge": True,
        "steps": [
            learn("Now you sing the cantus, and the guide sings the counterpoint close above you. Hold your slow line while the quicker-moving one pulls at your ear.",
                  [("You: the cantus", "Do fa mi re so fa mi re do"),
                   ("Above you", "Its counterpoint, a sixth or an octave up"),
                   ("Listen down to yourself", "Can you hear both lines as you sing?")], "harmony",
                  {"tempo": 60, "notes": line(low, 0), "turn": False, "with": [{"notes": line(high, 0)}]}),
            {"kind": "play", "text": EN("After the guide's do, sing the cantus while the guide sings the counterpoint above you."),
             "exercise": {"tempo": 60, "notes": [{"beat": 0, "length": 2, "step": -7, "listenOnly": True}] + line(low, 4), "turn": False, "with": [{"notes": line(high, 4)}]},
             "measures": EN("Scored on the cantus on pitch with the counterpoint close above. Could you hear both lines while you sang?")},
        ],
    }


# ---- Unit 5: Make your own ----

MAJOR = {0, 2, 4, 5, 7, 9, 11}
SMOOTH = {0, 3, 4, 7, 8, 9}


def choices_over(cantus_steps):
    """Every note in the key, in the learner's range (-9 to +5), smooth over each cantus note; a
    perfect start (do or so), and the cadence ti then do."""
    out = []
    last = len(cantus_steps) - 1
    for k, c in enumerate(cantus_steps):
        if k == 0:
            out.append([0, -5])
        elif k == last - 1:
            out.append([-1])
        elif k == last:
            out.append([0])
        else:
            ok = [s for s in range(-9, 6) if s % 12 in MAJOR and (s - c) % 12 in SMOOTH and s > c]
            ok = [s for s in ok if not any(o % 12 == s % 12 and o < s for o in ok)]  # one octave of each: octave folding can't tell them apart
            if k == last - 2:
                ok = [s for s in ok if abs(s + 1) <= 5 and abs(s + 1) != 6]  # into ti by a step or a small leap, never a tritone
            out.append(ok)
    return out


def chosen_line(cantus_steps, start, beats=4):
    return [{"beat": start + beats * k, "length": beats, "step": opts[0], "choices": opts, "lyric": "ah"} for k, opts in enumerate(choices_over(cantus_steps))]


def cp_5_yours():
    return {
        "id": "cp-5-yours", "title": EN("Your choice"),
        "steps": [
            learn("Now you choose. At each cantus note, every smooth note in your range lights up: sing any one of them.",
                  [("Every lit note works", "Thirds, fifths, sixths and octaves"),
                   ("Move against it", "Opposite ways, as often as you can"),
                   ("A dimmed note", "It would make parallel or direct fifths (both voices moving the same way into a fifth or octave), or an awkward leap")], "harmony",
                  {"tempo": 60, "notes": line(FIRST_1, 0), "turn": False, "with": [{"notes": cantus(CANTUS_1, 0)}]}),
            {"kind": "play", "text": EN("A practice pass, not scored: at each cantus note, try a lit note and hear what it does."),
             "exercise": {"tempo": 60, "notes": CUE + chosen_line(CANTUS_1, 4), "turn": False, "with": [{"notes": cantus(CANTUS_1, 4, 4)}]}},
            {"kind": "play", "text": EN("Now for real, slowly: at each note of the cantus, sing any lit note. Make your own line."),
             "exercise": {"tempo": 60, "notes": CUE + chosen_line(CANTUS_1, 4), "turn": False, "with": [{"notes": cantus(CANTUS_1, 4, 4)}],
                          "score": "species", "rules": "contrary"},
             "measures": EN("Scored on landing on lit notes; the top score needs at least three moves in opposite ways.")},
        ],
    }


def cp_5_hold():
    bass = [{"beat": 4, "length": 4, "step": -12}, {"beat": 8, "length": 4, "step": -17}, {"beat": 12, "length": 4, "step": -12}]
    re = [{"beat": 8, "length": 4, "step": -10}]
    # Do for 4 beats, then do again for 2 over the new chord (the rub, scored as its own note), ti, do.
    held = [{"beat": 4, "length": 4, "step": 0, "lyric": "ah"}, {"beat": 8, "length": 2, "step": 0, "lyric": "ah"}, {"beat": 10, "length": 2, "step": -1, "lyric": "ah"}, {"beat": 12, "length": 4, "step": 0, "lyric": "ah"}]
    early = [{"beat": 0, "length": 4, "step": 0}, {"beat": 4, "length": 4, "step": -1}, {"beat": 8, "length": 4, "step": 0}]
    late = [{"beat": 0, "length": 6, "step": 0}, {"beat": 6, "length": 2, "step": -1}, {"beat": 8, "length": 4, "step": 0}]
    under = [{"beat": 0, "length": 4, "step": -12}, {"beat": 4, "length": 4, "step": -17}, {"beat": 4, "length": 4, "step": -10}, {"beat": 8, "length": 4, "step": -12}]
    return {
        "id": "cp-5-hold", "title": EN("Hold on, then let go"), "strictness": "standard",
        "steps": [
            learn("Hold a note into the next chord, where it rubs, then fall a step: a suspension, one of the oldest ways to make a listener lean in.",
                  [("Hold do", "While the bass moves under you"),
                   ("Feel the rub", "Do against so and re"),
                   ("Then let go", "Step down to ti, then home to do")], "drone",
                  {"tempo": 60, "notes": [dict(n, beat=n["beat"] - 4) for n in held], "turn": False,
                   "with": [{"notes": [dict(n, beat=n["beat"] - 4) for n in bass]}, {"notes": [dict(n, beat=n["beat"] - 4) for n in re], "volume": 0.4}]}),
            {"kind": "choose", "text": EN("Two ways to move. Listen to both, then choose."),
             "exercise": {"tempo": 60, "rounds": [
                 {"prompt": EN("Which one holds on into the rub?"), "clips": [{"notes": early + under}, {"notes": late + under}], "answer": 1,
                  "why": EN("B holds do over the new chord, where it rubs, then lets go. A steps down as the chord changes: smooth, but no lean.")},
                 {"prompt": EN("Which one leans before it lands?"), "clips": [{"notes": early + under}, {"notes": late + under}], "answer": 1,
                  "why": EN("B leans: the held do rubs over the new chord, then lands on ti. A steps down as the chord changes: smooth, but no lean. Composers have loved that lean for centuries.")},
             ]}},
            {"kind": "play", "text": EN("Hold do while the bass moves, feel the rub, then step to ti and home to do."),
             "exercise": {"tempo": 60, "notes": CUE + held, "turn": False, "with": [{"notes": bass}, {"notes": re, "volume": 0.4}]},
             "measures": EN("Scored on your notes on pitch, the held one too. Did you know? Fux's fourth species is all suspensions: notes tied over, rubbing on the strong beat, then falling a step.")},
        ],
    }


def cp_5_challenge():
    return {
        "id": "cp-5-challenge", "title": EN("Write a counterpoint"), "challenge": True,
        "steps": [
            learn("A new cantus, and every note is your choice. Make a line by the rules, then listen to the duet you wrote.",
                  [("Nearly every note lit", "Choose as you go"),
                   ("By the rules", "Half your moves opposite, no parallel or direct fifths or octaves"),
                   ("The ending", "Ti to do")], "harmony",
                  {"tempo": 60, "notes": cantus(CANTUS_3, 0), "turn": False}),
            {"kind": "play", "text": EN("Slowly: at each note of the cantus, choose a lit note. Then hear your duet."),
             "exercise": {"tempo": 60, "notes": CUE + chosen_line(CANTUS_3, 4), "turn": False, "with": [{"notes": cantus(CANTUS_3, 4, 4)}],
                          "score": "species", "rules": "all"},
             "measures": EN("Scored on landing on lit notes; the top score needs nearly every note lit and every rule: half your moves opposite ways, no parallel or direct fifths or octaves, and ti to do at the end.")},
        ],
    }


def relaxed(lessons):
    """Unit 1 is the first time against other voices: the beginner's ±50 cents. Every other unit is standard (±35)."""
    return [dict(l, strictness="relaxed") if "strictness" not in l else l for l in lessons]


course = {
    "id": "counterpoint", "version": 1, "reviewed": False, "title": EN("Counterpoint"),
    "units": [
        {"id": "cp-hold-your-own", "title": EN("Hold your own"), "colour": 3,
         "lessons": relaxed([cp_1_round(), cp_1_hear(), cp_1_pedal(), cp_1_ostinato(), cp_1_challenge()])},
        {"id": "cp-rounds-and-canons", "title": EN("Rounds and canons"), "colour": 3,
         "lessons": [cp_2_follow(), cp_2_minor(), cp_2_canon(), cp_2_challenge()]},
        {"id": "cp-two-lines", "title": EN("Two lines, one song"), "colour": 3,
         "lessons": [cp_3_call(), cp_3_counter(), cp_3_descant(), cp_3_partners(), cp_3_challenge()]},
        {"id": "cp-note-against-note", "title": EN("Note against note"), "colour": 3,
         "lessons": [cp_4_consonance(), cp_4_motion(), cp_4_first(), cp_4_second(), cp_4_challenge()]},
        {"id": "cp-make-your-own", "title": EN("Make your own"), "colour": 3,
         "lessons": [cp_5_yours(), cp_5_hold(), cp_5_challenge()]},
    ],
}
# Every choose step says what it scored (the house pattern).
for unit in course["units"]:
    for lesson in unit["lessons"]:
        for step in lesson["steps"]:
            if step["kind"] == "choose":
                step.setdefault("measures", EN("Scored on the rounds you got right first time."))

json.dump(course, open(OUT, "w"))
