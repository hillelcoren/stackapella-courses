"""Sea shanties and work songs (docs/courses/sea-shanties.md in the app's repo): writes
course/plus/sea-shanties/course.json. Built from the courses lead's outline, as revised by a voice-teacher review
and a game-design review: the crew's answers on pitch first, then the pull on the beat, then the shantyman's
call, then a crew of you, kept as a song.

Work in progress (2026-11-08): this has Haul Away, Joe (Sharp 1914 No. 27) and Blow the Man Down (Whall 1913),
both from the library's templates. Drunken Sailor (lesson 1, the finale) and Leave Her, Johnny (the capstan song)
wait for the arranger's pre-1927 sources, so the course stays "soon" and this file writes no course.json until
they're in (WRITE below).

Every line is `beat:length step [word], ...` in the template's own beats (re-timed so a passage starts at 0),
steps from the singer's comfortable note (do = 0). The checks fail the build on:
- a sung note outside -5 to +9;
- a `rhythm` step with fewer than four timed moments (the scoring guard: three is too few to judge);
- a unit 1 lesson whose last scored step is timed (unit 1 is pitch only);
- an `entry` step as a lesson's last scored step (`entry` has no one-star floor);
- a lesson with partners singing under you and no `headphones: "needed"`, or one without them that has it;
- the house words: no "star", "stars" or "starboard", no em dashes, none of the words the voice-teacher review
  ruled out (shout, yell, loud...), and no letter names.

    python3 -I tools/sh_course.py && python3 -I tools/coursefmt.py course/plus/sea-shanties/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/sea-shanties/course.json"
WRITE = False  # until Drunken Sailor and Leave Her, Johnny are sourced: the course must open on lesson 1's chorus

BANNED = re.compile(r"\bstars?\b|starboard|—|\bshout|\byell|\bbellow|\broar|\bbelt\b|\bpush|as loud as|\blouder\b|\bpower", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)

LOW, HIGH = -5, 9  # the span: steps from the singer's comfortable note
COLOUR = 2
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
EPS = 1e-9

SAFE = "stop if anything tightens or hurts"
BIG = ("As big as you could keep up", "Like calling a friend across a garden")
BODY = ("Pull with your body", f"Never your throat; {SAFE}")
HEADPHONES = ("Headphones on", "Through a speaker, the crew rests while you sing")
PITCH = "Scored on your answers on pitch."
BEAT = "Scored on your answers on pitch and on the beat."
CHOSE = "Scored on the rounds you got right first time."


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def num(x):
    x = round(x, 6)
    return int(x) if x == int(x) else x


def L(text, lyric="oo", shift=0):
    """`beat:length step [word], ...` in template beats, moved back by `shift`."""
    out = []
    for token in text.split(","):
        when, step, *word = token.split()
        beat, length = when.split(":")
        n = {"beat": num(float(beat) - shift), "length": num(float(length)), "step": int(step)}
        word = word[0] if word else lyric
        if word:
            n["lyric"] = word
        out.append(n)
    return out


def end_of(notes):
    return max(n["beat"] + n["length"] for n in notes)


class Song:
    """A library template: its shantyman's line (the soprano) and chords, in steps from its do, `down` steps lower
    so the crew's answers sit in the course's span."""

    def __init__(self, name, down):
        data = json.loads((REPO / "templates" / "library" / f"{name}.json").read_text())
        key = KEYS[data["key"].rstrip("m")]
        do = 60 + key
        self.name, self.tempo, self.down = name, data["tempo"], down
        self.tune = [(n["beat"], n["length"], n["pitch"] - do - down, n.get("lyric")) for n in data["parts"][0]["guide"]["notes"]]
        self.chords = [(c["beat"], (c["root"] - key - down) % 12, c["quality"]) for c in data["chords"]]
        self.bounds = {b for s in data["sections"] for p in s["phrases"] for b in p}
        self.parts = {p["key"]: [(n["beat"], n["length"], n["pitch"] - do - down, n.get("lyric")) for n in p["guide"]["notes"]]
                      for p in data["parts"]}

    def crew(self, frm, to, parts=("alto", "tenor", "bass")):
        """The guide's crew: the template's lower parts from `frm` to `to`, one partner line each, re-timed to 0."""
        return [{"notes": [{"beat": num(b - frm), "length": num(length), "step": p, **({"lyric": w} if w else {})}
                           for b, length, p, w in self.parts[k] if frm <= b < to]} for k in parts if k in self.parts]

    def notes(self, frm, to):
        """The tune from `frm` to `to`, re-timed to start at 0, words kept (a note with no word is held over)."""
        assert frm in self.bounds and to in self.bounds, f"{self.name}: {frm} to {to} is not whole phrases"
        return [{"beat": num(b - frm), "length": num(length), "step": p, **({"lyric": w} if w and w != "~" else {})}
                for b, length, p, w in self.tune if frm <= b < to]

    def chords_at(self, frm, to):
        sounding = [c for c in self.chords if c[0] <= frm + EPS][-1]
        inside = [c for c in self.chords if frm + EPS < c[0] < to - EPS]
        return [{"beat": num(b - frm), "root": r, "quality": q} for b, r, q in [(frm,) + sounding[1:]] + inside]

    def calls(self, frm, to, calls):
        """The guide's crew-less line: only the notes in the `calls` ranges (template beats), as a partner."""
        keep = [n for n in self.notes(frm, to) if any(a <= n["beat"] + frm < b for a, b in calls)]
        return {"notes": keep}


