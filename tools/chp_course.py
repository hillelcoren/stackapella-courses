"""Learn your part for rehearsal (docs/courses/choir-part.md in the app's repo): writes
course/plus/choir-part/course.json. A short course for choir members: one piece, O Come, All Ye
Faithful (library), learned on the alto the way a choir member learns a part at home before
rehearsal. Every sung step names the song's own phrases (`exercise.song`), so the notes come with the
song and are placed in the singer's own key and octave, as in the song courses.

    python3 -I tools/chp_course.py && python3 -I tools/coursefmt.py course/plus/choir-part/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/choir-part/course.json"

BANNED = re.compile(r"\b(stars?|starring|christmas|carols?|advent|festive|season)\b|—", re.I)
SONG = "o-come-all-ye-faithful"
# The singer picks their part (docs/courses/choir-part-sections-plan.md): every song step sings "yours",
# the app resolving it to the pick. A step's own words are the default part's (alto); BY_PART's soprano,
# tenor and bass words replace them where a card speaks about the part's own notes.
PART = "yours"
PARTS = ["soprano", "alto", "tenor", "bass"]
DEFAULT = "alto"
TEMPO = 94
NOTES = "Scored on the notes."
SAFETY = "Sing at an easy, medium-soft volume, not a whisper. If a note sits too high or low, sing it lightly, never louder. Stop if anything tightens or hurts."


def EN(text):
    assert not BANNED.search(text), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def song(phrases, others=False):
    spec = {"template": SONG, "part": PART, "phrases": list(phrases)}
    if others:
        spec["with"] = "others"
    return spec


def learn(headline, cards, visual="harmony", listen=None, by_part=None):
    """by_part: {part: (headline, cards)} for the parts whose words differ from the default's."""
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}
    if listen:
        step["listen"] = listen
    if by_part:
        assert set(by_part) <= set(PARTS) - {DEFAULT}, by_part.keys()
        step["byPart"] = {p: {"headline": EN(h), "steps": [card(*c) for c in cs]} for p, (h, cs) in by_part.items()}
    return step


def hear(phrases, others=False, tempo=None):
    """A learn card's example: the guide sings it (and the others, when asked)."""
    listen = {"song": song(phrases, others), "turn": False}
    if tempo:
        listen["tempo"] = tempo
    return listen


def sing(text, phrases, *, others=False, turn=False, guide=True, tempo=None, measures=NOTES, kind="play", text_by_part=None, **extra):
    exercise = {"song": song(phrases, others), "turn": turn}
    if tempo:
        exercise["tempo"] = tempo
    if not guide:
        exercise["guide"] = False
    exercise.update(extra)
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if text_by_part:
        assert set(text_by_part) <= set(PARTS) - {DEFAULT}, text_by_part.keys()
        step["textByPart"] = {p: EN(t) for p, t in text_by_part.items()}
    if kind == "play":
        step["measures"] = EN(measures)
    return step


def wait_for_me(text, phrases, tempo=None):
    exercise = {"song": song(phrases)}
    if tempo:
        exercise["tempo"] = tempo
    return {"kind": "try", "text": EN(text), "exercise": exercise}


# Each unit page's "Did you know?" (docs/seo-lesson-pages-plan.md), read in its source and checked again.
FACTS = {
    "1-hear": {"id": "self-to-other-ratio", "text": EN("In a 1999 study with a synthesized choir, each singer liked their own voice at a narrow level, typically within 2 decibels either way, but levels ranged from about even to 15 decibels louder."), "source": EN("Ternström, JASA (1999)"), "url": "https://europepmc.org/article/MED/10380674"},
    "2-lines": {"id": "not-how-much-but-how", "text": EN("In a 2009 study, advanced pianists practised a hard three-bar passage. How long they practised didn't predict how well they played it the next day. What share of their tries they played right did."), "source": EN("Duke, Simmons and Cash, Journal of Research in Music Education (2009)"), "url": "https://doi.org/10.1177/0022429408328851"},
    "3-refrain": {"id": "james-recollect", "text": EN("In 1890 William James wrote that once you almost know a piece by heart, \"it pays better to wait and recollect by an effort from within\" than to look at the book again."), "source": EN("James, The Principles of Psychology (1890), chapter 16, York University Classics in the History of Psychology"), "url": "https://psychclassics.yorku.ca/James/Principles/prin16.htm"},
    "4-ready": {"id": "sleep-on-the-melody", "text": EN("In a 2006 study, people who learned a short piano melody played it more accurately after a night's sleep, with no further practice. The same hours awake brought no significant gain."), "source": EN("Simmons and Duke, Journal of Research in Music Education (2006)"), "url": "https://doi.org/10.1177/002242940605400308"},
}


