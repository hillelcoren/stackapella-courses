"""Whistling (docs/courses/whistling.md in the app's repo): writes course/plus/whistling/course.json. Built from the
courses lead's outline, as revised by a whistling teacher's review and a game-design review, on the frontend's
whistle mode: a step with `"whistle": true` is tracked from 400 to 4000 Hz and folded down by whole octaves to the
written line before any scorer, and `base: "whistle"` lays it from the note lesson 1's `whistleNote` step keeps.

Every line is in semitones from your whistle note (0), with the note in the middle of a line, never at its bottom
(low whistles come out weak and airy). The spans: unit 1 within 2 semitones, unit 2 a fifth, unit 3 a sixth, unit 4
about an octave. The tunes are the library's, public domain and already sourced, each passage placed so your whistle
note sits mid-tune: Ode to Joy (Beethoven, 1824), the first eight bars; Simple Gifts (Brackett, 1848), its turning;
The Water Is Wide (traditional), its first verse. Hot Cross Buns is the course's own three-note line.

The checks fail the build on: a note outside its unit's span; a scored step without `whistle`; `rhythm` in unit 1
or on a challenge's last step; a measure (`drift`, `landing`, `rhythm`, the wave) as the last scored step of the
lesson that first shows it, or the wave as any lesson's last; a missing fact; the house words.

    python3 -I tools/wh_course.py && python3 -I tools/coursefmt.py course/plus/whistling/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/whistling/course.json"
WRITE = True

BANNED = re.compile(r"\bstars?\b|—|\bloud\b|\blouder\b|\bpush|\bpower\b|\bdrone\b|\bscale\b", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
EPS = 1e-9
SPAN = {1: (-2, 2), 2: (-4, 4), 3: (-4, 5), 4: (-5, 7)}
COLOUR = 4

SAFE = "if your lips tire or you feel light-headed, stop and breathe normally"
SAFE_CARD = ("Soft lips, an easy jaw", f"A gentle stream of air; {SAFE}")
PITCH = "Scored on your notes on pitch."
LANDS = "Scored on where each note lands from its first sound."
STEADY = "Scored on the note staying where it started."
RIBBON = "Scored on following the ribbon."
BEAT = "Scored on your notes on pitch and on the beat."
CHOSE = "Scored on the rounds you got right first time."
KEEP = "whistling.first-whistle"
W = {"whistle": True, "base": "whistle"}


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def num(x):
    x = round(x, 6)
    return int(x) if x == int(x) else x


def N(spec, lyric="oo"):
    """`step:length ...` from beat 0; a `-` step is a rest of that length."""
    out, beat = [], 0
    for token in spec.split():
        step, length = token.split(":")
        length = float(length)
        if step != "-":
            out.append({"beat": num(beat), "length": num(length), "step": int(step), "lyric": lyric})
        beat += length
    return out


class Song:
    """A library template's tune (its top part) and chords, in steps from your whistle note (midi - ref)."""

    def __init__(self, name, ref):
        data = json.loads((REPO / "templates" / "library" / f"{name}.json").read_text())
        self.tempo = data["tempo"]
        self.tune = [(n["beat"], n["length"], n["pitch"] - ref) for n in data["parts"][0]["guide"]["notes"]]
        self.chords = [(c["beat"], (c["root"] - ref) % 12, c["quality"]) for c in data["chords"]]
        self.sections = {s.get("name"): s["phrases"] for s in data["sections"]}

    def notes(self, frm, to, lyric="oo"):
        return [{"beat": num(b - frm), "length": num(length), "step": p, "lyric": lyric} for b, length, p in self.tune if frm - EPS <= b < to - EPS]

    def chords_at(self, frm, to):
        sounding = [c for c in self.chords if c[0] <= frm + EPS][-1]
        inside = [c for c in self.chords if frm + EPS < c[0] < to - EPS]
        return [{"beat": num(b - frm), "root": r, "quality": q} for b, r, q in [(frm,) + sounding[1:]] + inside]

    def phrases(self, section, i, j):
        p = self.sections[section]
        return self.notes(p[i][0], p[j][1]), self.chords_at(p[i][0], p[j][1])


