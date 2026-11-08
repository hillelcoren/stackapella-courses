"""Scat singing (docs/courses/scat.md in the app's repo): writes course/plus/scat/course.json. Every
line counts from the singer's comfortable note (do, 0), and the blues is in that key. Swing is
written into the notes: an on-beat eighth lasts two thirds of a beat, an off-beat one a third. A
trade is the call (the guide alone, `listenOnly`) and then you; where you choose, a note's `choices`
are the chord's tones (or the scale's notes) within a sixth of do. Under every line: the chords and a
walking bass (a partner voice). Breaths are checked by tools/breaths.py before the file is written.

    python3 -I tools/sc_course.py && python3 -I tools/coursefmt.py course/plus/scat/course.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/scat/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

BANNED = re.compile(r"\b(stars?|starring)\b", re.I)
SAFETY = "Light and easy: a loose jaw, a medium volume, the middle of your voice. Accent with breath, never the throat. Stop if anything tightens."
RANGE = 9  # a sixth either side of do
TEMPO = 80

CHORD = {"I": 0, "IV": 5, "V": 7}
TONES = {"I": (0, 4, 7, 10), "IV": (5, 9, 0, 3), "V": (7, 11, 2, 5)}  # 1, 3, 5, flat 7 of each dominant seventh
BLUES = (10, 0, 3, 5, 6, 7)  # the blues scale's notes: flat seven, do, flat three, four, flat five, five
FORM = ["I", "I", "I", "I", "IV", "IV", "I", "I", "V", "IV", "I", "V"]


def EN(text):
    assert not BANNED.search(text), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="harmony"):
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def fact(fid, text, source, url):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


def play(text, exercise, measures=None, kind="play", rhythm=None):
    """`rhythm` "swing": scored on the swung beat too, and the words say so."""
    assert ("swung beat" in (measures or "")) == (rhythm == "swing"), text
    if rhythm:
        exercise = dict(exercise, rhythm=rhythm)
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def choose(text, rounds, tempo=TEMPO):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


def selfcheck(text, model, questions, tempo=TEMPO):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


def within(pcs):
    """Every step within a sixth of do whose pitch class is one of `pcs`."""
    return sorted(s for s in range(-RANGE, RANGE + 1) if s % 12 in pcs)


def lit(chord, flat_seven=True):
    tones = TONES[chord] if flat_seven else TONES[chord][:3]
    return within(tones)


# ---- Swing ----

def swung(tokens, steps, words, start=0.0):
    """Notes from a rhythm in eighths: 'e' an eighth (swung by where it falls), 'q' a quarter, 'h' a
    half, 'w' a whole; 'r' an eighth's rest, 'R' a quarter's rest. Returns the notes (steps and words
    in order) and the beat after the last token."""
    def at(k):  # eighth slot k from `start` (an on-beat start), as a beat: on-beat eighths 2/3 long
        return start + k // 2 + (2 / 3 if k % 2 else 0)
    size = {"e": 1, "q": 2, "h": 4, "w": 8, "r": 1, "R": 2}
    notes, k, i = [], 0, 0
    for t in tokens:
        if t in "eqhw":
            n = {"beat": round(at(k), 4), "length": round(at(k + size[t]) - at(k), 4), "step": steps[i]}
            if words[i]:
                n["lyric"] = words[i]
            notes.append(n)
            i += 1
        k += size[t]
    assert i == len(steps) == len(words), (tokens, steps, words)
    return notes, start + k / 2


# Four two-bar calls (8 beats each), in do's key over I7; two of them start on the "and".
CALLS = [
    ("e e e e q r e h R R".split(), [0, 2, 4, 7, 4, 2, 0], ["doo", "bah", "doo", "bah", "doo", "bah", "doo"]),
    ("r e e e q q e e h R".split(), [4, 7, 4, 2, 0, 2, 4, 0], ["bee", "dah", "doo", "dn", "dat", "doo", "bah", "doo"]),
    ("e e q e e q h R R".split(), [7, 4, 2, 0, -2, 0, 4], ["doo", "bah", "doo", "bee", "dah", "doo", "dat"]),
    ("r e q e e q q h R".split(), [0, 4, 7, 9, 7, 4, 0], ["bah", "doo", "bee", "dah", "doo", "bah", "doo"]),
]
ON_THE_AND = (1, 3)


def shift(notes, by):
    """A call moved onto another chord's root: every step by `by`, folded back within a sixth of do."""
    out = []
    for n in notes:
        s = n["step"] + by
        while s > RANGE:
            s -= 12
        while s < -RANGE:
            s += 12
        out.append(dict(n, step=s))
    return out


