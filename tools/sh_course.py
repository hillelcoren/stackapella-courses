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
WRITE = True

BANNED = re.compile(r"\bstars?\b|starboard|—|\bshout|\byell|\bbellow|\broar|\bbelt\b|\bpush|as loud as|\blouder\b|\bpower", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)

LOW, HIGH = -5, 9  # the span: steps from the singer's comfortable note
COLOUR = 2
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
EPS = 1e-9

SAFE = "stop if anything tightens or hurts"
BIG = ("As big as you could keep up", "Like calling a friend across a garden")
BODY = ("Pull with your body", f"Never your throat; {SAFE}")
HEADPHONES = ("Headphones on", "Through a speaker, the crew rests while you sing")  # a lesson singing over the crew
SPEAKER_OK = ("Headphones or a speaker", "The calls sound in your rests either way")
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
# Drunken Sailor: Terry, The Shanty Book Part I (1921) No. 14, checked against Whall (1913) p. 107, E dorian at 88,
# one printed quaver a beat; the shantyman's verse (0 to 32), then everyone's chorus, "Hooray and up she rises", as
# Terry prints it (no printing has "Way, hey"). Down 3, verse and chorus sit from -5 to +9; the tenor sits from -3
# to +7 an octave up. No pull marks: it was stamp and go, walked.
SAILOR = Song("drunken-sailor", 3)
KEEP = "shanties.first-answer"


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


# Through a speaker (the app's speakerPartnerNotes, d609a49d1): a run of joined partner notes keeps sounding
# only when it's clear of every note you sing, ending 0.4 s before it or starting 0.15 s after it. The chords
# rest either way, which a shanty can lose (they were sung unaccompanied); a dropped call or crew line can't.
CALL_CLEAR_BEFORE, CALL_CLEAR_AFTER = 0.4, 0.15


def speaker_drops(ex):
    """How many partner notes a speaker drops in a `turn: false` step (a turn step has no partners)."""
    if not ex.get("with"):
        return 0
    bs, target = 60 / ex["tempo"], ex["notes"]
    until = min(n["beat"] for n in target)
    lost = 0
    for line in ex["with"]:
        runs = []
        for n in sorted((n for n in line["notes"] if n["beat"] >= until), key=lambda n: n["beat"]):
            if runs and abs(end_of(runs[-1]) - n["beat"]) < 1e-6:
                runs[-1].append(n)
            else:
                runs.append([n])
        for run in runs:
            a, z = run[0]["beat"] * bs, end_of(run) * bs
            if not all(z <= t["beat"] * bs - CALL_CLEAR_BEFORE or a >= (t["beat"] + t["length"]) * bs + CALL_CLEAR_AFTER for t in target):
                lost += len(run)
    return lost


def scored(step):
    return step["kind"] in ("play", "choose") and not step.get("exercise", {}).get("unscored")


def check(lid, unit, steps, headphones):
    last = max(i for i, s in enumerate(steps) if scored(s))
    under_you = False
    for i, step in enumerate(steps):
        where = f"sh-{lid} step {i + 1}"
        ex = step.get("exercise", {})
        if step["kind"] in ("play", "try"):
            for line in [ex.get("notes", []), ex.get("answer", [])] + [w["notes"] for w in ex.get("with", [])]:
                assert all(n["beat"] >= 0 and n["length"] > 0 for n in line), f"{where}: a note before beat 0, or with no length"
            for n in sung(ex):
                assert LOW <= n["step"] <= HIGH, f"{where}: step {n['step']} at beat {n['beat']} is outside {LOW} to {HIGH}"
        if step["kind"] == "play":
            under_you = under_you or bool(ex.get("under")) or speaker_drops(ex) > 0
            if "rhythm" in ex:
                assert "score" not in ex, f"{where}: rhythm only on a default-scored step"
                assert timed_moments(sung(ex), ex["tempo"]) >= 4, f"{where}: a rhythm step needs four timed moments"
                assert unit > 1, f"{where}: unit 1 is pitch only"
            if ex.get("score") == "entry":
                assert len(judged_entries(sung(ex))) >= 3, f"{where}: an entry step needs three or more answers"
                assert i != last, f"{where}: entry has no one-star floor, so it's never the lesson's last scored step"
    assert under_you == headphones, f"sh-{lid}: headphones needed exactly where a speaker would drop the crew or your takes"