# The tunes, each in G; the whistle note at B (Ode to Joy, Simple Gifts: G4 to D5 is -4 to +3) or G (The Water Is
# Wide: D4 to D5 is -5 to +7).
ODE = Song("ode-to-joy", 71)
GIFTS = Song("simple-gifts", 71)
WATER = Song("the-water-is-wide", 67)
ODE8, ODE8_CHORDS = ODE.phrases("Verse 1", 0, 3)   # the first eight bars
ODE4, ODE4_CHORDS = ODE.phrases("Verse 1", 0, 1)
GIFTS_T, GIFTS_T_CHORDS = GIFTS.phrases("Turning", 0, 1)
WATER_V, WATER_V_CHORDS = WATER.phrases("Verse 1", 0, 3)


# ---- Steps ----

def card(title, detail):
    assert len(title) <= 40, title
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards):
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": "steady", "reviewed": False}


def play(text, notes, measures, *, tempo=72, chords=None, **extra):
    ex = {"tempo": tempo, "notes": notes, "turn": not chords, **W}
    if chords:
        ex["chords"] = chords
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def lane(text, target, measures, **extra):
    return {"kind": "wave", "text": EN(text), "exercise": {"tempo": 60, "lead": 2, "step": 0, "lyric": "oo", "combo": False, **W, "target": target, **extra},
            "measures": EN(measures)}