def walking_bass(chords, start=0.0):
    """A walking bass, a note a beat (root, third, fifth, sixth), low under do."""
    shape = (0, 4, 7, 9)
    notes = []
    for bar, name in enumerate(chords):
        root = CHORD[name] - 24
        for b in range(4):
            notes.append({"beat": start + bar * 4 + b, "length": 1, "step": root + shape[b], "lyric": "dm"})
    return {"notes": notes, "volume": 0.4}


def chords_of(names, start=0.0):
    return [{"beat": start + k * 4, "root": CHORD[n] - 12, "quality": "dom7", "bass": None} for k, n in enumerate(names)]


def band(names, start=0.0):
    """The chords and the walking bass for `names`, a chord a bar."""
    return {"chords": chords_of(names, start), "with": [walking_bass(names, start)]}


def trade(call_index, chord="I", start=0.0, choose_last=1, sets=None, sung_steps=None):
    """A four-bar trade from `start`: the call (two bars, guide only), then your echo (two bars), its
    last `choose_last` notes lit from `sets` (the chord's tones by default)."""
    tokens, steps, words = CALLS[call_index]
    call, _ = swung(tokens, steps, words, start)
    call = shift(call, CHORD[chord] if CHORD[chord] <= 5 else CHORD[chord] - 12)
    for n in call:
        n["listenOnly"] = True
    echo, _ = swung(tokens, steps, words, start + 8)
    echo = shift(echo, CHORD[chord] if CHORD[chord] <= 5 else CHORD[chord] - 12)
    if sung_steps:
        for n, s in zip(echo, sung_steps):
            n["step"] = s
    options = sets if sets is not None else lit(chord)
    for n in echo[-choose_last:]:
        n["choices"] = options
        n["step"] = min(options, key=lambda s: abs(s - n["step"]))
    return call + echo


def trades(calls_chords, choose_last=1, sets=None):
    notes, names = [], []
    for k, (ci, chord) in enumerate(calls_chords):
        notes += trade(ci, chord, k * 16, choose_last, None if sets is None else sets(chord))
        names += [chord] * 4
    return notes, names


def exercise(notes, names, **extra):
    ex = {"tempo": extra.pop("tempo", TEMPO), "notes": notes, "turn": False}
    ex.update(band(names))
    ex.update(extra)
    return ex


# The swing steps take `rhythm: "swing"` (pitch 70, timing 30, off-beats judged at two thirds of the beat;
# docs/play-timing-plan.md in the app's repo): every one is written swung, so straight eighths lose the
# timing part.
PITCH_SWING = "Scored on your notes on pitch and on the swung beat."
LANDED = "Scored on your notes on pitch and on the swung beat, each one you chose on a lit note."

# ---- Unit 1: The swing pocket ----

FIRST = [(0, "I"), (2, "I"), (1, "I"), (3, "I")]


def first_trades(**extra):
    notes, names = trades(FIRST)
    return exercise(notes, names, **extra)