def lesson(lid, title, steps, **extra):
    fact = {"fact": FACTS[lid]} if lid in FACTS else {}
    return {"id": f"chp-{lid}", "title": EN(title), **fact, **extra, "steps": steps}


# The chord a pianist gives, and the note to find in it: each group's call is the chord sung up
# (do, mi, sol of its key, in steps from the singer's note), its answer one of them.
def from_the_chord(key, sing_degree):
    call = [key, key + 4, key + 7]
    return {"call": call, "sing": [call[sing_degree]], "chord": {"root": key}}


UNIT1 = {
    "id": "chp-1", "title": EN("Your line in the sound"), "colour": 3,
    "lessons": [
        lesson("1-hear", "Hear your line", [
            learn("Learn a choir part the way it sticks: hear it in the whole sound, then on its own, then sing it with the others.", [
                ("Hear everyone first", "The start of the song, every part"),
                ("Your part", "Pick soprano, alto, tenor or bass: it's set in your own range, and you can change it any time"),
                ("Sing easy", SAFETY),
            ], listen=hear([0, 1], others=True)),
            learn("Now the alto on its own. Follow the words.", [
                ("Its shape", "It starts low and holds, then climbs"),
                ("Under the tune", "Most of the way you sit under the tune. Lost? Find the tune and stay under it."),
            ], listen=hear([0, 1]), by_part={
                "soprano": ("Now the soprano on its own: the tune. Follow the words.", [
                    ("Its shape", "It starts on home, dips low on \"all\" and again on \"faithful\", then leaps up and climbs to \"triumphant\""),
                    ("The tune", "You carry the tune, the line the others fit around. Lost? Come back in at the next line."),
                ]),
                "tenor": ("Now the tenor on its own. Follow the words.", [
                    ("Its shape", "It starts low and holds, climbs to \"faithful\", then stays on that note through most of \"joyful and triumphant\""),
                    ("Between alto and bass", "Most of the way you sit under the alto and over the bass. Lost? Find the bass and stay above it."),
                ]),
                "bass": ("Now the bass on its own. Follow the words.", [
                    ("Its shape", "It climbs to \"faithful\", then jumps about on \"joyful and triumphant\""),
                    ("At the bottom", "You're the lowest line, often on the chord's bottom note. Lost? Listen for the chord and find its bottom note."),
                ]),
            }),
            wait_for_me("Find the notes of line 1: each one waits until you're on it.", [0]),
            sing("Sing lines 1 and 2 with the guide and the other parts around you.", [0, 1], others=True, generous=True, keep="choir-part.first",
                 measures="Scored on the notes. Listen back: could you hear your line inside the chords?"),
        ], strictness="relaxed"),
        lesson("1-first", "Your first note", [
            learn("At rehearsal the pianist plays a chord, and you find your note in it.", [
                ("The chord, then your note", "Hear the chord's bottom, middle and top notes, then sing the one asked for"),
                ("The alto here", "It starts on the chord's middle note, below the tune"),
                ("Think before you sing", "Hear the note in your head first, then start right on it"),
            ], visual="echo", by_part={
                p: ("At rehearsal the pianist plays a chord, and you find your note in it.", [
                    ("The chord, then your note", "Hear the chord's bottom, middle and top notes, then sing the one asked for"),
                    (f"The {p} here", where),
                    ("Think before you sing", "Hear the note in your head first, then start right on it"),
                ]) for p, where in [
                    ("soprano", "It starts on home, the bass's note sung high, at the top of the sound"),
                    ("tenor", "It starts on the chord's bottom note, home, an octave under the tune"),
                    ("bass", "It starts on the chord's bottom note, home, the lowest note in the sound"),
                ]}),
            {"kind": "bullseye", "text": EN("Hear the chord's three notes, then sing the one asked for: the middle note, the top note, then the bottom one."),
             "exercise": {"tempo": 72, "think": 1, "echoes": [from_the_chord(0, 1), from_the_chord(-3, 2), from_the_chord(2, 0)]}},
            sing("Now line 1 starting cold: no guide, the other parts on. Give me my note is there if you need it.", [0], others=True, guide=False, giveNote=True),
        ], strictness="relaxed"),
        lesson("1-page", "Your line on the page", [
            learn("In a choir score your line is one of four. Find it, follow it with the words, and see where it climbs and where it holds.", [
                ("Where it holds", "Three notes the same, then up"),
                ("Above the tune", "At \"faithful\" your line ends above the tune. Hold your note."),
                ("Mark your breaths", "Pencil in your score where you'll breathe, so you never run out mid-line"),
            ], visual="phrase", by_part={
                p: ("In a choir score your line is one of four. Find it, follow it with the words, and see where it climbs and where it holds.", [
                    a, b, ("Mark your breaths", "Pencil in your score where you'll breathe, so you never run out mid-line"),
                ]) for p, a, b in [
                    ("soprano", ("Where it moves", "Two notes the same, then down to \"all\" and back up"), ("Low at the end", "At \"faithful\" the tune falls a fifth to its lowest note, the one you sang on \"all\". Land it lightly.")),
                    ("tenor", ("Where it holds", "Three notes the same, then up"), ("Meet the tune", "At \"faithful\" the tune comes down to your note, so you both sing the same note. Hold it steady.")),
                    ("bass", ("Where it holds", "Two notes the same, up a third to two more the same, then up a step at a time"), ("Up to \"faithful\"", "Your line climbs to \"faithful\": hold \"faith-\" its full two beats, then step up.")),
                ]}),
            sing("Read line 1 on the stave and sing it with the guide.", [0], staff={"names": "on", "look": 4}),
            sing("Line 2, the names fainter now: read it and sing it with the guide.", [1], staff={"names": "faint", "look": 4}),
        ], strictness="relaxed"),
        lesson("1-two", "The first two lines", [
            sing("Lines 1 and 2 cold: find your first note, then no guide, just you and the other parts.", [0, 1], others=True, guide=False, giveNote=True),
        ], strictness="relaxed", challenge=True),
    ],
}