def choose(text, rounds, tempo=72):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, **W, "rounds": [
        {"prompt": EN(p), "clips": [{"notes": c} for c in clips], "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


def selfcheck(text, notes, questions):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": 60, "lead": 2, **W, "model": {"notes": notes}, "questions": [EN(q) for q in questions]}}


def style(notes, at, how):
    return [dict(n, style=how) if i == at else n for i, n in enumerate(notes)]


# ---- The checks ----

def scored(step):
    if step["kind"] not in ("play", "choose", "bullseye", "wave"):
        return False
    target = step.get("exercise", {}).get("target")
    return not (target and all(t.get("scored") is False for t in target))


def measure_of(step):
    ex = step.get("exercise", {})
    if step["kind"] == "wave":
        return "wave" if any(t["kind"] == "wave" for t in ex["target"]) else None
    if "rhythm" in ex:
        return "rhythm"
    return ex.get("score") if ex.get("score") in ("drift", "landing") else None


SEEN = set()


def check(lid, unit, steps, challenge):
    lo, hi = SPAN[unit]
    last = max(i for i, s in enumerate(steps) if scored(s))
    for i, step in enumerate(steps):
        ex = step.get("exercise", {})
        where = f"wh-{lid} step {i + 1}"
        if step["kind"] in ("play", "try", "choose", "bullseye", "wave") and scored(step):
            assert ex.get("whistle") is True, f"{where}: every scored step is a whistle step"
        notes = ex.get("notes", []) + [n for r in ex.get("rounds", []) for c in r["clips"] for n in c["notes"]]
        for n in notes:
            assert lo <= n["step"] <= hi, f"{where}: step {n['step']} is outside unit {unit}'s span {lo} to {hi}"
        if "rhythm" in ex:
            assert unit > 1 and not (challenge and i == last), f"{where}: no timing in unit 1 or on a challenge's last step"
        m = measure_of(step)
        if m == "wave":
            assert i != last, f"{where}: the wave is never a lesson's last scored step"
        if m and i == last:
            assert m in SEEN, f"{where}: {m} is shown before it's a lesson's last scored step"
    for step in steps:
        m = measure_of(step)
        if m:
            SEEN.add(m)


# ---- The facts ----

FACTS = {}


def lesson(lid, unit, title, steps, **extra):
    assert len(steps) <= 5, lid
    check(lid, unit, steps, extra.get("challenge", False))
    if not extra.get("challenge") and lid in FACTS:
        extra = {"fact": FACTS[lid], **extra}
    return {"id": f"wh-{lid}", "title": EN(title), **extra, "steps": steps}


# ---- Unit 1: Your whistle ----

SAG = [{"beat": 0, "length": 3, "step": 0, "lyric": "oo"}]
STARTS = N("0:1 -:1 1:1 -:1 -1:1 -:1 0:2")
BUNS = N("2:1 1:1 0:2 2:1 1:1 0:2 0:0.5 0:0.5 0:0.5 0:0.5 1:0.5 1:0.5 1:0.5 1:0.5 2:1 1:1 0:2")

UNIT1 = [
    lesson("1-find", 1, "Find your whistle", [
        learn("Wet your lips and make a small, soft \"oo\" shape. Rest your tongue tip behind your bottom teeth, and blow slowly, as if cooling soup. Change the opening and your tongue a little at a time until a note comes.", [
            ("A hiss with a faint note is the start", "For many people it takes a few days, not a minute"),
            ("Breathing in can find it", "Some find their first note whistling in; then whistle out"),
            SAFE_CARD,
        ]),
        lane("Blow gently until the dot appears. Breathy is fine: the app hears the note, not how clear it is.",
             [{"seconds": 10, "kind": "free", "scored": False}], "Not scored: just find the note."),
        choose("Two whistles. Listen to both, then choose.", [
            ("Which whistle held steady?", [SAG, style(SAG, 0, "fall")], 0, "The first stayed on its note. The second sagged at the end."),
            ("Which whistle held steady?", [style(SAG, 0, "fall"), SAG], 1, "The second held; the first drooped as its air ran out."),
        ]),
        lane("Whistle any comfortable note and hold it for a few seconds. The line is only a guide.",
             [{"seconds": 5, "kind": "straight"}], "Scored on finding a steady whistle: any comfortable note counts.",
             score="whistleNote", keep=KEEP),
    ]),
    lesson("1-steady", 1, "Hold it steady", [
        learn("Your whistle note, held. Keep the air steady and the tongue still, and the note stays put.", [
            ("Steady air", "A slow, even stream"),
            ("A still tongue", "The tongue moves the note: keep it where it is"),
        ]),
        play("Your note, held for four beats.", N("0:4"), STEADY, tempo=60, score="drift"),
        selfcheck("Once more, then hear yourself.", N("0:4"), ["Clear or breathy?", "Did it wobble at the start?"]),
        lane("Hold it on the lane: a straight line, start to end.", [{"seconds": 5, "kind": "straight"}], "Scored on how straight the note stayed."),
    ]),
    lesson("1-start", 1, "A clean start", [
        learn("Start each note with a soft \"h\", the shape already set, so the note is there from its first sound.", [
            ("A soft h", "The shape first, then the air"),
            ("On the note at once", "No slide up into it"),
        ]),
        {"kind": "bullseye", "text": EN("Whistle each note back, and watch where it lands."),
         "exercise": {"tempo": 72, **W, "echoes": [0, 1, -1]}, "measures": EN(LANDS)},
        play("Four short notes, a rest before each: on the note from the first sound.", STARTS, LANDS, score="landing"),
        lane("Then one long one, held.", [{"seconds": 4, "kind": "straight"}], "Scored on how straight the note stayed."),
    ]),
    lesson("1-challenge", 1, "Hot Cross Buns", [
        learn("Three notes and a tune: your note and the two just above it, each started clean.", [
            ("Three notes", "Down, down, then the quick ones"),
            SAFE_CARD,
        ]),
        play("The whole tune, heard then whistled.", BUNS, PITCH),
    ], challenge=True),
]


# ---- Unit 2: The tongue ----

UP_DOWN = N("0:1 1:1 0:1 -1:1 0:2")
FIVE = N("-2:1 -1:1 0:1 1:1 2:1 1:1 0:1 -1:1 -2:2")
NOTE_LOW = [{"beat": 0, "length": 1, "step": -2, "lyric": "oo"}, {"beat": 1, "length": 2, "step": 1, "lyric": "oo"}]

UNIT2 = [
    lesson("2-step", 2, "The next note up", [
        learn("The tongue moves the note. Think a silent \"ee\" to go up and a silent \"oo\" to come down: the lips hardly move.", [
            ("Up: a silent ee", "The tongue rises and moves forward"),
            ("Down: a silent oo", "The tongue settles back"),
            SAFE_CARD,
        ]),
        {"kind": "try", "text": EN("Find the notes: each one waits until you're on it."), "exercise": {"tempo": 72, **W, "notes": UP_DOWN}},
        play("Up one, back, down one, home.", UP_DOWN, PITCH),
    ]),
    lesson("2-five", 2, "Five notes, one at a time", [
        learn("Five notes up and back, your whistle note in the middle.", [
            ("One at a time", "Each note its own small tongue move"),
            ("Your note in the middle", "Two below, two above"),
        ]),
        play("Five notes up and back.", FIVE, PITCH),
    ]),
    lesson("2-slide", 2, "A slide", [
        learn("Glide the tongue and the note slides with it, smoothly, from low to high and back.", [
            ("A smooth glide", "No jumps on the way"),
            ("Find your edges", "The last slide goes as low and high as is easy"),
        ]),
        lane("Follow the ribbon up and back.", [{"seconds": 5, "kind": "path", "band": 150, "points": [[0, -3], [2.5, 3], [5, -3]]}], RIBBON),
        lane("Now as low and as high as is easy, then back. Not scored: notice where your whistle flips to a new shape.",
             [{"seconds": 6, "kind": "free", "scored": False}], "Not scored: just notice where it flips."),
        choose("Listen to both, then choose.", [
            ("Which one slid up into the note?", [style(NOTE_LOW, 1, "scoop"), NOTE_LOW], 0, "The first slid up into its second note. The second landed right on it."),
            ("Which one slid up into the note?", [NOTE_LOW, style(NOTE_LOW, 1, "scoop")], 1, "The second slid into it; the first was there at once."),
        ]),
        lane("Follow the ribbon once more.", [{"seconds": 5, "kind": "path", "band": 150, "points": [[0, 3], [2.5, -3], [5, 3]]}], RIBBON),
    ]),
    lesson("2-challenge", 2, "Ode to Joy", [
        learn("Beethoven's tune, its first eight bars: nearly all of it one note at a time.", [
            ("One note at a time", "And one small jump near the end"),
            SAFE_CARD,
        ]),
        play("The first eight bars, over the chords.", ODE8, PITCH, tempo=88, chords=ODE8_CHORDS),
    ], challenge=True),
]


# ---- Unit 3: Leaps ----

THIRDS = N("-2:1 0:1 -2:1 0:1 2:1 0:1 -2:2")
BIG = N("-2:1 2:1 -2:1 3:1 -2:2")
SIXTH = N("-4:1 1:1 -4:1 -2:1 2:1 -2:2")
JUMP = [{"beat": 0, "length": 1, "step": -2, "lyric": "oo"}, {"beat": 1, "length": 2, "step": 2, "lyric": "oo"}]
OVER = [{"beat": 0, "length": 1, "step": -2, "lyric": "oo"}, {"beat": 1, "length": 0.25, "step": 3, "lyric": "oo"}, {"beat": 1.25, "length": 1.75, "step": 2, "lyric": "oo"}]

UNIT3 = [
    lesson("3-small", 3, "Small jumps", [
        learn("A jump skips the notes between. Slide it slowly first, then jump: one quick tongue move, the air still flowing.", [
            ("Slide, then jump", "The same tongue move, faster"),
            ("Skip one note", "That jump is a third"),
            SAFE_CARD,
        ]),
        lane("Slide it first, slowly.", [{"seconds": 4, "kind": "path", "band": 150, "points": [[0, -2], [2, 2], [4, -2]]}], RIBBON),
        play("Now jump: skip one note each time.", THIRDS, LANDS, score="landing"),
        play("Once more, every note on pitch.", THIRDS, PITCH),
    ]),
    lesson("3-bigger", 3, "Bigger jumps", [
        learn("Bigger jumps: land the top note right on it, not past it.", [
            ("Hear it first", "The top note in your head before you jump"),
            ("Land, don't overshoot", "Aim for the note, not above it"),
        ]),
        choose("Listen to both, then choose.", [
            ("Which one landed on the top note?", [JUMP, OVER], 0, "The first landed right on it. The second went past it and came back."),
            ("Which one landed on the top note?", [OVER, JUMP], 1, "The second landed clean; the first overshot first."),
        ]),
        play("Ode to Joy's first two lines, on the beat.", ODE4, BEAT, tempo=88, chords=ODE4_CHORDS, rhythm=True),
        play("Bigger jumps, each top note landed.", BIG, PITCH),
    ]),
    lesson("3-high", 3, "The big jump", [
        learn("The biggest jump here is a sixth: the top note only as high as is easy. Slide it, then land it, then jump.", [
            ("Only as high as is easy", "If it won't come, sing it smaller"),
            ("Air keeps moving", "One quick tongue move"),
        ]),
        play("The big jump, slowly, landing each top note.", SIXTH, LANDS, tempo=60, score="landing"),
        play("Now at speed.", SIXTH, PITCH),
    ]),
    lesson("3-challenge", 3, "Simple Gifts", [
        learn("Simple Gifts, its turning: the tune's own jumps, each landed clean.", [
            ("Jumps that land", "Hear each top note first"),
            SAFE_CARD,
        ]),
        play("The turning, over the chords.", GIFTS_T, PITCH, tempo=84, chords=GIFTS_T_CHORDS),
    ], challenge=True),
]


# ---- Unit 4: A whistled tune ----

PHRASES = N("-1:1 0:1 2:1 0:1 -1:2 -:1 2:1 0:1 -1:1 0:1 -2:2")
REPEATS = N("0:1 0:1 2:1 2:1 0:2")

UNIT4 = [
    lesson("4-drone", 4, "In tune with a held note", [
        learn("A held note sounds under you. Whistle your note on top of it, and listen for the two settling together.", [
            ("Listen under you", "The held note doesn't move"),
            ("Settle into it", "Small tongue moves until it rings"),
            SAFE_CARD,
        ]),
        play("Your note over the held one, four beats.", N("0:4"), PITCH, tempo=60, drone={"step": 0}, tuning=True),
        play("Two notes over it: your note, then the one above.", N("0:3 2:3"), PITCH, tempo=60, drone={"step": 0}, tuning=True),
    ]),
    lesson("4-breath", 4, "A breath each phrase", [
        learn("Whistling uses air fast. Take a breath at each phrase's end, and start repeated notes each with a soft \"h\".", [
            ("A breath each phrase", "In the rest, before the next"),
            ("Repeated notes", "A soft h on each"),
        ]),
        choose("Listen to both, then choose.", [
            ("Which one took a breath between the phrases?", [PHRASES, N("-1:1 0:1 2:1 0:1 -1:3 2:1 0:1 -1:1 0:1 -2:2")], 0,
             "The first left a rest to breathe in. The second ran straight on."),
        ]),
        play("Repeated notes, each with a soft h.", REPEATS, LANDS, score="landing"),
        play("Two phrases, a breath between.", PHRASES, PITCH),
    ]),
    lesson("4-wave", 4, "An even wave", [
        learn("A whistle can carry an even wave: a tiny silent \"ee-oo\" with the tongue, slowly at first. Singers call it vibrato. It takes time: a straight note is just as good.", [
            ("Slow first", "Three or four waves a second"),
            ("Tongue, not air", "The tongue makes the wave"),
        ]),
        lane("Follow the slow wave, with the ghost wave fading out.", [{"seconds": 6, "kind": "wave", "hz": 3, "cents": 60, "fade": 2}], "Scored on following the wave."),
        lane("Now a straight note, held: as good as any wave.", [{"seconds": 5, "kind": "straight"}], "Scored on how straight the note stayed."),
    ]),
    lesson("4-challenge", 4, "The Water Is Wide", [
        learn("A whole tune, then a second whistle under it, kept as a song. Then your first whistle, beside today's.", [
            ("The whole first verse", "A breath at each phrase end"),
            ("Whistle with yourself", "A low line under your own tune"),
            ("Then and now", "Your first whistle from lesson 1"),
        ]),
        play("The first verse, over the chords.", WATER_V, PITCH, tempo=76, chords=WATER_V_CHORDS),
        play("Now a low line under your own tune: two notes, held.", N("-5:12 -3:12 -5:12 -5:12"), PITCH, tempo=76, chords=WATER_V_CHORDS, under={"step": 1}),
        lane("One last note, held: your whistle today.", [{"seconds": 5, "kind": "straight"}], "Scored on how straight the note stayed.", thenAndNow=KEEP),
    ], challenge=True, headphones="needed",
       keepSong={"title": EN("My whistled tune"), "takes": [{"step": 1, "name": EN("Tune")}, {"step": 2, "name": EN("Under")}], "from": 1, "partners": [], "chords": EN("Piano")}),
]

course = {
    "id": "whistling", "version": 1, "reviewed": False, "title": EN("Whistling"),
    "units": [
        {"id": "wh-your-whistle", "title": EN("Your whistle"), "colour": COLOUR, "lessons": UNIT1},
        {"id": "wh-the-tongue", "title": EN("The tongue"), "colour": COLOUR, "lessons": UNIT2},
        {"id": "wh-leaps", "title": EN("Leaps"), "colour": COLOUR, "lessons": UNIT3},
        {"id": "wh-a-whistled-tune", "title": EN("A whistled tune"), "colour": COLOUR, "lessons": UNIT4},
    ],
}

missing = [l["id"] for u in course["units"] for l in u["lessons"] if not l.get("challenge") and "fact" not in l]
if missing:
    print("facts still to come:", ", ".join(missing))
if WRITE:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(course, open(OUT, "w"), ensure_ascii=False)