def sc_1_trade():
    # The try is your echo alone (a try holds each note until you find it, so the call's guide-only notes stay out).
    tokens, steps, words = CALLS[0]
    try_notes, _ = swung(tokens, steps, words)
    try_names = ["I", "I"]
    return {
        "id": "sc-1-trade", "title": EN("Trade with the band"), "strictness": "relaxed",
        "fact": fact("scat-syllables-as-instruments", "Scat syllables can copy instruments. A 1987 study likened Ella Fitzgerald's \"b\" and \"p\" to reed instruments and her \"d\" to tongued brass, and Sarah Vaughan's \"sh\" to brushes on a drum.", "Wikipedia, Scat singing (citing Stewart, Jazzforschung/Jazz Research 19 (1987))", "https://en.wikipedia.org/wiki/Scat_singing"),
        "steps": [
            learn("Scat is singing like a horn on syllables. The band plays a call; you answer it. No wrong notes here: where you choose, every lit note fits.",
                  [("The call", "Two bars from the band"), ("Your echo", "The same two bars back"), ("Your last note", "Any lit note: one that sounds at rest")]),
            play("Echo one call, its syllables written out.", exercise(try_notes, try_names), None, kind="try"),
            play(f"Four trades. End each on any lit note, a different one each time if you like. {SAFETY}",
                 first_trades(keep="sc.first-trade", generous=True), LANDED, rhythm="swing"),
        ],
    }


def pair_clip(swing):
    notes = []
    for k in range(8):
        on = k % 2 == 0
        beat = k // 2 + (0 if on else (2 / 3 if swing else 0.5))
        end = k // 2 + (2 / 3 if swing else 0.5) if on else k // 2 + 1
        notes.append({"beat": round(beat, 4), "length": round(end - beat, 4), "step": 0 if on else 2})
    return {"notes": notes}


def sc_1_swing():
    rounds = [{"prompt": EN("Which one swings?"), "clips": [pair_clip(s), pair_clip(not s)], "answer": 0 if s else 1,
               "why": EN("Swing makes each pair long-short, like a heartbeat; straight makes them even.")} for s in (True, False, True)]
    one, _ = swung(["e"] * 8, [0] * 8, ["doo", "bah"] * 4)
    two, _ = swung(["e"] * 8 + ["h", "R", "R"], [0, 2] * 4 + [0], ["doo", "bah"] * 4 + ["doo"])
    return {
        "id": "sc-1-swing", "title": EN("Long, short"),
        "fact": fact("swing-ratio-tempo", "Swing isn't one fixed ratio. When researchers measured jazz drummers' ride cymbals, the long note grew longer at slow tempos, up to about 3.5 to 1, and the swing evened out at fast tempos.",
                     "Friberg and Sundström, Jazz drummers' swing ratio in relation to tempo, Acoustical Society of America (1999)", "https://acoustics.org/pressroom/httpdocs/137th/friberg.html"),
        "steps": [
            learn("Swing is long, short: \"doo-BAH\". A soft d on the long note, a b and a little accent on the short one, with breath, never the throat.",
                  [("Doo", "Long, soft"), ("BAH", "Short, leaning"), ("Long, short", "Like a heartbeat")]),
            choose("Listen to each, then choose.", rounds),
            play("\"Doo-bah\" on one note, swung. Just try it.", exercise(one, ["I", "I"]), None, kind="try"),
            play("Now on two notes, swung, landing on \"doo\".", exercise(two, ["I", "I", "I"]), PITCH_SWING, rhythm="swing"),
        ],
    }


def sc_1_and():
    notes, names = [], []
    for k, (ci, chord) in enumerate([(1, "I"), (3, "I"), (1, "I"), (3, "I")]):
        t = trade(ci, chord, k * 16, choose_last=1, sets=[0])  # the echo ends on do, on "dat" or "doo"
        notes += t
        names += [chord] * 4
    return {
        "id": "sc-1-and", "title": EN("Start on the and"),
        "fact": fact("bebop-from-scat-syllables", "The word \"bebop\" comes from scat syllables. In Dizzy Gillespie's account, fans heard him scat his new, untitled tunes to the band, and \"would ask for bebop.\"", "Wikipedia, Bebop", "https://en.wikipedia.org/wiki/Bebop"),
        "steps": [
            learn("Jazz lines love to start just after the beat, on the \"and\". End each one clean, the t of \"dat\" cutting it off.",
                  [("Wait", "Let the beat go by"), ("Then go", "On the and"), ("Dat", "A clean end")]),
            play("Four calls that start on the and; echo each.", exercise(notes, names), PITCH_SWING, rhythm="swing"),
        ],
    }