UNIT2 = {
    "id": "chp-2", "title": EN("Fix the hard bars"), "colour": 3,
    "lessons": [
        lesson("2-lines", "Two new lines", [
            learn("Learn a new line a little slower, then join it to the next, so the joins get practised too. The joins are where singers get lost.", [
                ("One line, slower", "Hear it, then sing it back"),
                ("The next line", "The same"),
                ("Then both together", "At speed, with the guide, straight through the join"),
            ], visual="phrase"),
            sing("Hear line 3, a little slower, then sing it back.", [2], turn=True, tempo=72),
            sing("Hear line 4, a little slower, then sing it back.", [3], turn=True, tempo=72),
            sing("Lines 3 and 4 joined, at speed, with the guide.", [2, 3]),
        ]),
        lesson("2-find", "Find the hard bars", [
            learn("Most of a part comes easily. A few bars don't: give them the time.", [
                ("What makes a bar hard", "A jump, a note from outside the key, or your line moving while the others hold"),
                ("This one", "On \"-hem\" you slip down a half step to a note from outside the key, just above the second \"O\" and \"to\", then leap up a fourth to a long note above the tune."),
                ("Slow it right down", "Same notes, same pitch, much slower. Take a quick breath from the end of \"O come ye,\" and keep it easy."),
            ], visual="phrase", listen=hear([2], tempo=60), by_part={
                p: ("Most of a part comes easily. A few bars don't: give them the time.", [
                    ("What makes a bar hard", "A jump, a note from outside the key, or your line moving while the others hold"),
                    ("This one", this),
                    ("Slow it right down", "Same notes, same pitch, much slower. Take a quick breath from the end of \"O come ye,\" and keep it easy."),
                ]) for p, this in [
                    ("soprano", "The line climbs a step at a time to \"Beth-\", then the tune drops a fourth on \"-le-\" and steps down to a long low note on \"-hem\"."),
                    ("tenor", "On \"to\" you dip a third to a low note, climb back on \"Bethlehem\", then stay on one note from \"-le-\" to the end, almost seven beats. Keep it steady as the chords change."),
                    ("bass", "The line steps up and rocks, drops a third on \"to\", then \"Bethlehem\" jumps: up a third, down a fourth, then up a fourth to a long note."),
                ]}),
            wait_for_me("Line 3, slowly: each note waits until you're on it.", [2], tempo=60),
            sing("Line 3 slowly on the stave, with the guide: watch for the note from outside the key.", [2], tempo=60, staff={"names": "on", "look": 4},
                 text_by_part={"soprano": "Line 3 slowly on the stave, with the guide: watch for the drop on \"Bethlehem\".",
                               "tenor": "Line 3 slowly on the stave, with the guide: watch the dip on \"to\" and the long last note.",
                               "bass": "Line 3 slowly on the stave, with the guide: watch the drop on \"to\" and the jumps on \"Bethlehem\"."}),
        ]),
        lesson("2-speed", "Up to speed", [
            learn("Slow and clean first, then a little faster each time. A bar you can sing slowly comes at speed; a bar you always rush never does.", [
                ("A little faster", "With the guide"),
                ("Faster again", "Still with the guide"),
                ("Full speed", "No guide, the other parts on, as at rehearsal"),
            ], visual="phrase"),
            sing("Line 3 a little faster, with the guide.", [2], tempo=72),
            sing("Faster again, with the guide.", [2], tempo=84),
            sing("Full speed, the guide off, the other parts on.", [2], others=True, guide=False),
        ]),
        lesson("2-verse", "The verse", [
            sing("The verse at full speed, the guide off: the hard bar where it lives.", [0, 1, 2, 3], others=True, guide=False, giveNote=True),
        ], challenge=True),
    ],
}

