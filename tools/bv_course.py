"""Backing vocals (docs/courses/backing-vocals.md in the courses repo): writes course/plus/backing-vocals/course.json.
Built from the courses lead's build spec, on the reviewers' rewritten lessons (a voice teacher who sings and
arranges backing vocals, then a game designer), whose lines are taken here exactly: pads under a lead, doo-wop
figures stacked into three parts of you (kept as a song), answers in the lead's gaps (the old call and
response), then a real song and Amazing Grace in three parts, kept, with Then and now on lesson 1's pad.

Every line is `beat:length step [word]` in the template's own beats (re-timed so a passage starts at 0), steps
from the singer's comfortable note (do = 0). The lead is a `with` partner line copied from the template's
tune, an octave up (do + 12) except in Shenandoah, so every backing note sits under it. The checks below fail
the build on a note outside -5 to +9, a backing note that isn't a tone of the chord sounding (a chord shorter
than a beat is held through, as backing singers do) or that is above the lead or on its note, a unison with
your own earlier take, a figure that doesn't fill whole bars, a `release` note with no rest after it, an
`entry` step with fewer than three answers, and the house words.

    python3 -I tools/bv_course.py && python3 -I tools/coursefmt.py course/plus/backing-vocals/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/backing-vocals/course.json"

BANNED = re.compile(r"\bstars?\b|—", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)
LOW, HIGH = -5, 9  # the span: steps from the singer's comfortable note
COLOUR = 3
KEYS = {"C": 0, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
TONES = {"maj": [0, 4, 7], "min": [0, 3, 7], "dom7": [0, 4, 7, 10], "maj7": [0, 4, 7, 11], "min7": [0, 3, 7, 10], "maj6": [0, 4, 7, 9]}
EPS = 1e-9

SAFE = "stop if anything tightens or hurts"
SAFETY = f"Easy volume, softer than the lead; {SAFE}"
HEADPHONES = ("Headphones on", "Through a speaker, the lead and your earlier takes rest while you sing")
QUIET, NEARER, FULL = 0.6, 0.8, 1  # the lead's volume: brought in quietly (a partner line's default is 0.5)
PITCH = "Scored on your notes on pitch."
CHOSE = "Scored on the rounds you got right first time."
KEEP = "backing.first-pad"


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def num(x):
    """Beats to six decimals (the templates' rule), whole numbers as ints."""
    x = round(x, 6)
    return int(x) if x == int(x) else x


def L(text, lyric="oo", shift=0):
    """A line as the review writes it, `beat:length step [word], ...`, in template beats, moved back by `shift`.
    A note with no word is "oo" (`lyric`); lyric=None leaves a word-less note bare (a held syllable)."""
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


def words(notes, text):
    """The words of a run of notes, one syllable a note: "Com- ing for to car- ry me home"."""
    syllables = text.split()
    assert len(syllables) == len(notes), (text, notes)
    return [dict(n, lyric=s) for n, s in zip(notes, syllables)]


def end_of(notes):
    return max(n["beat"] + n["length"] for n in notes)


# ---- The songs: the template's tune (the lead) and chords, in steps from its do ----

class Song:
    def __init__(self, folder, name):
        data = json.loads((REPO / "templates" / folder / f"{name}.json").read_text())
        key = KEYS[data["key"]]
        do = 60 + key  # the template melody's own octave: its do is the singer's do
        self.name, self.tempo = name, data["tempo"]
        self.tune = [(n["beat"], n["length"], n["pitch"] - do, n.get("lyric")) for n in data["parts"][0]["guide"]["notes"]]
        self.chords = [(c["beat"], (c["root"] - key) % 12, c["quality"], None if c.get("bass") is None else (c["bass"] - key) % 12)
                       for c in data["chords"]]
        self.bounds = {b for s in data["sections"] for p in s["phrases"] for b in p}

    def passage(self, frm, to):
        assert frm in self.bounds and to in self.bounds, f"{self.name}: {frm} to {to} is not whole phrases"
        return frm, to

    def lead(self, frm, to, up=12, calls=None, volume=FULL):
        """The tune from `frm` to `to`, re-timed to start at 0, `up` steps higher; `calls`: only the notes in
        those template ranges (the call and response, the backing singing the response)."""
        keep = [n for n in self.tune if frm <= n[0] < to and (calls is None or any(a <= n[0] < b for a, b in calls))]
        notes = [{"beat": num(b - frm), "length": num(length), "step": p + up, **({"lyric": w} if w and w != "~" else {})}
                 for b, length, p, w in keep]
        return {"notes": notes, "volume": volume}

    def chords_at(self, frm, to):
        """The chords from `frm` to `to`, the one sounding at `frm` included, re-timed to start at 0."""
        sounding = [c for c in self.chords if c[0] <= frm + EPS][-1]
        inside = [c for c in self.chords if frm + EPS < c[0] < to - EPS]
        return [{"beat": num(b - frm), "root": r, "quality": q, "bass": bass} for b, r, q, bass in [(frm,) + sounding[1:]] + inside]


GRACE = Song("free", "amazing-grace")
SWING = Song("library", "swing-low")
MICHAEL = Song("free", "michael-row")
RED = Song("library", "red-river-valley")
SHEN = Song("library", "shenandoah")

# ---- The doo-wop loop (unit 2): no song, one chord a bar at 80, do, la, fa, so, then a closing do ----

LOOP_T = 80
BAR = 4
LOOP_ROOTS = [(0, "maj"), (9, "min"), (5, "maj"), (7, "maj")]


def loop_chords(rounds, close=False):
    out = [{"beat": num(16 * r + BAR * i), "root": root, "quality": q, "bass": None}
           for r in range(rounds) for i, (root, q) in enumerate(LOOP_ROOTS)]
    if close:
        out.append({"beat": 16 * rounds, "root": 0, "quality": "maj", "bass": None})
    return out


def bars(pattern, rounds, lyric="oo"):
    """A figure in whole bars: `pattern` is [(beat in the bar, length, [the step on each of the four chords], word?)],
    sung `rounds` times round the four-bar loop."""
    for b, length, steps, *_ in pattern:
        assert b >= 0 and b + length <= BAR + EPS and len(steps) == 4, f"a figure's note {b}:{length} leaves its bar"
    out = []
    for r in range(rounds):
        for i in range(4):
            for b, length, steps, *word in pattern:
                out.append({"beat": num(16 * r + BAR * i + b), "length": num(length), "step": steps[i], "lyric": (word or [lyric])[0]})
    return out


def closing(step, lyric="oo", rounds=2):
    """The closing do chord after the loop, a whole bar."""
    return [{"beat": 16 * rounds, "length": BAR, "step": step, "lyric": lyric}]


# The course's own doo-wop lead, on "la", at +12 to +21, above all three parts; its only non-chord notes pass.
DOOWOP_LEAD = L("0:2 16, 2:1 14, 3:1 12, 4:3 12, 7:1 16, 8:2 17, 10:1 16, 11:1 12, 12:4 14, 16:2 16, 18:2 19, 20:3 16, "
                "23:1 12, 24:2 17, 26:2 21, 28:2 19, 30:1 17, 31:1 14, 32:4 12", "la")

# ---- Steps ----


def card(title, detail):
    assert len(title) <= 40 and len(title.split()) <= 9, f"a card title is short: {title}"
    assert len(detail) <= 72 and "\n" not in detail and ". " not in detail, f"a card's detail is one line: {detail}"
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual, listen=None):
    assert len(cards) <= 3, headline
    assert HEADPHONES in cards, f"every learn step says headphones on: {headline}"
    assert any(SAFE in d for _, d in cards), f"every learn step carries the safety line: {headline}"
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}
    if listen:
        step["listen"] = listen
    return step