def sc_1_challenge():
    notes, names = trades([(1, "I"), (3, "I"), (1, "I"), (3, "I")])
    return {
        "id": "sc-1-challenge", "title": EN("Four trades on the and"), "challenge": True,
        "steps": [
            learn("Lesson 1's trades, to hear how far you've come, then four calls that start on the and, your echoes ending wherever you like on a lit note.",
                  [("Then and now", "Lesson 1's four trades"), ("On the and", "Calls that start off the beat"), ("Your landing", "Any lit note")]),
            play("Lesson 1's four trades again.", first_trades(thenAndNow="sc.first-trade"), LANDED, rhythm="swing"),
            play("Now the four calls on the and.", exercise(notes, names), LANDED, rhythm="swing"),
        ],
    }

# ---- Unit 2: The form and the landing ----

def change_clip(changes):
    second = "IV" if changes else "I"
    return {"notes": [{"beat": 0, "length": 2, "step": 0}, {"beat": 2, "length": 2, "step": 0}],
            "chords": [{"beat": 0, "root": -12, "quality": "dom7", "bass": None}, {"beat": 2, "root": CHORD[second] - 12, "quality": "dom7", "bass": None}]}


def sc_2_form():
    rounds = [{"prompt": EN("Which one changes chord?"), "clips": [change_clip(c), change_clip(not c)], "answer": 0 if c else 1,
               "why": EN("The note on top stays; the chord under it moves from I to IV.")} for c in (True, False, True, False)]
    near = {"I": 0, "IV": 5, "V": -5}
    notes = []
    for bar, name in enumerate(FORM):
        b = bar * 4
        notes.append({"beat": b, "length": 2, "step": near[name], "lyric": "doo"})
        if bar + 1 < len(FORM):
            nxt = near[FORM[bar + 1]]
            pick, _ = swung(["e", "e"], [near[name], nxt + (2 if nxt < 9 else -1)], ["doo", "bah"], b + 3)
            notes += pick
    return {
        "id": "sc-2-form", "title": EN("The twelve bars"),
        "fact": fact("heebie-jeebies-1926", "Louis Armstrong and His Hot Five recorded \"Heebie Jeebies\" in 1926, and it put scat singing on the map, though others had scatted on records before. Armstrong said he dropped his lyric sheet and scatted instead; historians still debate the story.",
                     "Riccardi, I Got the Heebies!, Louis Armstrong House Museum", "https://virtualexhibits.louisarmstronghouse.org/2026/02/26/i-got-the-heebies-100-years-of-heebie-jeebies/"),
        "steps": [
            learn("The blues is twelve bars long: four of I, two of IV, two of I, then V, IV, I and V to turn around. Each bar's root is the floor under it.",
                  [("I, I, I, I", "Home for four bars"), ("IV, IV, I, I", "Away and back"), ("V, IV, I, V", "And round again")]),
            choose("Listen to each, then choose.", rounds),
            play("The root of every bar on \"doo\", with a swung \"doo-bah\" into each change.", exercise(notes, FORM), PITCH_SWING, rhythm="swing"),
        ],
    }


def finish(chords):
    notes, names = [], []
    for k, chord in enumerate(chords):
        call = trade(0, chord, k * 8, choose_last=1, sets=lit(chord, flat_seven=False))
        call = [n for n in call if n["beat"] < k * 8 + 8]  # the call only
        for n in call[:-1]:
            n["listenOnly"] = True
        last = call[-1]
        last.pop("listenOnly", None)
        last["choices"] = lit(chord, flat_seven=False)
        last["lyric"] = "dat"
        notes += call
        names += [chord] * 2
    return notes, names