# Haul Away, Joe: Sharp, English Folk-Chanteys (1914) No. 27, as John Short of Watchet sang it; the template is
# in C# minor, the answer "Way, haul away, haul away, Joe" from the octave down to do. Down 5, the answer sits
# from -5 to +7 and the calls reach +10 (the guide sings them).
JOE = Song("haul-away-joe", 5)
# Blow the Man Down: Whall, Ships, Sea Songs and Shanties (1913); the template is in F at 150 in 3/4. The
# answers sit from 0 to +9 as written; the course takes it slower first (the voice-teacher review).
BLOW = Song("blow-the-man-down", 0)
BLOW_SLOW = 120
# Leave Her, Johnny: Sharp 1914 No. 2, John Short's capstan shanty, E dorian at 90; the soprano sings the solos,
# everyone the choruses. Down 1, the choruses sit from -3 to +6 and the solos from -3 to +9. No pull marks in
# the print, as a capstan song should be: the crew walked the bars round.
LEAVE = Song("leave-her-johnny", 1)


def card(title, detail):
    assert len(title) <= 40 and len(title.split()) <= 9, f"a card title is short: {title}"
    assert len(detail) <= 72 and "\n" not in detail and ". " not in detail, f"a card's detail is one line: {detail}"
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual):
    assert len(cards) <= 3, headline
    assert any(SAFE in d for _, d in cards), f"every learn step carries the safety line: {headline}"
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def find(text, notes, tempo):
    """Wait for me: each note waits until you're on it."""
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes}}