TONES = {"maj": [0, 4, 7], "min": [0, 3, 7], "dom7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10]}


def check_layers(where, steps, i):
    """A layer over your own earlier take: never on its note for more than a beat (a unison with yourself swallows
    your layer), but for a line's last word (its last two notes), where a crew ends together.
    The parts are the arranger's checked harmony (passing tones included), and the root line is built from the
    chords, so neither needs a chord check here."""
    ex = steps[i]["exercise"]
    for k in ex["under"]["steps"]:
        assert k < i, f"{where}: a layer is an earlier step"
        last = sorted(n["beat"] for n in ex["notes"])[-2]
        for n in ex["notes"]:
            for m in steps[k]["exercise"]["notes"]:
                overlap = min(n["beat"] + n["length"], m["beat"] + m["length"]) - max(n["beat"], m["beat"])
                assert n["beat"] >= last or not (overlap > 1 + EPS and n["step"] == m["step"]), f"{where}: a unison with step {k + 1} at beat {n['beat']}"


def lesson(lid, unit, title, steps, **extra):
    headphones = extra.pop("headphones", False)
    check(lid, unit, steps, headphones)
    for i, st in enumerate(steps):
        if st["kind"] == "play" and st["exercise"].get("under"):
            check_layers(f"sh-{lid} step {i + 1}", steps, i)
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

B_CALL1, B_ANSWER1 = BLOW.notes(0, 13), BLOW.notes(13, 24)  # notes() re-times each passage from 0
B_CALL2, B_ANSWER2 = BLOW.notes(24, 37), BLOW.notes(37, 48)
assert B_ANSWER1[0]["lyric"] == "Way-" and B_ANSWER2[0]["lyric"] == "Give", (B_ANSWER1, B_ANSWER2)


# The song as it goes, for the beat: your answers with the guide's calls as a partner line, chords on the
# step's own timeline. A turn step (hear, then answer) puts a beat's gap between call and answer, which is no
# song's own rhythm, so turn steps are pitch only and carry no chords (they'd sit on the wrong beats).

def answers(song, ranges, frm):
    """The soprano's notes in `ranges` (template beats), re-timed from `frm`: the crew's answers."""
    return [dict(n, beat=num(n["beat"] + frm - frm)) for n in song.notes(frm, max(z for _, z in ranges))
            if any(a <= n["beat"] + frm < z for a, z in ranges)]


J_SONG = (0, 80)  # the chorus, three verses and the chorus: five answers, enough moments that one noisy onset
# can't cost a singer on time the third mark (the scoring guard, 80 ms behind with onset noise, 2026-11-08)
J_ANSWERS = answers(JOE, [(9, 16), (25, 32), (41, 48), (57, 64), (73, 80)], 0)
J_CALLS = JOE.calls(*J_SONG, [(0, 9), (16, 25), (32, 41), (48, 57), (64, 73)])
B_SONG = (0, 48)  # the first call and its two answers
B_ANSWERS = answers(BLOW, [(13, 24), (37, 48)], 0)
B_CALLS = BLOW.calls(*B_SONG, [(0, 13), (24, 37)])
B_VCALL = BLOW.notes(48, 61)  # verse 1's call, a fifth above the crew's last note
assert B_VCALL[0]["step"] - B_ANSWER2[-1]["step"] == 7, (B_VCALL[0], B_ANSWER2[-1])

L_VERSE = (0, 32)
L_TWO = (0, 64)
L_SOLOS = [(0, 9), (16, 24.5), (32, 41), (48, 56.5)]
L_CHORUSES = [(9, 16), (24.5, 32), (41, 48), (56.5, 64)]
L_CALL1, L_ANSWER1 = LEAVE.notes(0, 9), LEAVE.notes(9, 16)


def verse(song, span, ranges):
    frm, to = span
    return [n for n in song.notes(frm, to) if any(a <= n["beat"] + frm < z for a, z in ranges)]


D_VERSE, D_CHORUS, D_SONG = (0, 32), (32, 64), (0, 64)
D_ANSWER = SAILOR.notes(*D_CHORUS)  # the chorus alone, from 0
D_LINE = D_ANSWER[:7]  # "Hooray and up she rises", the first line
assert [n["lyric"] for n in D_LINE] == ["Hoo-", "ray", "and", "up", "she", "ri-", "ses,"], D_LINE
D_CALL_LINE = SAILOR.notes(0, 8)
D_SINGS = SAILOR.notes(*D_SONG)
D_CHORUS_SUNG = [n for n in D_SINGS if n["beat"] >= 32]  # your chorus, after the shantyman's verse
D_VERSE_SUNG = [n for n in D_SINGS if n["beat"] < 32]
D_CALLS = SAILOR.calls(*D_SONG, [D_VERSE])
D_CREW = SAILOR.crew(*D_SONG) + [SAILOR.calls(*D_SONG, [D_CHORUS])]  # the guide's crew, all four parts, on the chorus
# The part under the tune: the alto, from the arranger's setting of Terry's harmony (the tenor an octave up would
# double the tune). Three notes leave the span, so the course sets them: "in" (beat 58) holds the -1 before it, in
# the chord, and "morn-ing" ends in unison with the tune on home, a crew's close.
SET = {58: -1, 60: -3, 62: -3}
D_PART = [{"beat": num(b), "length": num(length), "step": SET.get(b, p), **({"lyric": w} if w else {})}
          for b, length, p, w in SAILOR.parts["alto"] if 32 <= b < 64]
# The root: each chord's root, held to the next change, on "doom", from the course's low end up. Sung under the
# guide's tune only (sh-4-root): in one singer's span it meets the tune on its roots, so it's never layered over
# your own chorus.
def roots(song, frm, to):
    cs = [c for c in song.chords if frm <= c[0] < to]
    out = []
    for (b, r, _q), nxt in zip(cs, cs[1:] + [(to, None, None)]):
        step = r if r <= 4 else r - 12
        out.append({"beat": num(b), "length": num(nxt[0] - b), "step": step, "lyric": "doom"})
    return out
D_ROOT = roots(SAILOR, 32, 64)
B_ALTO = [{"beat": num(b), "length": num(length), "step": p, **({"lyric": w} if w else {})}
          for b, length, p, w in BLOW.parts["alto"] if any(a <= b < z for a, z in [(13, 24), (37, 48)])]


UNIT1_LESSONS = [
    lesson("1-answer", 1, "The answer", [
        learn("A shanty is a work song: the shantyman sings, and the crew answers together. In Drunken Sailor the crew's answer is \"Hooray and up she rises\".", [
            BIG, BODY, SPEAKER_OK,
        ], "phrase"),
        find("Find the answer's notes. Each waits until you're on it.", D_LINE, SAILOR.tempo),
        call_answer("Hear the shantyman's line, then answer: \"Hooray and up she rises\".",
                    D_CALL_LINE, D_LINE, SAILOR.tempo),
        with_crew("Now the whole song: the shantyman sings the verse, then you sing the chorus, all four lines.",
                  D_CHORUS_SUNG, SAILOR.tempo, D_CALLS, PITCH, chords=SAILOR.chords_at(*D_SONG), generous=True, keep=KEEP),
    ]),
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
    lesson("1-challenge", 1, "Haul Away, Joe", [
        learn("A whole song as the crew: the chorus, then three verses, each answered with \"Way, haul away, haul away, Joe\".", [
            ("Breathe in the call", "One breath an answer"),
            BODY, SPEAKER_OK,
        ], "phrase"),
        with_crew("The whole song: the shantyman calls, you answer every time.",
                  answers(JOE, [(9, 16), (25, 32), (41, 48), (57, 64), (73, 80)], 0), JOE.tempo,
                  JOE.calls(0, 80, [(0, 9), (16, 25), (32, 41), (48, 57), (64, 73)]), PITCH, chords=JOE.chords_at(0, 80)),
    ], challenge=True),
]

UNIT2_LESSONS = [
    lesson("2-pull", 2, "On the pull", [
        learn("Now the beat: on a real rope, everyone pulled on the same word, or nothing moved. Aim the \"aw\" of \"haul\" at the beat, not the h.", [
            ("The vowel on the beat", "The \"aw\" of \"haul\", the \"oh\" of \"Joe\""),
            ("One strong pull", f"On \"Joe\", short and sung; {SAFE}"),
            SPEAKER_OK,
        ], "phrase"),
        with_crew("The whole song: the shantyman calls, you answer every time on the beat.",
                  J_ANSWERS, JOE.tempo, J_CALLS, BEAT, chords=JOE.chords_at(*J_SONG), rhythm=True),
    ]),
    lesson("2-stamp", 2, "Stamp and go", [
        learn("Drunken Sailor was stamp and go: a big crew grabbed the rope and tramped away along the deck with it, so the beat is your feet. It was also sung at the capstan.", [
            ("The beat is your feet", "Walk it if you like"),
            ("Hooray on the beat", f"The \"oo\", not the h; {SAFE}"),
            SPEAKER_OK,
        ], "phrase"),
        with_crew("The verse from the shantyman, then your chorus on the beat.",
                  D_CHORUS_SUNG, SAILOR.tempo, D_CALLS, BEAT, chords=SAILOR.chords_at(*D_SONG), rhythm=True),
    ]),
    lesson("2-hoist", 2, "The long hoist", [
        learn("A halyard shanty had two short answers, with a double pull in each. Same answers as before, now on the beat, at a steady hoist.", [
            ("Two pulls an answer", "Together, on the beat"),
            ("A steady hoist", f"Steady before fast; {SAFE}"),
            SPEAKER_OK,
        ], "phrase"),
        # At the template's 150 the beat window is at its 60 ms floor and a beginner's take fell to one mark (the
        # unit-by-unit simulation, 2026-11-08), so the hoist stays at 120.
        with_crew("The call, then your two answers on the beat.",
                  B_ANSWERS, BLOW_SLOW, B_CALLS, BEAT, chords=BLOW.chords_at(*B_SONG), rhythm=True),
    ]),
    lesson("2-capstan", 2, "Walk it round", [
        learn("Leave Her, Johnny was a capstan shanty: no pull, the crew walked the capstan bars round and round, so the beat is your feet. It was sung coming into port.", [
            ("A steady walk", "Every answer in on the beat"),
            ("No pull here", f"Just walking, round and round; {SAFE}"),
            SPEAKER_OK,
        ], "phrase"),
        find("Find the chorus's notes: \"Leave her, Johnny, leave her\".", L_ANSWER1, LEAVE.tempo),
        with_crew("A verse: the shantyman sings, you answer each chorus on the beat.",
                  verse(LEAVE, L_VERSE, L_CHORUSES), LEAVE.tempo, LEAVE.calls(*L_VERSE, L_SOLOS), BEAT,
                  chords=LEAVE.chords_at(*L_VERSE), rhythm=True),
    ]),
    lesson("2-challenge", 2, "Into port", [
        learn("Two verses of Leave Her, Johnny, the last song of a voyage: every chorus on the beat, walked round the capstan.", [
            ("Every answer on the beat", "Walk it round"),
            ("Breathe in the solo", f"Then answer; {SAFE}"),
            SPEAKER_OK,
        ], "phrase"),
        with_crew("Two verses: you answer every chorus on the beat.",
                  verse(LEAVE, L_TWO, L_CHORUSES), LEAVE.tempo, LEAVE.calls(*L_TWO, L_SOLOS), BEAT,
                  chords=LEAVE.chords_at(*L_TWO), rhythm=True),
    ], challenge=True),
]

UNIT3_LESSONS = [
    lesson("3-lead", 3, "Lead the call", [
        learn("Now you're the shantyman: you sing Drunken Sailor's verse alone, and the guide's crew answers you with the chorus you know.", [
            ("You sing alone", f"A big warm voice, never a strain; {SAFE}"),
            ("The crew answers", "In four parts, after your verse"),
            SPEAKER_OK,
        ], "phrase"),
        with_crew("Your verse, then the crew's chorus.",
                  D_VERSE_SUNG, SAILOR.tempo, D_CREW, PITCH, chords=SAILOR.chords_at(*D_SONG), giveNote=True),
    ]),
    lesson("3-find", 3, "Find the call", [
        learn("Your first note comes from the crew's last: they end on home, and your call starts a fifth above it.", [
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
            SPEAKER_OK,
        ], "phrase"),
        with_crew("A verse as the shantyman, the crew answering.",
                  verse(LEAVE, L_VERSE, L_SOLOS), LEAVE.tempo, LEAVE.crew(*L_VERSE), PITCH,
                  chords=LEAVE.chords_at(*L_VERSE), giveNote=True),
    ], challenge=True),
]

UNIT4_LESSONS = [
    lesson("4-together", 4, "All together", [
        learn("A crew sings the chorus together. Sing Drunken Sailor's chorus with the guide's crew in four parts, your voice inside theirs.", [
            ("Inside the crew", "Hear the others as you sing"),
            BODY, HEADPHONES,
        ], "phrase"),
        with_crew("The verse, then the chorus with the whole crew.",
                  D_CHORUS_SUNG, SAILOR.tempo, D_CALLS["notes"] and [D_CALLS] + SAILOR.crew(*D_SONG), PITCH,
                  chords=SAILOR.chords_at(*D_SONG)),
    ], headphones=True),
    lesson("4-part", 4, "A part under the tune", [
        learn("Now a part of your own: a line under the tune, from Terry's harmony. It moves less than the tune does, and ends with it on home.", [
            ("Under the tune", "Lower, and steadier"),
            ("Hold your line", f"Let the tune go by; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        find("Find the part's notes. Each waits until you're on it.", [dict(n, beat=num(n["beat"] - 32)) for n in D_PART], SAILOR.tempo),
        with_crew("The chorus: your part under the guide's tune.",
                  D_PART, SAILOR.tempo, [D_CALLS, SAILOR.calls(*D_SONG, [D_CHORUS])], PITCH, chords=SAILOR.chords_at(*D_SONG)),
    ], headphones=True),
    lesson("4-root", 4, "The root", [
        learn("Under every chord is its root, the note the crew stands on. Sing the root of each chord, held on \"doom\", while the tune goes over you.", [
            ("One note a chord", "Held until the chord changes"),
            ("Low and easy", f"Never pressed; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("The chorus: the roots under the guide's tune.",
                  D_ROOT, SAILOR.tempo, [D_CALLS, SAILOR.calls(*D_SONG, [D_CHORUS])], PITCH, chords=SAILOR.chords_at(*D_SONG)),
    ], headphones=True),
    lesson("4-stack", 4, "Stack a crew", [
        learn("Two of you: first your answers to Blow the Man Down, then a part under them, sung over your own first take.", [
            ("First the answers", "Then the part under them"),
            ("Hear yourself", f"Your first take sings with you; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("Your answers first.", B_ANSWERS, BLOW_SLOW, B_CALLS, PITCH, chords=BLOW.chords_at(*B_SONG)),
        with_crew("Now the part under them, over your answers.", B_ALTO, BLOW_SLOW, B_CALLS, PITCH,
                  chords=BLOW.chords_at(*B_SONG), under={"steps": [1]}),
    ], headphones=True),
    lesson("4-challenge", 4, "Your crew", [
        learn("Your own crew, kept as a song: your chorus, then the part under it, sung over your own chorus. First, your answer from lesson 1, beside today's.", [
            ("Two of you", "The answer, then the part under it"),
            ("Kept as a song", f"Play it back any time; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        with_crew("The verse from the shantyman, then your chorus.",
                  D_CHORUS_SUNG, SAILOR.tempo, D_CALLS, PITCH, chords=SAILOR.chords_at(*D_SONG), thenAndNow=KEEP),
        with_crew("The part, over your chorus.", D_PART, SAILOR.tempo, D_CALLS, PITCH,
                  chords=SAILOR.chords_at(*D_SONG), under={"steps": [1]}),
    ], challenge=True, headphones=True,
       keepSong={"title": EN("Drunken Sailor, my crew"), "takes": [{"step": 1, "name": EN("Answer")}, {"step": 2, "name": EN("Part")}], "from": 2, "partners": [EN("Shantyman")]}),
]

course = {
    "id": "sea-shanties", "version": 1, "reviewed": False, "title": EN("Sea shanties and work songs"),
    "units": [
        {"id": "sh-the-crew-answers", "title": EN("The crew answers"), "colour": COLOUR, "lessons": UNIT1_LESSONS},
        {"id": "sh-on-the-pull", "title": EN("On the pull"), "colour": COLOUR, "lessons": UNIT2_LESSONS},
        {"id": "sh-the-shantyman", "title": EN("The shantyman"), "colour": COLOUR, "lessons": UNIT3_LESSONS},
        {"id": "sh-a-crew-of-you", "title": EN("A crew of you"), "colour": COLOUR, "lessons": UNIT4_LESSONS},
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