def sc_2_finish():
    notes, names = finish(["I", "IV", "I", "V"])
    model = [n for n in notes if not n.get("listenOnly")]
    return {
        "id": "sc-2-finish", "title": EN("Finish the phrase"),
        "fact": fact("stop-time-tap-dancers", "In \"stop-time\" the band hits a chord, then falls silent for the soloist to fill. Louis Armstrong's famous stop-time chorus in \"Potato Head Blues\" (1927) drew partly on the tap dancing at the Sunset Café.", "Wikipedia, Potato Head Blues (citing Brothers, Louis Armstrong: Master of Modernism (2014))", "https://en.wikipedia.org/wiki/Potato_Head_Blues"),
        "steps": [
            learn("The band plays a phrase and stops short: you sing its last note, any of the chord's 1, 3 or 5.",
                  [("Listen", "The phrase from the band"), ("Finish it", "Its last note is yours"), ("Any lit note", "1, 3 or 5 of the chord")]),
            play("Four phrases to finish.", exercise(notes, names), "Scored on landing each last note on a lit note."),
            selfcheck("Once more, then hear yours beside the guide's.", model, ["Did your \"doo\" and your \"dat\" sound different?", "Did your jaw stay loose?"]),
        ],
    }


def ending_clip(major):
    return {"notes": [{"beat": 0, "length": 1, "step": 7}, {"beat": 1, "length": 1, "step": 5}, {"beat": 2, "length": 2, "step": 4 if major else 3}],
            "chords": [{"beat": 0, "root": -12, "quality": "maj", "bass": None}]}


def sc_2_third():
    rounds = [{"prompt": EN("Which ending is bright (major)?"), "clips": [ending_clip(m), ending_clip(not m)], "answer": 0 if m else 1,
               "why": EN("The bright one ends on the chord's third; the other ends a half step lower, darker.")} for m in (True, False, True)]
    third = {"I": 4, "IV": -3, "V": -1}
    notes, names = [], []
    for k, chord in enumerate(["I", "IV", "I", "V"]):
        notes += trade(0, chord, k * 16, choose_last=1, sets=[third[chord]])
        names += [chord] * 4
    return {
        "id": "sc-2-third", "title": EN("The colour note"),
        "fact": fact("shell-voicings-third-seventh", "A jazz \"shell voicing\" leaves out a chord's fifth, sometimes its root too: the third and seventh alone imply what kind of chord it is. Bud Powell and Bill Evans used them extensively.", "University of North Carolina Wilmington, Using Shell Voicings", "https://people.uncw.edu/russellr/ShellVoicings.html"),
        "steps": [
            learn("The third is the chord's colour: it says major. Land your phrases on it.",
                  [("Listen", "Bright or dark?"), ("The third", "The colour note"), ("Land it", "Right on, no slide")]),
            choose("Listen to each, then choose.", rounds),
            play("Echo four calls, each ending on the chord's third.", exercise(notes, names, score="landing"), "Scored on where each note landed, and whether it slid in."),
        ],
    }


def sc_2_challenge():
    notes, names = [], []
    for k, chord in enumerate(["I", "I", "IV", "I"]):
        tokens, steps, words = CALLS[(1, 3)[k % 2]]
        ph, _ = swung(tokens, steps, words, k * 8)
        ph = shift(ph, CHORD[chord] if CHORD[chord] <= 5 else CHORD[chord] - 12)
        ph[-1]["choices"] = lit(chord, flat_seven=False)
        notes += ph
        names += [chord] * 2
    return {
        "id": "sc-2-challenge", "title": EN("Land them all"), "challenge": True,
        "steps": [
            learn("Lesson 1's trades, then the first eight bars of the blues: four phrases, each starting on the and (unit 1), each landing on 1, 3 or 5.",
                  [("Then and now", "Lesson 1's trades"), ("On the and", "Every phrase"), ("Land it", "1, 3 or 5 of its chord")]),
            play("Lesson 1's four trades again.", first_trades(thenAndNow="sc.first-trade"), LANDED, rhythm="swing"),
            play("Eight bars, four phrases, each landing on a lit note.", exercise(notes, names), LANDED, rhythm="swing"),
        ],
    }