def listen(tempo, notes):
    return {"tempo": tempo, "turn": False, "notes": notes}


def play(text, notes, tempo, measures=PITCH, *, chords=None, lead=None, **extra):
    ex = {"tempo": tempo, "turn": False, "notes": notes}
    if chords:
        ex["chords"] = chords
    if lead:
        ex["with"] = [lead]
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def wait_for_me(text, notes, tempo):
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes}}


def clip(*lines, chords=None):
    notes = sorted((n for line in lines for n in line), key=lambda n: (n["beat"], n["step"]))
    c = {"notes": notes}
    if chords:
        c["chords"] = chords
    return c


def choose(text, tempo, rounds):
    """rounds: (prompt, [clip, clip], answer, why); each clip's sung option is checked for the span."""
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": [
        {"prompt": EN(p), "clips": clips, "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


def selfcheck(text, tempo, model, questions):
    return {"kind": "selfcheck", "text": EN(text),
            "exercise": {"tempo": tempo, "model": model, "along": True, "questions": [EN(q) for q in questions]}}


def under(*steps):
    return {"steps": list(steps)}


# ---- The checks ----

PASSED_OVER = []  # (lesson, beat): a held note through a chord shorter than a beat (Shenandoah's pedal only)


def in_span(where, notes):
    for n in notes:
        assert LOW <= n["step"] <= HIGH, f"{where}: step {n['step']} at beat {n['beat']} is outside {LOW} to {HIGH}"


def chord_spans(chords, end):
    beats = [c["beat"] for c in chords] + [end]
    return [(beats[i], beats[i + 1], c) for i, c in enumerate(chords)]


def sounding(notes, beat):
    return [n["step"] for n in notes if n["beat"] - EPS <= beat < n["beat"] + n["length"] - EPS]


def check_line(where, ex):
    """A backing line, at every quarter beat: a tone of the chord sounding (a chord shorter than a beat is held
    through), and under the lead, never on its note."""
    notes, lead = ex["notes"], [n for w in ex.get("with", []) for n in w["notes"]]
    end = max(end_of(notes), end_of(lead) if lead else 0)
    spans = chord_spans(ex["chords"], end) if ex.get("chords") else []
    for n in notes:
        b = n["beat"]
        while b < n["beat"] + n["length"] - EPS:
            for a, z, c in spans:
                if a - EPS <= b < z - EPS:
                    if n["step"] % 12 not in {(c["root"] + t) % 12 for t in TONES[c["quality"]]}:
                        assert z - a < 1, f"{where}: step {n['step']} at beat {b} isn't in the chord on {c['root']}"
                        PASSED_OVER.append((where.split()[0], n["beat"]))
            for p in sounding(lead, b):
                assert n["step"] < p, f"{where}: step {n['step']} at beat {b} is on or above the lead's {p}"
            b += 0.25


def check_layers(where, steps, i):
    """No note of a part on the note of a part under it (your own earlier take)."""
    ex = steps[i]["exercise"]
    for k in ex["under"]["steps"]:
        assert k < i, f"{where}: a layer is an earlier step"
        layer = steps[k]["exercise"]["notes"]
        for n in ex["notes"]:
            for m in layer:
                overlap = min(n["beat"] + n["length"], m["beat"] + m["length"]) - max(n["beat"], m["beat"])
                assert not (overlap > EPS and n["step"] == m["step"]), f"{where}: a unison with step {k + 1} at beat {n['beat']}"


def judged_entries(notes):
    """`entry` judges every note after a rest of a quarter beat or more, never the first."""
    ordered = sorted(notes, key=lambda n: n["beat"])
    return [b["beat"] for a, b in zip(ordered, ordered[1:]) if b["beat"] - (a["beat"] + a["length"]) >= 0.25 - EPS]


def check(lid, steps):
    for i, step in enumerate(steps):
        where = f"bv-{lid} step {i + 1}"
        ex = step.get("exercise", {})
        if step["kind"] in ("play", "try"):
            in_span(where, ex["notes"])
        if step["kind"] == "play":
            if "rhythm" in ex:
                assert ex["rhythm"] in (True, "swing") and "score" not in ex, f"{where}: rhythm is true or \"swing\", on a default-scored step"
            check_line(where, ex)
            if "under" in ex:
                check_layers(where, steps, i)
            if ex.get("score") == "release":
                ordered = sorted(ex["notes"], key=lambda n: n["beat"])
                for a, b in zip(ordered, ordered[1:]):
                    assert b["beat"] - (a["beat"] + a["length"]) >= 2 - EPS, f"{where}: a released note needs a rest after it"
            if ex.get("score") == "entry":
                assert len(judged_entries(ex["notes"])) >= 3, f"{where}: an entry step needs three or more answers"
        if step["kind"] == "selfcheck" and step.get("_sung"):
            in_span(where, ex["model"]["notes"])
        if step["kind"] == "choose":
            for r in step["_options"]:
                in_span(where, r)


# Each lesson page's "Did you know?" (2026-11-08): read in its source, then checked again.
FACTS = {
    "1-pad": {"id": "bagpipe-amazing-grace", "text": EN("A bagpipe Amazing Grace, by the pipes, drums and military band of the Royal Scots Dragoon Guards, was Britain's best-selling single of 1972. Under the tune, the pipes' drones hold one constant note, usually the home note."), "source": EN("Wikipedia, 1972 in British music; Bagpipes"), "url": "https://en.wikipedia.org/wiki/1972_in_British_music"},
    "1-moving": {"id": "rule-of-the-shortest-way", "text": EN("Keep the shared note, else take the nearest: in his 1841 harmony textbook the organist Johann August Dürrnberger called this the \"rule of the shortest way\". Anton Bruckner was one of his students."), "source": EN("Wikipedia, Voice leading"), "url": "https://en.wikipedia.org/wiki/Voice_leading"},
    "1-together": {"id": "choir-hearts-in-step", "text": EN("In a 2013 study of fifteen 18-year-old choir singers, their heart rates rose and fell together when they sang a slow chant, breathing only between phrases. Humming one note, breathing at will, gave no shared pattern."), "source": EN("Vickhoff et al., Frontiers in Psychology (2013)"), "url": "https://www.frontiersin.org/articles/10.3389/fpsyg.2013.00334/full"},
    "2-doo-wah": {"id": "doo-wop-progression-buxtehude", "text": EN("Your four chords are known as the doo-wop progression, or the \"Heart and Soul\" chords. They're far older: Dieterich Buxtehude, who died in 1707, repeated them in the bass line of a psalm setting."), "source": EN("Wikipedia, '50s progression"), "url": "https://en.wikipedia.org/wiki/50s_progression"},
    "2-shoo-bop": {"id": "syllables-for-drums", "text": EN("Doo-wop street singers generally sang with no instruments. They kept time with a swing-like off-beat, and syllables like \"doo-wop\" stood in for the drums."), "source": EN("Wikipedia, Doo-wop"), "url": "https://en.wikipedia.org/wiki/Doo-wop"},
    "2-three": {"id": "doo-wop-name-1961", "text": EN("The earliest known print use of \"doo-wop\" for this music came in 1961, as the style faded: a Chicago Defender column called the Marcels' \"Blue Moon\" a doo-wop \"like those of many years ago\"."), "source": EN("Wikipedia, Doo-wop"), "url": "https://en.wikipedia.org/wiki/Doo-wop"},
    "3-fill": {"id": "whatd-i-say-filled-time", "text": EN("One night on tour, Ray Charles and his band ran out of songs with time still to fill. He improvised \"What'd I Say\", and had his backing singers answer him."), "source": EN("Wikipedia, What'd I Say"), "url": "https://en.wikipedia.org/wiki/What%27d_I_Say"},
    "3-response": {"id": "basing-the-leader", "text": EN("Slave Songs of the United States (1867), the book that printed Michael, Row, describes a leader starting each verse, often improvising, while the others, \"who 'base' him, as it is called\", strike in with the refrain."), "source": EN("Allen, Ware and Garrison, Slave Songs of the United States (1867), introduction, Internet Archive"), "url": "https://archive.org/details/slavesongsofunit00alle", "distinct": ["michael-row-1863"]},
    "3-on-time": {"id": "gandy-dancers-third-beat", "text": EN("Gandy dancers, railroad gangs who straightened track, tapped their bars on the rails to a caller's song. Once they tapped in perfect time, he called for a pull on the third beat of a four-beat refrain."), "source": EN("Encyclopedia of Alabama, Gandy Dancer Work Song Tradition"), "url": "https://encyclopediaofalabama.org/article/gandy-dancer-work-song-tradition/"},
    "4-red-river": {"id": "artificial-double-tracking", "text": EN("Pop singers often double a vocal by singing it twice. In 1966 an Abbey Road engineer invented a way to fake it, artificial double tracking, mainly at John Lennon's request: he despised the chore."), "source": EN("Wikipedia, Automatic double tracking"), "url": "https://en.wikipedia.org/wiki/Automatic_double_tracking"},
    "4-two-more": {"id": "andrews-sisters-three-parts", "text": EN("The Andrews Sisters sang close harmony in three parts: LaVerne a contralto, Maxene a soprano, and Patty, a mezzo-soprano, the lead. They started out imitating an earlier sister trio, the Boswell Sisters."), "source": EN("Wikipedia, The Andrews Sisters"), "url": "https://en.wikipedia.org/wiki/The_Andrews_Sisters"},
}


def lesson(lid, title, steps, **extra):
    check(lid, steps)
    if "fact" not in extra and lid in FACTS:
        extra = {"fact": FACTS[lid], **extra}
    return {"id": f"bv-{lid}", "title": EN(title), **extra, "steps": steps}


def strip(value):
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


def options(step, *lines):
    """Mark a choose step's sung options (not the lead's notes) for the span check."""
    step["_options"] = list(lines)
    return step


# ---- Unit 1: Oohs and aahs ----

G_VERSE = GRACE.passage(0, 48)
G_TWO = GRACE.passage(0, 24)
FIRST_PAD = L("1:10 0, 13:6 0, 19:4 -1, 25:10 0, 37:3 0, 40:3 -1, 43:5 0")

S_CHORUS = SWING.passage(0, 31)
S_TWO = SWING.passage(0, 16)
MOVING = L("0:4 4, 4:2 5, 6:1 4, 8:4 4, 12:3 2, 16:1 5, 17:3 4, 20:2 5, 22:1 4, 24:3 4, 27:1 5, 28:2 4")
assert MOVING[:5] == L("0:4 4, 4:2 5, 6:1 4, 8:4 4, 12:3 2")

TOGETHER = L("1:10 0, 13:10 7, 25:10 0, 37:11 7")
SH_VERSE = SHEN.passage(0, 41)
SH_TWO = SHEN.passage(0, 16)
SH_PAD = L("1:6.25 -5, 9:3 -3, 12:3.25 -5, 17:2.5 -3, 19.5:3.75 -5, 24:4 -5, 28:1 -3, 29:2.25 -5, 33:3 -3, 36:5 -5")

AG_MID = L("1:6 4, 7:3 5, 10:1 4, 13:6 4, 19:4 2, 25:6 4, 31:3 5, 34:1 4, 37:3 4, 40:3 2, 43:5 4")
AG_TOP = L("1:6 7, 7:2 9, 13:10 7, 25:6 7, 31:2 9, 37:11 7")


def first_two(line, to):
    return [n for n in line if n["beat"] < to]


UNIT1 = {"id": "bv-oohs-and-aahs", "title": EN("Oohs and aahs"), "colour": COLOUR, "lessons": [
    lesson("1-pad", "A pad", [
        learn("A pad is one held \"oo\" under the tune. Yours: do, and ti when the chord moves to so.", [
            ("Softer than the tune", f"Easy volume; {SAFE}"),
            ("Hold still while the tune moves", "Your note stays put; the tune passes over it"),
            HEADPHONES,
        ], "harmony"),
        wait_for_me("Find each pad note: do, ti, do. Each waits until you're on it.", L("0:2 0, 2:2 -1, 4:2 0"), GRACE.tempo),
        play("The first two lines over the chords alone: a soft \"oo\" on do, then ti as the chord moves. Breathe where the tune would; a quick breath mid-note is fine.",
             first_two(FIRST_PAD, 24), GRACE.tempo, "Scored on your pad's notes on pitch. The ring shows how well each one locks to the chord.",
             chords=GRACE.chords_at(*G_TWO), tuning=True),
        play("Now the whole verse, the tune coming in quietly over you. Rest where the tune breathes. Your first pad is kept for the course's last lesson.",
             FIRST_PAD, GRACE.tempo, "Scored on your pad's notes on pitch, under the tune.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE, volume=QUIET), keep=KEEP),
    ]),
    lesson("1-moving", "Moving with the chords", [
        learn("Keep the note the new chord shares; else step to the nearest. Mi, fa, mi, re.", [
            ("Move only when you must", "A common tone holds; else the nearest step"),
            ("Why \"oo\"", f"An \"oo\" blends where an \"ah\" carries; {SAFE}"),
            HEADPHONES,
        ], "blend"),
        options(choose("Hear the chord move under each pad, then choose.", SWING.tempo, [
            ("The chord moves from do's to fa's. Which pad moves the least?",
             [clip(L("0:2 4, 2:2 5"), chords=[{"beat": 0, "root": 0, "quality": "maj", "bass": None}, {"beat": 2, "root": 5, "quality": "maj", "bass": None}]),
              clip(L("0:2 4, 2:2 9"), chords=[{"beat": 0, "root": 0, "quality": "maj", "bass": None}, {"beat": 2, "root": 5, "quality": "maj", "bass": None}])],
             0, "Fa is a half step from mi, so the pad hardly moves. La is a leap."),
            ("The chord moves from do's to so's. Which pad moves the least?",
             [clip(L("0:2 4, 2:2 2"), chords=[{"beat": 0, "root": 0, "quality": "maj", "bass": None}, {"beat": 2, "root": 7, "quality": "maj", "bass": None}]),
              clip(L("0:2 4, 2:2 -1"), chords=[{"beat": 0, "root": 0, "quality": "maj", "bass": None}, {"beat": 2, "root": 7, "quality": "maj", "bass": None}])],
             0, "Re is a whole step from mi, and so's chord holds it. Low ti is a leap down."),
        ]), L("0:2 4, 2:2 5"), L("0:2 4, 2:2 9"), L("0:2 4, 2:2 2"), L("0:2 4, 2:2 -1")),
        play("The first two lines over the chords: mi, fa, mi, then re, each held on \"oo\".",
             first_two(MOVING, 16), SWING.tempo, "Scored on your pad's notes on pitch. The ring shows how well each one locks to the chord.",
             chords=SWING.chords_at(*S_TWO), tuning=True),
        play("The whole chorus under the tune. Only the chord changes light: between them, hold by ear.",
             MOVING, SWING.tempo, "Scored on your pad's notes on pitch, most of them sung with no light to follow.",
             chords=SWING.chords_at(*S_CHORUS), lead=SWING.lead(*S_CHORUS, volume=NEARER), lights="changes"),
        {**selfcheck("Your pad once more, the guide singing it with you, then hear yours beside it.", SWING.tempo,
                     {"notes": MOVING, "chords": SWING.chords_at(*S_CHORUS)}, [
                         "Singing with the guide, did your \"oo\" disappear into its \"oo\"?",
                         "Was it the same shape from start to end: no \"w\" in, no \"ah\" out?",
                         "Did you stay at speaking volume or softer?",
                     ]), "_sung": True},
    ]),
    lesson("1-together", "Together off", [
        learn("Backing singers stop with the tune. Each note is the one the phrase's chords share: do, then so.", [
            ("Off with the tune", "When the tune's phrase ends, yours does"),
            ("Breathe with the tune", f"Then back in together; {SAFE}"),
            HEADPHONES,
        ], "steady"),
        options(choose("Hear each pad under the tune, then choose.", GRACE.tempo, [
            ("Which pad stops with the tune?", [clip(L("0:2 12, 2:1 9, 3:1 7", None), L("0:4 0")), clip(L("0:2 12, 2:1 9, 3:1 7", None), L("0:4.75 0"))],
             0, "The first ends as the tune does. The second hangs on after it."),
            ("Which pad stops with the tune?", [clip(L("0:2 12, 2:1 9, 3:1 7", None), L("0:3.25 0")), clip(L("0:2 12, 2:1 9, 3:1 7", None), L("0:4 0"))],
             1, "The first stops before the tune does. The second ends with it."),
        ]), L("0:4 0"), L("0:4.75 0"), L("0:3.25 0")),
        play("The first two lines under the tune: do, held, then so. Stop each with the tune.",
             first_two(TOGETHER, 24), GRACE.tempo, "Scored on your notes on pitch.",
             chords=GRACE.chords_at(*G_TWO), lead=GRACE.lead(*G_TWO)),
        play("The whole verse: do, so, do, so, each stopped as the tune's phrase ends, with a breath after it.",
             TOGETHER, GRACE.tempo, "Scored on stopping with the tune, not on the notes.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE), score="release"),
    ]),
    lesson("1-shenandoah", "Shenandoah's pad", [
        learn("Shenandoah, slow and wide: a low \"oo\" that rocks between so and la. Hear the tune first.", [
            ("Low and light", f"Your low so, never pressed; {SAFE}"),
            ("In with the chord", "Some lines, the pad waits for the chord to start"),
            HEADPHONES,
        ], "harmony", listen=listen(SHEN.tempo, SHEN.lead(*SH_TWO, up=0)["notes"])),
        wait_for_me("Find the pad's notes: low so, low la, low so.", L("0:2 -5, 2:2 -3, 4:2 -5"), SHEN.tempo),
        play("The first two lines under the tune: low so, then la, then so.",
             first_two(SH_PAD, 16), SHEN.tempo, "Scored on your pad's notes on pitch, under the tune.",
             chords=SHEN.chords_at(*SH_TWO), lead=SHEN.lead(*SH_TWO, up=0)),
        play("The whole verse. Only the chord changes light: between them, rock between so and la by ear.",
             SH_PAD, SHEN.tempo, "Scored on your pad's notes on pitch, most of them sung with no light to follow.",
             chords=SHEN.chords_at(*SH_VERSE), lead=SHEN.lead(*SH_VERSE, up=0), lights="changes"),
    ], challenge=True),
]}

# ---- Unit 2: Doo-wop ----

DOO_ONCE = bars([(0, 1, [4, 4, 5, 2], "doo"), (1, 2, [4, 4, 5, 2], "wah")], 1)
assert [(n["beat"], n["length"], n["step"]) for n in DOO_ONCE] == [(n["beat"], n["length"], n["step"]) for n in L("0:1 4, 1:2 4, 4:1 4, 5:2 4, 8:1 5, 9:2 5, 12:1 2, 13:2 2")]
DOO_WAH = bars([(0, 1, [4, 4, 5, 2], "doo"), (1, 2, [7, 9, 9, 7], "wah")], 2)
assert [(n["beat"], n["length"], n["step"]) for n in DOO_WAH[:8]] == [(n["beat"], n["length"], n["step"]) for n in L("0:1 4, 1:2 7, 4:1 4, 5:2 9, 8:1 5, 9:2 9, 12:1 2, 13:2 7")]
assert DOO_WAH[8:] == [dict(n, beat=n["beat"] + 16) for n in DOO_WAH[:8]]
BOPS_ONCE = bars([(1, 0.5, [0, 0, 0, -1]), (3, 0.5, [0, 0, 0, -1])], 1, "bop")
assert [(n["beat"], n["length"], n["step"]) for n in BOPS_ONCE] == [(n["beat"], n["length"], n["step"]) for n in L("1:0.5 0, 3:0.5 0, 5:0.5 0, 7:0.5 0, 9:0.5 0, 11:0.5 0, 13:0.5 -1, 15:0.5 -1")]
BOPS = bars([(1, 0.5, [0, 0, 0, -1]), (3, 0.5, [0, 0, 0, -1])], 2, "bop")
assert len(BOPS) == 16 and len(judged_entries(BOPS)) == 15
LOW_PART = bars([(0, 3.5, [0, 0, 0, -1])], 2) + closing(0)
MID_PART = bars([(0, 3.5, [4, 4, 5, 2])], 2) + closing(4)
TOP_PART = bars([(0, 3.5, [7, 9, 9, 7])], 2) + closing(7)
MID_DOO_WAH = bars([(0, 1, [4, 4, 5, 2], "doo"), (1, 2, [4, 4, 5, 2], "wah")], 2) + closing(4, "wah")
TOP_BOPS = bars([(1, 0.5, [7, 9, 9, 7]), (3, 0.5, [7, 9, 9, 7])], 2, "bop") + closing(7, "wah")

# The doo-wop lead: above every part, its non-chord notes only the three that pass (re at 2, mi at 10, fa at 30).
_spans = chord_spans(loop_chords(2, close=True), 36)
_outside = [n["beat"] for n in DOOWOP_LEAD for a, z, c in _spans
            if a <= n["beat"] < z and n["step"] % 12 not in {(c["root"] + t) % 12 for t in TONES[c["quality"]]}]
assert _outside == [2, 10, 30], _outside
assert 12 <= min(n["step"] for n in DOOWOP_LEAD) and max(n["step"] for n in DOOWOP_LEAD) <= 21
DOOWOP = {"notes": DOOWOP_LEAD, "volume": FULL}


def clip_bar(*beats):
    """Two bops on do, one a beat-and-a-half gap apart, at these beats."""
    return L(", ".join(f"{b}:0.5 0 bop" for b in beats))


I_CHORD = [{"beat": 0, "root": 0, "quality": "maj", "bass": None}]

UNIT2 = {"id": "bv-doo-wop", "title": EN("Doo-wop"), "colour": COLOUR, "lessons": [
    lesson("2-doo-wah", "Doo-wah", [
        learn("\"Doo\" on the beat, \"wah\" opens up: the change is the vowel. Four chords, one a bar, round and round.", [
            ("Light, never punched", f"Easy volume; {SAFE}"),
            ("The same notes as your mi, fa, re pad", "Mi, mi, fa, re: one a chord"),
            HEADPHONES,
        ], "vowels"),
        wait_for_me("Find the notes you'll use: mi, so, la, fa, re.", L("0:1 4, 1:1 7, 2:1 9, 3:1 5, 4:1 2"), LOOP_T),
        play("Once round the four chords: \"doo\", then \"wah\" on the same note, on mi, mi, fa, re.",
             DOO_ONCE, LOOP_T, PITCH, chords=loop_chords(1)),
        play("Twice round, the two-note doo-wah: \"doo\" on mi, mi, fa, re, and \"wah\" up to so, la, la, so. Halfway, the lights fade.",
             DOO_WAH, LOOP_T, "Scored on your notes on pitch, the second half with the lights faded.",
             chords=loop_chords(2), lights="fade"),
    ]),
    lesson("2-shoo-bop", "Shoo-bop", [
        learn("Shoo-bop: the \"sh\" is breath, and the note is on \"bop\". Short and light, on the beat. Here, just \"bop\".", [
            ("On beats two and four", "Two bops a bar, in the gaps"),
            ("Short and light", f"A low bop is never pushed; {SAFE}"),
            HEADPHONES,
        ], "bass"),
        options(choose("Hear each pair of bops over the chord, then choose.", LOOP_T, [
            ("Which bops are on the beat?", [clip(clip_bar(1, 3), chords=I_CHORD), clip(clip_bar(1.25, 3.25), chords=I_CHORD)],
             0, "The second pair comes in late, just after the beat."),
            ("Which bops are on the beat?", [clip(clip_bar(0.8, 2.8), chords=I_CHORD), clip(clip_bar(1, 3), chords=I_CHORD)],
             1, "The first pair rushes, just ahead of the beat."),
        ]), clip_bar(1, 3), clip_bar(1.25, 3.25), clip_bar(0.8, 2.8)),
        play("Once round: two bops a bar on do, then on low ti for the last chord.",
             BOPS_ONCE, LOOP_T, PITCH, chords=loop_chords(1)),
        play("Twice round, each bop on the beat.",
             BOPS, LOOP_T, "Scored on coming in on the beat, and the note you land on.", chords=loop_chords(2), score="entry"),
    ]),
    lesson("2-three", "Three parts", [
        learn("Three of you, one chord: low, middle, top, each a step from its last note.", [
            ("One part at a time", "Each sung over the ones before"),
            ("Never louder to hear yourself", f"Lower your headphones instead; {SAFE}"),
            HEADPHONES,
        ], "harmony"),
        play("The low part, twice round and a closing chord: do, do, do, low ti, each held on \"oo\".",
             LOW_PART, LOOP_T, "Scored on your notes on pitch. The ring shows how well each one locks to the chord.",
             chords=loop_chords(2, close=True), tuning=True),
        play("The middle over your low part: mi, mi, fa, re.",
             MID_PART, LOOP_T, "Scored on your notes on pitch, over your low part.",
             chords=loop_chords(2, close=True), under=under(1)),
        play("The top over both: so, la, la, so. Three of you.",
             TOP_PART, LOOP_T, "Scored on your notes on pitch, over your two parts.",
             chords=loop_chords(2, close=True), under=under(1, 2)),
    ]),
    lesson("2-doo-wop", "Your doo-wop", [
        learn("Your three parts, now with rhythm, under a lead. Kept as a song.", [
            ("Low, then doo-wah, then bops", "Each over the ones before"),
            ("Under the lead", f"Every part sits below it; {SAFE}"),
            HEADPHONES,
        ], "harmony"),
        play("The low part on \"oo\", under the lead: do, do, do, low ti, and the closing chord.",
             LOW_PART, LOOP_T, "Scored on your notes on pitch, under the lead.",
             chords=loop_chords(2, close=True), lead=DOOWOP),
        play("The middle doo-wah over it: \"doo\", \"wah\" on mi, mi, fa, re, then a held \"wah\".",
             MID_DOO_WAH, LOOP_T, "Scored on your notes on pitch, over your low part.",
             chords=loop_chords(2, close=True), lead=DOOWOP, under=under(1)),
        play("The top bops over both: two a bar on so, la, la, so. Halfway, the lights fade.",
             TOP_BOPS, LOOP_T, "Scored on your notes on pitch, over your two parts, the second half with the lights faded.",
             chords=loop_chords(2, close=True), lead=DOOWOP, under=under(1, 2), lights="fade"),
    ], challenge=True, keepSong={"title": EN("My doo-wop"), "takes": [
        {"step": 1, "name": EN("Low")}, {"step": 2, "name": EN("Doo-wah")}, {"step": 3, "name": EN("Bops")}],
        "from": 3, "partners": [EN("Lead")]}),
]}

# ---- Unit 3: Answers (Swing Low and Michael Row, the call and response they were) ----
# An answer is in time or it isn't one: the answers with no `score` of their own take `rhythm` (pitch 70,
# timing 30; docs/play-timing-plan.md in the app's repo) and say so.

COMING = "Com- ing for to car- ry me home"
SWING_CALLS = [(0, 8), (16, 24)]
FILLS = L("7:1 4, 13:1 2, 14:2 -1, 23:1 4, 29:1 4, 30:1 0")

M_VERSE = MICHAEL.passage(0, 32)
RESPONSE = L("8:1 4 Hal-, 9:1 7 le-, 10:4 9 lu-, 14:1 7 jah!, 24:1 0 Hal-, 25:1 2 le-, 26:2 4 lu-, 28:2 2, 30:2 0 jah!", None)
HALLELUJAH = L("8:1 4 Hal-, 9:1 4 le-, 10:4 5 lu-, 14:1 4 jah!, 24:1 -5 Hal-, 25:1 -3 le-, 26:2 0 lu-, 28:2 -1, 30:2 0 jah!", None)

ON_TIME_TWO = L("2:1 0 low") + words(L("8:0.5 0, 8.5:0.5 0, 9:0.5 0, 9.5:0.5 0, 10:0.5 4, 10.5:0.5 4, 11:1 7, 12:3 7"), COMING)
ON_TIME = ON_TIME_TWO + L("18:1 4 low") + words(L("24:0.5 0, 24.5:0.5 0, 25:0.5 0, 25.5:0.5 0, 26:0.5 4, 26.5:0.5 4, 27:1 2, 28:2 0"), COMING)
assert judged_entries(ON_TIME) == [8, 18, 24]

S_ALL = SWING.passage(31, 96)
S_VERSE = SWING.passage(31, 64)
VERSE_CALLS = [(31, 40), (47, 56), (64, 72), (80, 88)]
ANSWERS_VERSE = (words(L("40:0.5 0, 40.5:0.5 0, 41:0.5 0, 41.5:0.5 0, 42:0.5 4, 42.5:0.5 4, 43:1 7, 44:2 7", shift=31), COMING)
                 + words(L("56:0.5 0, 56.5:0.5 0, 57:0.5 0, 57.5:0.5 0, 58:0.5 4, 58.5:0.5 4, 59:1 2, 60:3 0", shift=31), COMING))
ANSWERS = (ANSWERS_VERSE + L("66:1 0 low", shift=31)
           + words(L("72:0.5 0, 72.5:0.5 0, 73:0.5 0, 73.5:0.5 0, 74:0.5 4, 74.5:0.5 4, 75:1 7, 76:3 7", shift=31), COMING)
           + L("82:1 4 low", shift=31)
           + words(L("88:0.5 0, 88.5:0.5 0, 89:0.5 0, 89.5:0.5 0, 90:0.5 4, 90.5:0.5 4, 91:1 2, 92:4 0", shift=31), COMING))

UNIT3 = {"id": "bv-answers", "title": EN("Answers"), "colour": COLOUR, "lessons": [
    lesson("3-fill", "Fill the gap", [
        learn("An answer waits for the tune's long note, then fills it.", [
            ("Wait for the long note", "Then a short \"oo\" under it"),
            ("Small and soft", f"An answer never covers the tune; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        options(choose("Hear the tune with each answer, then choose.", SWING.tempo, [
            ("Which answer waits for the long note?",
             [clip(SWING.lead(8, 16)["notes"], L("13:1 2, 14:2 -1", shift=8), chords=SWING.chords_at(8, 16)),
              clip(SWING.lead(8, 16)["notes"], L("10:2 2, 12:2 -1", shift=8), chords=SWING.chords_at(8, 16))],
             0, "The answer waits for the long note: the first fills the held \"home\", the second sings over \"carry me\"."),
        ]), L("13:1 2, 14:2 -1"), L("10:2 2, 12:2 -1")),
        play("The first two lines: an \"oo\" in the tune's rest, then two under its held \"home\".",
             first_two(FILLS, 16), SWING.tempo, "Scored on your answers on pitch and on the beat.",
             chords=SWING.chords_at(*S_TWO), lead=SWING.lead(*S_TWO), rhythm=True),
        play("The whole chorus: each answer in a rest or under a held note.",
             FILLS, SWING.tempo, "Scored on your answers on pitch and on the beat.",
             chords=SWING.chords_at(*S_CHORUS), lead=SWING.lead(*S_CHORUS), rhythm=True),
    ]),
    lesson("3-response", "The response", [
        learn("Call and response, the oldest backing job: the leader calls \"Michael, row the boat ashore\", and you answer \"Hallelujah\".", [
            ("The leader calls", "You answer, and rest through the next call"),
            ("An answer, not a shout", f"Easy volume; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        play("The lead sings only the calls. You sing the response: the tune's own \"Hallelujah\".",
             RESPONSE, MICHAEL.tempo, "Scored on your response on pitch and on the beat.",
             chords=MICHAEL.chords_at(*M_VERSE), lead=MICHAEL.lead(*M_VERSE, calls=[(0, 8), (16, 24)]), rhythm=True),
        play("Now the lead sings it all. You sing the \"Hallelujah\" in harmony under it, resting through the calls. Halfway, the lights fade.",
             HALLELUJAH, MICHAEL.tempo, "Scored on your harmony on pitch and on the beat, the second half with the lights faded.",
             chords=MICHAEL.chords_at(*M_VERSE), lead=MICHAEL.lead(*M_VERSE), lights="fade", rhythm=True),
    ]),
    lesson("3-on-time", "Back in on time", [
        learn("Echo the tune's \"low\", then answer the line. Count the gap; come in on the beat.", [
            ("Count the gap", "The tune rests; you come in on the beat"),
            ("Light and quick", f"The words short and easy; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        play("The first two lines: echo \"low\", then answer \"Coming for to carry me home\".",
             ON_TIME_TWO, SWING.tempo, "Scored on your answers on pitch and on the beat.",
             chords=SWING.chords_at(*S_TWO), lead=SWING.lead(*S_TWO, calls=SWING_CALLS), rhythm=True),
        play("The whole chorus: each echo and answer in on the beat.",
             ON_TIME, SWING.tempo, "Scored on coming back in on time after each rest, and the note you land on.",
             chords=SWING.chords_at(*S_CHORUS), lead=SWING.lead(*S_CHORUS, calls=SWING_CALLS), score="entry"),
    ]),
    lesson("3-verse", "Answers through a verse", [
        learn("The whole call and response. The tune calls four times: you answer, and echo its \"low\".", [
            ("Four calls, four answers", "Two in the verse, two in the chorus"),
            ("Count, then come in", f"Easy volume; {SAFE}"),
            HEADPHONES,
        ], "phrase"),
        play("The verse: answer both calls, \"Coming for to carry me home\".",
             [n for n in ANSWERS if n["beat"] < 33], SWING.tempo, "Scored on your answers on pitch and on the beat.",
             chords=SWING.chords_at(*S_VERSE), lead=SWING.lead(*S_VERSE, calls=VERSE_CALLS), rhythm=True),
        play("The verse and the chorus: answer every call, and echo the chorus's \"low\". Halfway, the lights fade.",
             ANSWERS, SWING.tempo, "Scored on your answers on pitch and on the beat, the second half with the lights faded.",
             chords=SWING.chords_at(*S_ALL), lead=SWING.lead(*S_ALL, calls=VERSE_CALLS), lights="fade", rhythm=True),
    ], challenge=True),
]}
assert [n for n in ANSWERS if n["beat"] < 33] == ANSWERS_VERSE

# ---- Unit 4: Behind a real song ----

R_VERSE = RED.passage(0, 33)
R_TWO = RED.passage(0, 16)
RED_PAD = L("1:4 4, 5:1 5, 6:1 4, 8:5 4, 13:2 5, 23:0.5 9 sun-, 23.5:0.5 5 shine, 30:1 5 a, 31:2 4 while")
assert judged_entries(RED_PAD) == [8, 23, 30]

UNIT4 = {"id": "bv-behind-a-song", "title": EN("Behind a real song"), "colour": COLOUR, "lessons": [
    lesson("4-red-river", "Red River Valley: a pad, then answers", [
        learn("A pad for two lines, then answers: wait, echo \"sunshine\", and fill \"a while\". Hear the tune first.", [
            ("Pad, then answers", f"Hold for two lines, then the gaps; {SAFE}"),
            ("Doubling the tune", "Pop backing often sings the tune too: the mic can't score it"),
            HEADPHONES,
        ], "harmony", listen=listen(RED.tempo, RED.lead(*R_VERSE)["notes"])),
        options(choose("Hear the tune with each echo, then choose.", RED.tempo, [
            ("Which echo sits in the tune's rest?",
             [clip(RED.lead(20, 24)["notes"], L("23:0.5 9, 23.5:0.5 5", shift=20), chords=RED.chords_at(20, 24)),
              clip(RED.lead(20, 24)["notes"], L("21:1 9, 22:1 5", shift=20), chords=RED.chords_at(20, 24))],
             0, "The first waits for the tune's rest. The second sings over \"sunshine\"."),
        ]), L("23:0.5 9, 23.5:0.5 5"), L("21:1 9, 22:1 5")),
        play("The first two lines: the pad on mi, a step up to fa and back, held under the tune.",
             first_two(RED_PAD, 16), RED.tempo, "Scored on your pad's notes on pitch.",
             chords=RED.chords_at(*R_TWO), lead=RED.lead(*R_TWO)),
        play("The whole verse: the pad, then echo \"sunshine\" in the rest, and fill \"a while\" under the tune's held note. Halfway, the lights fade.",
             RED_PAD, RED.tempo, "Scored on your notes on pitch, the second half with the lights faded.",
             chords=RED.chords_at(*R_VERSE), lead=RED.lead(*R_VERSE), lights="fade"),
    ]),
    lesson("4-two-more", "Amazing Grace: two more parts", [
        learn("Your pad from lesson 1 is the low part. Now a middle and a top: mi, fa, re and so, la.", [
            ("The top rests", "Where the tune dips low, the top waits"),
            ("Breathe at different times", f"In a group, so the pad never stops; {SAFE}"),
            HEADPHONES,
        ], "dynamics"),
        wait_for_me("Find the top part's notes: so, la, so.", L("0:2 7, 2:2 9, 4:2 7"), GRACE.tempo),
        play("The middle part under the tune: mi, fa and re, each held on \"oo\".",
             AG_MID, GRACE.tempo, "Scored on your middle part's notes on pitch.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE)),
        play("The top part over your middle, under the tune: so and la, resting where the tune dips low. Only the chord changes light.",
             AG_TOP, GRACE.tempo, "Scored on your top part's notes on pitch, most of them sung with no light to follow.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE), under=under(2), lights="changes"),
        selfcheck("Your middle part once more, the tune singing with you, then hear yours beside it.", GRACE.tempo,
                  {"notes": GRACE.lead(*G_VERSE)["notes"], "chords": GRACE.chords_at(*G_VERSE)}, [
                      "In your headphones, could you hear the lead over yourself?",
                      "Did your \"oo\" stay soft on the high notes too?",
                  ]),
    ]),
    lesson("4-amazing-grace", "Amazing Grace, your backing", [
        learn("Three parts under the tune, kept as a song. First, your pad from lesson 1, beside today's.", [
            ("Then and now", "Your first pad beside today's, the same line"),
            ("Three of you under the tune", f"Low, middle, top; {SAFE}"),
            HEADPHONES,
        ], "harmony"),
        play("The low part, your pad from lesson 1, the tune at full volume this time. Nothing lit while you sing.",
             FIRST_PAD, GRACE.tempo, "Scored on your pad's notes on pitch, from memory.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE), lights="off", thenAndNow=KEEP),
        play("The middle part over your low part. Only the chord changes light.",
             AG_MID, GRACE.tempo, "Scored on your middle part's notes on pitch, most of them sung with no light to follow.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE), under=under(1), lights="changes"),
        play("The top part over both. Only the chord changes light. Three of you, under the tune.",
             AG_TOP, GRACE.tempo, "Scored on your top part's notes on pitch, over your two parts.",
             chords=GRACE.chords_at(*G_VERSE), lead=GRACE.lead(*G_VERSE), under=under(1, 2), lights="changes"),
    ], challenge=True, keepSong={"title": EN("Amazing Grace, my backing"), "takes": [
        {"step": 1, "name": EN("Low")}, {"step": 2, "name": EN("Middle")}, {"step": 3, "name": EN("Top")}],
        "from": 3, "partners": [EN("Lead")]}),
]}

# Shenandoah's low so, held through the half-beat chord at beat 5, is the only note a passing chord excuses.
assert {lid for lid, _ in PASSED_OVER} == {"bv-1-shenandoah"} and {b for _, b in PASSED_OVER} == {1}, PASSED_OVER

course = {
    "id": "backing-vocals",
    "version": 1,
    "headphones": "needed",  # what plays under you rests through a speaker (steps.json courseHeadphones)
    "reviewed": False,
    "title": EN("Backing vocals"),
    "units": [UNIT1, UNIT2, UNIT3, UNIT4],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(strip(course), open(OUT, "w"), ensure_ascii=False)