def call_answer(text, call, answer, tempo, measures=PITCH, *, chords=None, **extra):
    """Hear the call, then sing the answer back (`turn` with `answer`): nothing sounds under you."""
    ex = {"tempo": tempo, "turn": True, "notes": call, "answer": answer}
    if chords:
        ex["chords"] = chords
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def with_crew(text, notes, tempo, partners, measures=PITCH, *, chords=None, **extra):
    """Sing your line while the guide sings the other lines (`with`): they sound under you, so headphones."""
    ex = {"tempo": tempo, "turn": False, "notes": notes, "with": partners if isinstance(partners, list) else [partners]}
    if chords:
        ex["chords"] = chords
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def choose(text, tempo, rounds):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": [
        {"prompt": EN(p), "clips": clips, "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


def selfcheck(text, tempo, model, questions):
    return {"kind": "selfcheck", "text": EN(text),
            "exercise": {"tempo": tempo, "model": model, "along": True, "questions": [EN(q) for q in questions]}}


# ---- The checks ----

def sung(ex):
    return ex.get("answer") or ex.get("notes") or []


def timed_moments(notes, tempo):
    """scoreTake's timed moments: the first note, each note after a rest of 0.1 s or more, each change of a
    semitone or more."""
    bs = 60 / tempo
    ordered = sorted(notes, key=lambda n: n["beat"])
    k = 0
    for i, n in enumerate(ordered):
        if i == 0 or (n["beat"] - (ordered[i - 1]["beat"] + ordered[i - 1]["length"])) * bs >= 0.1 or n["step"] != ordered[i - 1]["step"]:
            k += 1
    return k


def judged_entries(notes):
    ordered = sorted(notes, key=lambda n: n["beat"])
    return [b["beat"] for a, b in zip(ordered, ordered[1:]) if b["beat"] - (a["beat"] + a["length"]) >= 0.25 - EPS]


def scored(step):
    return step["kind"] in ("play", "choose") and not step.get("exercise", {}).get("unscored")


def check(lid, unit, steps, headphones):
    last = max(i for i, s in enumerate(steps) if scored(s))
    under_you = False
    for i, step in enumerate(steps):
        where = f"sh-{lid} step {i + 1}"
        ex = step.get("exercise", {})
        if step["kind"] in ("play", "try"):
            for n in sung(ex):
                assert LOW <= n["step"] <= HIGH, f"{where}: step {n['step']} at beat {n['beat']} is outside {LOW} to {HIGH}"
        if step["kind"] == "play":
            under_you = under_you or bool(ex.get("with") or ex.get("under"))
            if "rhythm" in ex:
                assert "score" not in ex, f"{where}: rhythm only on a default-scored step"
                assert timed_moments(sung(ex), ex["tempo"]) >= 4, f"{where}: a rhythm step needs four timed moments"
                assert unit > 1, f"{where}: unit 1 is pitch only"
            if ex.get("score") == "entry":
                assert len(judged_entries(sung(ex))) >= 3, f"{where}: an entry step needs three or more answers"
                assert i != last, f"{where}: entry has no one-star floor, so it's never the lesson's last scored step"
    assert under_you == headphones, f"sh-{lid}: headphones needed exactly where the crew or your takes sing under you"


def lesson(lid, unit, title, steps, **extra):
    headphones = extra.pop("headphones", False)
    check(lid, unit, steps, headphones)
    out = {"id": f"sh-{lid}", "title": EN(title), **extra, "steps": steps}
    if headphones:
        out["headphones"] = "needed"
    return out


# ---- Haul Away, Joe: sweating up ----

J_CHORUS = (0, 16)  # "Haul away, haul away, haul away my Rosie" (the call), "Way, haul away, haul away, Joe" (the answer)
J_VERSE1 = (16, 32)
J_ANSWER_AT = (9, 16)
J_ANSWER = JOE.notes(*J_CHORUS)[-8:]  # the answer's eight notes, re-timed below
J_ANSWER = [dict(n, beat=num(n["beat"] - 9)) for n in J_ANSWER]
J_CALL = [n for n in JOE.notes(*J_CHORUS) if n["beat"] < 9]
assert [n["lyric"] for n in J_ANSWER] == ["Way,", "haul", "a-", "way,", "haul", "a-", "way,", "Joe."], J_ANSWER

# ---- Blow the Man Down: the long hoist ----

B_CALL1, B_ANSWER1 = BLOW.notes(0, 13), [dict(n, beat=num(n["beat"] - 13)) for n in BLOW.notes(13, 24)]
B_CALL2, B_ANSWER2 = BLOW.notes(24, 37), [dict(n, beat=num(n["beat"] - 37)) for n in BLOW.notes(37, 48)]
assert B_ANSWER1[0]["lyric"] == "Way-" and B_ANSWER2[0]["lyric"] == "Give", (B_ANSWER1, B_ANSWER2)


# The song as it goes, for the beat: your answers with the guide's calls as a partner line, chords on the
# step's own timeline. A turn step (hear, then answer) puts a beat's gap between call and answer, which is no
# song's own rhythm, so turn steps are pitch only and carry no chords (they'd sit on the wrong beats).

def answers(song, ranges, frm):
    """The soprano's notes in `ranges` (template beats), re-timed from `frm`: the crew's answers."""
    return [dict(n, beat=num(n["beat"] + frm - frm)) for n in song.notes(frm, max(z for _, z in ranges))
            if any(a <= n["beat"] + frm < z for a, z in ranges)]


J_SONG = (0, 32)  # the chorus and verse 1
J_ANSWERS = answers(JOE, [(9, 16), (25, 32)], 0)
J_CALLS = JOE.calls(*J_SONG, [(0, 9), (16, 25)])
B_SONG = (0, 48)  # the first call and its two answers
B_ANSWERS = answers(BLOW, [(13, 24), (37, 48)], 0)
B_CALLS = BLOW.calls(*B_SONG, [(0, 13), (24, 37)])
B_VCALL = BLOW.notes(48, 61)  # verse 1's call, a fifth above the crew's last note
assert B_VCALL[0]["step"] - B_ANSWER2[-1]["step"] == 7, (B_VCALL[0], B_ANSWER2[-1])

L_VERSE = (0, 32)
L_TWO = (0, 64)
L_SOLOS = [(0, 9), (16, 24.5), (32, 41), (48, 56.5)]
L_CHORUSES = [(9, 16), (24.5, 32), (41, 48), (56.5, 64)]
L_CALL1, L_ANSWER1 = LEAVE.notes(0, 9), [dict(n, beat=num(n["beat"] - 9)) for n in LEAVE.notes(9, 16)]


def verse(song, span, ranges):
    frm, to = span
    return [n for n in song.notes(frm, to) if any(a <= n["beat"] + frm < z for a, z in ranges)]


UNIT1_LESSONS = [
    # sh-1-answer (Drunken Sailor's chorus, lesson 1) waits for the arranger's Sharp No. 7.
    lesson("1-joe", 1, "Sweating up", [
        learn("Haul Away, Joe was for sweating up: one short answer and one strong pull, to get the last inch out of a rope. The shantyman calls, and the crew answers.", [
            BIG, BODY, ("The pull comes at the end", "On \"Joe\", short and sung"),
        ], "phrase"),
        find("Find the answer's notes. Each waits until you're on it.", J_ANSWER, JOE.tempo),
        call_answer("Hear the call, then answer: \"Way, haul away, haul away, Joe\". Breathe in the call.",
                    J_CALL, J_ANSWER, JOE.tempo),
    ]),
    lesson("1-breathe", 1, "Breathe in the call", [
        learn("Blow the Man Down hoisted a sail: the long hoist. While the shantyman sang, the crew shifted their hands on the rope and took a breath, low and quiet.", [
            ("Breathe in the call", "Low and quiet, in the shantyman's last words"),
            ("One breath an answer", "No breath halfway through"),
            BODY,
        ], "phrase"),
        find("Find the first answer's notes: \"Way-ay, blow the man down\".", B_ANSWER1, BLOW_SLOW),
        call_answer("Hear the call, then answer. Take your breath in the call's last word.",
                    B_CALL1, B_ANSWER1, BLOW_SLOW),
        call_answer("The second answer now: \"Give me some time to blow the man down\".",
                    B_CALL2, B_ANSWER2, BLOW_SLOW),
    ]),
]

UNIT2_LESSONS = [
    lesson("2-pull", 2, "On the pull", [
        learn("Now the beat: on a real rope, everyone pulled on the same word, or nothing moved. Aim the \"aw\" of \"haul\" at the beat, not the h.", [
            ("The vowel on the beat", "The \"aw\" of \"haul\", the \"oh\" of \"Joe\""),
            ("One strong pull", f"On \"Joe\", short and sung; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("The chorus and a verse: the shantyman calls, you answer on the beat.",
                  J_ANSWERS, JOE.tempo, J_CALLS, BEAT, chords=JOE.chords_at(*J_SONG), rhythm=True),
    ], headphones=True),
    lesson("2-hoist", 2, "The long hoist", [
        learn("A halyard shanty had two short answers, with a double pull in each. Same answers as before, now on the beat, slow first, then at the crew's pace.", [
            ("Two pulls an answer", "Together, on the beat"),
            ("Slow, then the crew's pace", f"Steady before fast; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("Slow first: the call, then your two answers on the beat.",
                  B_ANSWERS, BLOW_SLOW, B_CALLS, BEAT, chords=BLOW.chords_at(*B_SONG), rhythm=True),
        with_crew("Now at the crew's pace.",
                  B_ANSWERS, BLOW.tempo, B_CALLS, BEAT, chords=BLOW.chords_at(*B_SONG), rhythm=True),
    ], headphones=True),
    lesson("2-capstan", 2, "Walk it round", [
        learn("Leave Her, Johnny was a capstan shanty: no pull, the crew walked the capstan bars round and round, so the beat is your feet. It was sung coming into port.", [
            ("A steady walk", "Every answer in on the beat"),
            ("No pull here", f"Just walking, round and round; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        find("Find the chorus's notes: \"Leave her, Johnny, leave her\".", L_ANSWER1, LEAVE.tempo),
        with_crew("A verse: the shantyman sings, you answer each chorus on the beat.",
                  verse(LEAVE, L_VERSE, L_CHORUSES), LEAVE.tempo, LEAVE.calls(*L_VERSE, L_SOLOS), BEAT,
                  chords=LEAVE.chords_at(*L_VERSE), rhythm=True),
    ], headphones=True),
]

UNIT3_LESSONS = [
    # sh-3-lead (Drunken Sailor's call, the tune from lesson 1) waits for the arranger's Sharp No. 7.
    lesson("3-find", 3, "Find the call", [
        learn("Now you're the shantyman. Your first note comes from the crew's last: they end on home, and your call starts a fifth above it.", [
            ("Listen to the crew's last note", "Then go up a fifth"),
            ("You sing alone", f"A big warm voice, never a strain; {SAFE}"),
            BIG,
        ], "phrase"),
        call_answer("The crew answers, then you call: \"As I was a-walking down Paradise Street\".",
                    B_ANSWER2, B_VCALL, BLOW_SLOW),
    ]),
    lesson("3-line", 3, "Make up a line", [
        learn("A shantyman made up new lines as he went, often about the ship. The chorus never changed. Your line fits if it has one syllable for each note.", [
            ("The chorus stays", "Only the shantyman's line is new"),
            ("One syllable a note", f"Say it in rhythm first; {SAFE}"),
            BIG,
        ], "phrase"),
        call_answer("First Sharp's line: hear the call, then sing it back.",
                    L_CALL1, L_CALL1, LEAVE.tempo),
        selfcheck("Your own line to the call's tune: about your day, your street, your week. Then hear yours beside the guide's.",
                  LEAVE.tempo, {"notes": L_CALL1}, ["Did your words fit one a note?", "Did the tune stay the same?"]),
    ]),
    lesson("3-challenge", 3, "Lead Leave Her, Johnny", [
        learn("You lead a whole verse: you sing the shantyman's lines, and the guide's crew answers you in four parts.", [
            ("Your lines alone", "The crew comes in after you"),
            ("Breathe in their chorus", f"Then lead again; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("A verse as the shantyman, the crew answering.",
                  verse(LEAVE, L_VERSE, L_SOLOS), LEAVE.tempo,
                  [p for p in LEAVE.crew(*L_VERSE)], PITCH, chords=LEAVE.chords_at(*L_VERSE), giveNote=True),
    ], challenge=True, headphones=True),
]

course = {
    "id": "sea-shanties", "version": 1, "reviewed": False, "title": EN("Sea shanties and work songs"),
    "units": [
        {"id": "sh-the-crew-answers", "title": EN("The crew answers"), "colour": COLOUR, "lessons": UNIT1_LESSONS},
        {"id": "sh-on-the-pull", "title": EN("On the pull"), "colour": COLOUR, "lessons": UNIT2_LESSONS},
        {"id": "sh-the-shantyman", "title": EN("The shantyman"), "colour": COLOUR, "lessons": UNIT3_LESSONS},
    ],
}

for u in course["units"]:
    for l in u["lessons"]:
        for i, s in enumerate(l["steps"]):
            ex = s.get("exercise") or {}
            if s["kind"] == "play":
                print(f"{l['id']}[{i}] {len(sung(ex))} notes, {timed_moments(sung(ex), ex['tempo'])} timed moments{', rhythm' if ex.get('rhythm') else ''}")
if WRITE:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(course, open(OUT, "w"))