# ---- Unit 3: Call and response ----

def sc_3_ends():
    notes, names = trades([(0, "I"), (2, "IV"), (3, "I"), (0, "V")], choose_last=2)
    return {
        "id": "sc-3-ends", "title": EN("Keep the rhythm, change the end"),
        "fact": fact("blues-aab-verse", "Many blues verses follow an AAB pattern: a line sung over four bars, the same line repeated over the next four, then a longer, different line to close.", "Wikipedia, Blues", "https://en.wikipedia.org/wiki/Blues"),
        "steps": [
            learn("Echo the call's rhythm, and choose its last two notes yourself, any of the chord's tones, the flat seven too.",
                  [("The rhythm", "Exactly the call's"), ("The end", "Two notes of your own"), ("The flat seven", "Now lit too")]),
            play("Four calls; the last two notes are yours.", exercise(notes, names), LANDED, rhythm="swing"),
        ],
    }


def answer(calls_chords, sets=None):
    notes, names = [], []
    for k, (ci, chord) in enumerate(calls_chords):
        t = trade(ci, chord, k * 16, choose_last=len(CALLS[ci][1]), sets=None if sets is None else sets(chord))
        notes += t
        names += [chord] * 4
    return notes, names


def sc_3_answer():
    notes, names = answer([(0, "I"), (2, "IV"), (3, "I"), (0, "V")])
    model = [n for n in notes if not n.get("listenOnly")][:7]
    return {
        "id": "sc-3-answer", "title": EN("Answer the call"),
        "fact": fact("calloway-hepsters-dictionary", "In 1938 the bandleader Cab Calloway published a dictionary of jazz slang, the Hepster's Dictionary.",
                     "Mellby, A Hepster's Dictionary, Princeton University Library (2021)", "https://graphicarts.princeton.edu/2021/03/04/a-hepsters-dictionary"),
        "steps": [
            learn("Now a whole answer of your own: the call's rhythm, and any of the chord's tones on every note.",
                  [("The rhythm", "Keep the call's"), ("The notes", "All yours, all lit"), ("The syllables", "Copy the call's")]),
            play("Four calls; answer each.", exercise(notes, names), LANDED, rhythm="swing"),
            selfcheck("Once more, then hear yours beside the guide's.", model, ["Did you copy the call's syllables?", "Did your jaw stay loose?"]),
        ],
    }


RIFF = ("e e e e h R R".split(), [-2, 0, 3, 5, 7], ["doo", "bah", "doo", "bah", "doo"])


def sc_3_riff():
    notes, names = [], []
    for k, chord in enumerate(["I", "IV", "I", "V"]):
        ph, _ = swung(*RIFF, k * 8)
        notes += ph
        names += [chord] * 2
    return {
        "id": "sc-3-riff", "title": EN("A riff"),
        "fact": fact("in-the-mood-riff-1930", "The riff of Glenn Miller's \"In the Mood\" was going round the bands years earlier: Wingy Manone recorded it in \"Tar Paper Stomp\" in 1930, and Fletcher Henderson's band used it in 1931.", "Wikipedia, In the Mood", "https://en.wikipedia.org/wiki/In_the_Mood"),
        "steps": [
            learn("A riff is a short phrase the band repeats over the changes. This one is the minor pentatonic: flat seven, do, flat three, four and five, ending on five.",
                  [("Five notes", "Flat seven up to five"), ("Every chord", "The same riff"), ("Ends on five", "It fits even over V")]),
            play("The riff over I, IV, I and V.", exercise(notes, names), PITCH_SWING, rhythm="swing"),
        ],
    }