UNIT3 = {
    "id": "chp-3", "title": EN("Guide on, guide off"), "colour": 3,
    "lessons": [
        lesson("3-refrain", "The refrain", [
            learn("The three \"O come, let us adore him\" lines share the words and the same three neighbouring notes, in a different order each time. The first drops low on \"him\", the second ends high, and the third drops low again, then goes on to \"Christ the Lord\".", [
                ("Not the tune", "Meanwhile the tune climbs, so you can't just follow it"),
                ("The rests", "Cut \"him\" off short, breathe in the rest, and come in on \"O\" just before the beat"),
            ], listen=hear([4, 5, 6]), by_part={
                "soprano": ("The three \"O come, let us adore him\" lines build: the second is much the same shape a third higher, and the third starts there, steps down through \"adore him\", then leaps up a fourth to \"Christ the Lord\".", [
                    ("Lead the climb", "The alto and tenor stay near their notes while you rise. The climb is yours: let it grow, never push."),
                    ("The rests", "Cut \"him\" off short, breathe in the rest, and come in on \"O\" just before the beat"),
                ]),
                "tenor": ("The three \"O come, let us adore him\" lines are each different for you: the first leaps up a fifth on \"us\", to the alto's note, the second stays almost on one note, and the third stays near it, then falls to \"Lord\".", [
                    ("Hold your ground", "In the second line the tune climbs while you stay near one note. Don't drift up with it."),
                    ("The rests", "Cut \"him\" off short, breathe in the rest, and come in on \"O\" just before the beat"),
                ]),
                "bass": ("The three \"O come, let us adore him\" lines jump for you: the first drops a sixth to a low \"him\", the second starts an octave above it, and the third starts back on the low note.", [
                    ("Hear the jump first", "Before line 6, hear its first note in your head: an octave above your last \"him\", on the tenor's note"),
                    ("The rests", "Cut \"him\" off short, breathe in the rest, and come in on \"O\" just before the beat"),
                ]),
            }),
            sing("Hear line 5, a little slower, then sing it back.", [4], turn=True, tempo=72),
            sing("Line 6 on the stave, a little slower, with the guide: spot what changed.", [5], tempo=72, staff={"names": "faint", "look": 4}),
            sing("The whole refrain at speed, with the guide and the other parts.", [4, 5, 6], others=True),
        ]),
        lesson("3-last", "The last line", [
            learn("The last line jumps: up a fourth to \"Christ\", up a third to \"Lord\", then down a fifth inside \"Lord\" to a long low note.", [
                ("Breathe first", "Shorten \"him,\" a little to breathe, then sing \"Christ the Lord\" in one breath"),
                ("Slowly, then faster", "With the guide, then without"),
                ("Ring the last chord", "Your long low note is the chord's middle note: listen for it to settle"),
            ], visual="phrase", by_part={
                p: (head, [
                    ("Breathe first", "Shorten \"him,\" a little to breathe, then sing \"Christ the Lord\" in one breath"),
                    ("Slowly, then faster", "With the guide, then without"),
                    ("Ring the last chord", ring),
                ]) for p, head, ring in [
                    ("soprano", "The last line climbs a fourth to \"Christ\", then steps down through \"the Lord\" to a long note on home.", "Your long last note is the chord's bottom note, home: listen for it to settle"),
                    ("tenor", "The last line stays put: \"him, Christ the\" on one note, then down a fourth to \"Lord\", on the bass's note: your lowest, held long.", "Hold your low note steady while the chord changes under it. It ends as the chord's top note, sung low."),
                    ("bass", "The last line moves down a third to \"Christ\", up a step to \"the\", then down a fifth inside \"Lord\" to a long low note.", "Your long low note is the chord's bottom note, home: listen for the others to settle on it"),
                ]}),
            sing("Hear the last line slowly, then sing it back.", [6], turn=True, tempo=60),
            sing("The last line a little faster, with the guide and the chords.", [6], tempo=84, tuning=True),
            sing("The last line at speed, the guide off, the other parts on.", [6], others=True, guide=False, giveNote=True),
        ]),
        lesson("3-away", "The guide steps away", [
            learn("The guide is there to learn from, then to put down. Put it down early: at rehearsal there's no guide in your ear.", [
                ("The whole part", "Every line you've learned, joined"),
                ("The lights fade", "Halfway through your notes stop lighting: keep going by ear"),
            ]),
            sing("The whole part with the guide and the other parts. Halfway, the lights fade.", [0, 1, 2, 3, 4, 5, 6], others=True, lights="fade"),
        ]),
        lesson("3-alone", "Your part, on your own", [
            sing("The whole part, start to end: no guide, the other parts on. Find your first note as you did before; Give me my note is there if you need it.", [0, 1, 2, 3, 4, 5, 6], others=True, guide=False, giveNote=True),
        ], challenge=True),
    ],
}