def sc_3_challenge():
    third = {"I": [4], "IV": [-3], "V": [-1]}
    notes, names = trades([(0, "I"), (2, "IV"), (3, "I"), (0, "V")], sets=lambda c: third[c])
    return {
        "id": "sc-3-challenge", "title": EN("Trading twos"), "challenge": True,
        "steps": [
            learn("Lesson 1's trades, then four calls and your answers, each ending on the chord's third, unit 2's colour note.",
                  [("Then and now", "Lesson 1's trades"), ("Trading twos", "Two bars each"), ("The colour note", "Every answer ends on the third")]),
            play("Lesson 1's four trades again.", first_trades(thenAndNow="sc.first-trade"), LANDED, rhythm="swing"),
            play("Four calls; your answers end on the third.", exercise(notes, names), LANDED, rhythm="swing"),
        ],
    }

# ---- Unit 4: The blues ----

def lean_clip(leans):
    notes = ([{"beat": 0, "length": 0.75, "step": 3}, {"beat": 0.75, "length": 1.25, "step": 4}] if leans else [{"beat": 0, "length": 2, "step": 4}])
    return {"notes": notes, "chords": [{"beat": 0, "root": -12, "quality": "dom7", "bass": None}]}


def sc_4_blue():
    rounds = [{"prompt": EN("Which one leans?"), "clips": [lean_clip(l), lean_clip(not l)], "answer": 0 if l else 1,
               "why": EN("It starts on the flat third, rubbing against the chord, then lifts to the third.")} for l in (True, False, True)]
    notes = []
    for k in range(4):
        b = k * 4
        notes += [{"beat": b, "length": 0.75, "step": 3, "lyric": "doo"}, {"beat": b + 0.75, "length": 1.25, "step": 4, "lyric": "bah"}]
    model = notes[:2]
    return {
        "id": "sc-4-blue", "title": EN("The blue note"),
        "fact": fact("handy-flat-third-folk-roots", "In his autobiography, W. C. Handy wrote that the flat third and seventh in his major-key blues came from the music of poor Black Southerners. Today we call them blue notes.", "Wikipedia, W. C. Handy", "https://en.wikipedia.org/wiki/W._C._Handy"),
        "steps": [
            learn("The blue note is the flat third sung against a major chord: it rubs on purpose, then lifts to the third. No pushing on the bend.",
                  [("Flat third", "Against the major chord"), ("It rubs", "On purpose"), ("Then lift", "To the third")]),
            choose("Listen to each, then choose.", rounds),
            play("Flat third, then third, four times over I7.", exercise(notes, ["I"] * 4), "Scored on your notes on pitch."),
            selfcheck("Once more, then hear yours beside the guide's.", model, ["Did it bend, or jump?", "Did your throat stay easy?"]),
        ],
    }


def sc_4_scale():
    up = [-2, 0, 3, 5, 6, 7]
    line, _ = swung(["e"] * 12 + ["h"], up + list(reversed(up)) + [0], ["bee", "dah"] * 6 + ["doo"])
    return {
        "id": "sc-4-scale", "title": EN("The blues scale"),
        "fact": fact("limb-braun-2008", "In brain scans of jazz pianists improvising, an area linked to self-monitoring quietened, while one at the front of the brain grew more active.",
                     "Limb and Braun, PLoS ONE (2008)", "https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0001679"),
        "steps": [
            learn("The blues scale is the riff's five notes plus the flat five, another blue note: flat seven, do, flat three, four, flat five, five.",
                  [("The riff's notes", "Five you know"), ("Plus flat five", "Another blue note"), ("Up and down", "Swung, \"bee-dah\"")]),
            play("Up the blues scale and down, swung.", exercise(line, ["I", "I", "I", "I"]), PITCH_SWING, rhythm="swing"),
        ],
    }