UNIT4 = {
    "id": "chp-4", "title": EN("Ready for rehearsal"), "colour": 3,
    "lessons": [
        lesson("4-ready", "The morning of", [
            learn("The night before: one run-through at full speed, then rest your voice. The morning of: a short, gentle hum, then your first note.", [
                ("A gentle hum", "Soft and easy, against a quiet drone"),
                ("Then your first note", "Found cold, as at rehearsal"),
            ], visual="steady"),
            {"kind": "wave", "text": EN("Hum a soft, easy, straight \"mm\" on the drone's note, three times: one plain tone, no wave."),
             "exercise": {"tempo": 60, "lead": 2, "step": 0, "lyric": "mm", "drone": {"step": 0},
                          "target": [{"seconds": 5, "kind": "straight"}, {"seconds": 5, "kind": "straight"}, {"seconds": 5, "kind": "straight"}], "generous": True},
             "measures": EN("Scored on how straight the hum stayed: no wave in it.")},
            sing("The refrain cold: no guide, the other parts on.", [4, 5, 6], others=True, guide=False, giveNote=True),
        ]),
        lesson("4-keep", "Don't stop", [
            learn("At rehearsal nobody stops for you. If you get lost, listen, and come back in at the start of the next line.", [
                ("No lights while you sing", "Your notes are shown after the take, not during it"),
                ("Lost?", "Keep listening. The rests between lines, like the one after each \"him\", are your way back in."),
            ]),
            sing("The whole part with the other parts, no guide, nothing lit while you sing. Sing it as you will at rehearsal.", [0, 1, 2, 3, 4, 5, 6], others=True, guide=False, lights="off"),
        ]),
        lesson("4-dress", "Dress rehearsal", [
            learn("What you've just done works for every piece: hear it, find your note, a line at a time, fix the hard bars, put the guide down, and don't stop.", [
                ("Your own section", "Every library song has Learn it step by step, part by part: pick yours"),
                ("Now record it", "The whole part in Sing, with the other three parts"),
                ("Choir groups", "If your director uses Stackapella, a choir group puts the choir's songs in one place, with your part already picked."),
            ]),
            sing("First, the two lines you began with, now on your own. Then hear how far you've come.", [0, 1], others=True, guide=False, giveNote=True, thenAndNow="choir-part.first"),
            {"kind": "record", "text": EN("The dress rehearsal: record your part in Sing, with the other three parts around you."),
             "template": SONG, "singers": 4, "part": PART, "measures": EN("Scored on the notes of your recording.")},
        ], challenge=True),
    ],
}

course = {
    "id": "choir-part",
    "version": 1,
    "reviewed": False,
    "title": EN("Learn your part for rehearsal"),
    "parts": {"template": SONG, "choose": PARTS, "default": DEFAULT},
    "units": [UNIT1, UNIT2, UNIT3, UNIT4],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"), ensure_ascii=False)