def solo(tokens_steps_words, chords, scale=True):
    notes, names = [], []
    for k, ((tokens, steps, words), chord) in enumerate(zip(tokens_steps_words, chords)):
        ph, _ = swung(tokens, steps, words, k * 8)
        options = within(BLUES) if scale else lit(chord)
        for n in ph[:-1]:
            n["choices"] = options
        ph[-1]["choices"] = lit(chord)
        # The written line sings only notes the step accepts, as trade() does: each on its nearest lit
        # note, a tie going up (mi to four, not the flat third every time).
        for n in ph:
            n["step"] = min(n["choices"], key=lambda s: (abs(s - n["step"]), -s))
        notes += ph
        names += [chord] * 2
    return notes, names


def sc_4_four():
    notes, names = solo([CALLS[0], CALLS[2]], ["I", "I"])
    return {
        "id": "sc-4-four", "title": EN("Four bars of your own"),
        "fact": fact("gonsalves-27-choruses", "At the 1956 Newport Jazz Festival, Paul Gonsalves soloed for 27 choruses in Duke Ellington's Diminuendo and Crescendo in Blue. The seated crowd rose to dance, and the night revived Ellington's career.", "Wikipedia, Ellington at Newport", "https://en.wikipedia.org/wiki/Ellington_at_Newport"),
        "steps": [
            learn("Four bars, every note your choice from the blues scale, the last on one of the chord's tones. No wrong notes: everything lit fits.",
                  [("A rhythm", "Written for you"), ("The notes", "Any of the blues scale"), ("The last", "A chord tone")]),
            play("Your four bars over I7.", exercise(notes, names), LANDED, rhythm="swing"),
        ],
    }


def sc_4_challenge():
    notes, names = trades([(0, "I"), (2, "IV")])
    own, own_names = solo([CALLS[3], CALLS[1]], ["V", "I"])
    for n in own:
        n["beat"] = round(n["beat"] + 32, 4)
    notes += own
    names += own_names
    ex = exercise(notes, names, tempo=84)
    return {
        "id": "sc-4-challenge", "title": EN("Your chorus"), "challenge": True,
        "steps": [
            learn("Lesson 1's trades, then a chorus: eight bars of trading (unit 3), then four bars all yours from the blues scale, with space between phrases, as a blues lyric breathes.",
                  [("Then and now", "Lesson 1's trades"), ("Trade", "Eight bars with the band"), ("Then solo", "Four bars of your own")]),
            play("Lesson 1's four trades again.", first_trades(thenAndNow="sc.first-trade"), LANDED, rhythm="swing"),
            play("Your chorus.", ex, LANDED, rhythm="swing"),
            selfcheck("Once more, your last four bars, then hear yours.", own[:7], ["Did it swing, or march?", "Did your jaw stay loose?"], 84),
        ],
    }


course = {
    "id": "scat", "version": 1, "reviewed": False, "title": EN("Scat singing"),
    "units": [
        {"id": "sc-the-swing-pocket", "title": EN("The swing pocket"), "colour": 3, "lessons": [sc_1_trade(), sc_1_swing(), sc_1_and(), sc_1_challenge()]},
        {"id": "sc-the-form", "title": EN("The form and the landing"), "colour": 3, "lessons": [sc_2_form(), sc_2_finish(), sc_2_third(), sc_2_challenge()]},
        {"id": "sc-call-and-response", "title": EN("Call and response"), "colour": 3, "lessons": [sc_3_ends(), sc_3_answer(), sc_3_riff(), sc_3_challenge()]},
        {"id": "sc-the-blues", "title": EN("The blues"), "colour": 3, "lessons": [sc_4_blue(), sc_4_scale(), sc_4_four(), sc_4_challenge()]},
    ],
}
for where in add_breaths(course):
    print("no room to breathe:", where)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"))
