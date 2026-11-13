"""Humming and lip trills (docs/courses/humming.md in the app's repo): writes course/plus/humming/course.json.
First written by hand (courses-songs, 2026-10-30, content-songs 84ede50, parked); generated from 2026-11-08 by
the courses lead, its steps as they were, with what's changed since:
- A lip trill's pitch is heard (the courses lead's tracker study on real trills, 2026-11-08): the tracker reads
  the voice's pitch, never the lips' flutter. But a trill sits just under the tracker's clarity bar, so its
  readings drop out while the sound goes on: `unbroken` (frontend's port) judges a break by the sound's
  loudness, and a trill step opts into a lower clarity bar (TRILL below, once the port names its field).
- The app can't tell a bubble from a hum when the lips stop, so the words say plainly that any easy sound
  counts, and "Did the bubble keep going?" stays a self-check.
- A fact on every lesson page, none on a challenge, each read in its source and checked twice.

Every step is in semitones from the singer's comfortable note, within a fifth below and an octave above it.
The checks fail the build on: a note or path point outside -5 to +12; a lesson without its safety line in
its first learn card when it opens a unit; a missing fact; a challenge with one; the house words.

    python3 -I tools/hum_course.py && python3 -I tools/coursefmt.py course/plus/humming/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/humming/course.json"
WRITE = True

BANNED = re.compile(r"\bstars?\b|—|\bpush|\bpower\b|\blouder\b(?! never)", re.I)
LOW, HIGH = -5, 12
# Frontend's `unbroken` port (the coordinator, 2026-11-08): breaks by loudness, edges trimmed, the path folded
# to its octave, and a trill step's own clarity bar. Set to the field it names (e.g. {"trill": True}) once it
# lands; until then a trill step is scored on the parked rule.
TRILL = {"trill": True}

TRY_ANY = "Can't trill yet? Hum or slide on \"oo\" instead: the app follows whatever easy sound you make."
UNBROKEN = "Scored on following the ribbon in one unbroken sound, never on how high or how long. The app can't tell a bubble from a hum, so either counts."
RIBBON = "Scored on following the ribbon."
HELD = "Scored on the note, held to its end."
NOTES = "Scored on the notes."


def EN(text):
    assert not BANNED.search(text), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards):
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "reviewed": False}


def path(points, band=150):
    for _, step in points:
        assert LOW <= step <= HIGH, f"a path point at {step} is outside {LOW} to {HIGH}"
    return {"seconds": points[-1][0], "kind": "path", "band": band, "points": [list(p) for p in points]}


def wave(text, lyric, target, measures, *, score=None, trill=False, **extra):
    ex = {"tempo": 60, "lead": 2, "step": 0, "lyric": lyric, "combo": False}
    if score:
        ex["score"] = score
    ex["target"] = target
    if trill:
        ex.update(TRILL)
    ex.update(extra)
    return {"kind": "wave", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def trill_ride(text, points, band=150, **extra):
    """A path on one bubble (`unbroken`): whatever easy sound you make, followed and kept going."""
    return wave(f"{text} {TRY_ANY}" if "Can't trill" not in text else text, "brr", [path(points, band)], UNBROKEN, score="unbroken", trill=True, **extra)


def held(text, lyric, beats=4):
    """A held note, heard then sung, scored on its pitch (a warm-up hum may wobble: a straight tone is the Vibrato
    course's skill, and the lane's straight target scored a beginner's slow wobble as nothing)."""
    return {"kind": "play", "text": EN(text), "exercise": {"tempo": 60, "turn": True, "notes": [{"beat": 0, "length": beats, "step": 0, "lyric": lyric}]},
            "measures": EN(HELD)}


def siren(text, points, **extra):
    return wave(text, "ng", [path(points)], RIBBON, **extra)


def notes(spec, lyric):
    """`step:length ...` from beat 0, each note on `lyric` (a list gives each note its own)."""
    out, beat = [], 0
    for i, token in enumerate(spec.split()):
        step, length = token.split(":")
        assert LOW <= int(step) <= HIGH, token
        out.append({"beat": beat, "length": float(length) if "." in length else int(length), "step": int(step),
                    "lyric": lyric[i] if isinstance(lyric, list) else lyric})
        beat += float(length) if "." in length else int(length)
    return out


def play(text, spec, lyric, measures=NOTES, **extra):
    return {"kind": "play", "text": EN(text), "exercise": {"tempo": 76, "turn": True, "notes": notes(spec, lyric), **extra}, "measures": EN(measures)}


def pair(text, pairs):
    """A held sound opening into another on the same note: [(step, first, second), ...], two beats each."""
    out, beat = [], 0
    for step, a, b, length in pairs:
        out += [{"beat": beat, "length": length, "step": step, "lyric": a}, {"beat": beat + length, "length": length, "step": step, "lyric": b}]
        beat += 2 * length
    return {"kind": "play", "text": EN(text), "exercise": {"tempo": 76, "turn": True, "notes": out}, "measures": EN(NOTES)}


def selfcheck(text, model, questions):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": 60, "lead": 2, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


# ---- The facts: each lesson page's "Did you know?", read in its source and checked twice ----

def fact(fid, text, source, url):
    assert len(text.split()) <= 45, fid
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


FACTS = {
    '1-coaster': fact('hum-one-buzz-or-two', 'A hum has one buzz, your vocal folds. A lip trill has two: the lips flutter too. A 2014 study of 23 people proposed sorting part-closed voice exercises into these two families.',
                         'Andrade PA, Wood G, Ratcliffe P, Epstein R, Pijper A, Svec JG, "Electroglottographic study of seven semi-occluded exercises: LaxVox, straw, lip-trill, tongue-trill, humming, hand-over-mouth, and tongue-trill combined with hand-over-mouth", Journal of Voice 2014', 'https://pubmed.ncbi.nlm.nih.gov/24560003/'),
    '1-bubble': fact('hum-brass-lip-buzz', 'Brass players learn to buzz with the lips alone, no instrument needed. Depending on how tight the lips are and how fast the air goes, the buzz comes out anywhere from a low raspberry to a high note.',
                        'UNSW Music Acoustics, "Brass instrument (lip reed) acoustics: an introduction"', 'https://newt.phys.unsw.edu.au/jw/brassacoustics.html'),
    '1-tune': fact('hum-trill-widens-range', 'In a 2020 study, 25 women did 3 minutes of lip trills. Straight after, their singing pitch range was wider on average, and their loudest notes rose by about 3 decibels.',
                      'Brockmann-Bauser M, Balandat B, Bohlender JE, "Immediate Lip Trill Effects on the Standard Diagnostic Measures Voice Range Profile, Jitter, Maximum Phonation Time, and Dysphonia Severity Index", Journal of Voice 2020', 'https://pubmed.ncbi.nlm.nih.gov/31196690/'),
    '2-ng': fact('hum-soft-palate-gate', 'Your soft palate, the soft back part of the roof of your mouth, is the gate to your nose. For "m" and "ng" it lowers, so air flows out through your nose.',
                    'University of Manitoba Linguistics (Kevin Russell), "Anatomy: Soft palate"', 'https://home.cc.umanitoba.ca/~krussll/phonetics/anatomy/soft-palate.html'),
    '2-bigger': fact('hum-siren-named-1819', 'The siren got its name in 1819 from Charles Cagniard de la Tour, who built it to measure the vibrations that make a sound. It sounded even under water, he wrote, so he named it after the singing Sirens of Greek myth.',
                        'Cagniard de la Tour, "Sur la Sirène, nouvelle machine d\'acoustique...", Annales de chimie et de physique 12 (1819), pp. 167-171, Internet Archive', 'https://archive.org/details/s3id13207800'),
    '2-open': fact('hum-maori-nga-breathe', 'In Māori, ng is one sound, and a word can begin with it: "ngā", ng opening into a long "ah", can mean "to breathe". English only lets ng end a syllable, as in sing, never start a word.',
                      'Te Aka Māori Dictionary, "ngā"', 'https://maoridictionary.co.nz/word/4504'),
    '3-buzz': fact('hum-face-buzz', "The buzz you feel in your face on an easy, ringing tone isn't sound echoing in your sinuses, an acoustic study argued. It's a sign your voice is turning breath into sound well.",
                      'Titze IR, "Acoustic interpretation of resonant voice", Journal of Voice 2001', 'https://pubmed.ncbi.nlm.nih.gov/11792028/'),
    '3-tune': fact('hum-nitric-oxide', 'Your sinuses make a gas called nitric oxide. In a 2002 study of 10 people, humming raised the amount in air breathed out through the nose fifteenfold over quiet breathing out.',
                      'Weitzberg E, Lundberg JO, "Humming greatly increases nasal nitric oxide", American Journal of Respiratory and Critical Care Medicine 2002', 'https://pubmed.ncbi.nlm.nih.gov/12119224/'),
    '3-open': fact('hum-jakobson-mama', 'Open a hum to "ah" and you get "ma". The linguist Roman Jakobson suggested that\'s where "mama" comes from: a nursing baby, mouth full, can only murmur through its nose, and once its mouth is free, opens the murmur into a vowel.',
                      'Roman Jakobson, "Why \'mama\' and \'papa\'?", Selected Writings I: Phonological Studies (Mouton, 1962), pp. 542-543', 'https://archive.org/details/selectedwritings01jako'),
    '4-trill-line': fact('hum-kele-trill-word', 'In Kele, spoken on Manus Island in Papua New Guinea, a lip trill can be part of a word: the word for face starts with m, then a lip trill, then "oo".',
                            'UCLA Phonetics Lab, Ladefoged, Vowels and Consonants (companion site), "Kele and Titan trills"', 'https://phonetics.ucla.edu/vowels/chapter13/kele.html'),
    '4-words': fact('hum-puccini-humming-chorus', 'The Humming Chorus in Puccini\'s Madama Butterfly, first staged at La Scala in Milan in 1904, has no words. A chorus offstage hums it; Puccini\'s sketch marks it "bocca chiusa", closed mouth.',
                       'Royal Society of Musicians of Great Britain, "From the Archives: Giacomo Puccini" (on its autograph sketch of the Humming Chorus)', 'https://www.rsmgb.org/news/from-the-archives-giacomo-puccini'),
    '4-warmup': fact('hum-warmup-trial', 'In a 2018 study, 30 pop and other commercial singers warmed up for 15 minutes, either with part-closed-mouth exercises or singing on an open "ah". Both groups said their voices felt better, and the two measured about the same.',
                        'Portillo MP, Rojas S, Guzman M, Quezada C, "Comparison of Effects Produced by Physiological Versus Traditional Vocal Warm-up in Contemporary Commercial Music Singers", Journal of Voice 32(2), 2018, 200-208', 'https://investigadores.uandes.cl/en/publications/comparison-of-effects-produced-by-physiological-versus-traditiona-2/'),
}


def lesson(lid, title, steps, **extra):
    assert len(steps) <= 5, lid
    if not extra.get("challenge"):
        assert lid in FACTS, f"hum-{lid}: every lesson page has a fact"
        extra = {"fact": FACTS[lid], **extra}
    else:
        assert "fact" not in extra, f"hum-{lid}: a challenge carries no fact"
    return {"id": f"hum-{lid}", "title": EN(title), **extra, "steps": steps}


COASTER = [(0, 0), (1.5, 5), (3, 0), (4.5, 7), (6, 0)]
FIVE_UP = "0:1 2:1 4:1 5:1 7:1 5:1 4:1 2:1 0:2"
TRILL_LINE = "0:1 2:1 4:1 2:1 4:1 5:1 4:2"
HUM_TUNE = "0:1 2:1 4:1 5:1 4:1 2:1 0:2"

UNIT1 = [
    lesson("1-coaster", "A roller coaster", [
        learn("A lip trill, or lip bubble, is a \"brr\" like a motorboat: loose lips fluttering on easy breath. It's one of the gentlest ways to wake your voice up.", [
            ("Loose lips", "A fingertip at each corner of your mouth helps"),
            ("Easy breath", "Never forced, just a steady flow"),
            ("Stop if it strains", "Tightens, tickles or hurts: rest. Don't sing when hoarse or ill"),
        ]),
        trill_ride("Ride the ribbon's roller coaster on one long bubble, without stopping: up, down, up again.", COASTER, band=200, generous=True, keep="humming.first-coaster"),
        selfcheck("One more bubble: hear the model, record yours, then listen back.", notes("0:2 5:2 0:2", "brr"),
                  ["Did the bubble keep going?", "If it stopped, did you hold your breath or tighten your jaw?"]),
    ]),
    lesson("1-bubble", "Keep it bubbling", [
        trill_ride("A gentler hill on one bubble.", [(0, 0), (2, 4), (4, 0)]),
        trill_ride("The same, a little longer, on one breath.", [(0, 0), (3, 5), (6, 0)]),
    ]),
    lesson("1-tune", "Trill on a tune", [
        play(f"Five notes up and back on a trill, heard then sung. {TRY_ANY}", FIVE_UP, "brr", **TRILL),
        selfcheck("Trill the top note once more and listen back.", notes("7:3", "brr"), ["Did your jaw stay loose?", "Did the bubble keep going on the high note?"]),
    ]),
    lesson("1-challenge", "The big dipper", [
        learn("A longer roller coaster, up to about an octave and back, on one bubble.", [
            ("Breathe first", "Then the whole ride"),
            ("Light at the top", "Easy, never forced; stop if anything tightens or hurts"),
        ]),
        trill_ride("The big dipper, on one bubble.", [(0, 0), (2, 7), (3.5, 2), (5.5, 12), (8, 0)], band=200),
    ], challenge=True),
]

UNIT2 = [
    lesson("2-ng", "Ng", [
        learn("\"Ng\" is the sound at the end of \"sing\": the back of your tongue up, your jaw easy, the sound coming out through your nose.", [
            ("Say \"sing\"", "And keep the end going"),
            ("Jaw easy", "Teeth a little apart"),
            ("Quiet", "A gentle, buzzy hum; stop if anything tightens or hurts"),
        ]),
        held("Hold an easy \"ng\".", "ng"),
        siren("A small siren on \"ng\", up and back.", [(0, 0), (2, 4), (4, 0)]),
    ]),
    lesson("2-bigger", "Bigger sirens", [
        siren("Up a sixth and back on \"ng\".", [(0, 0), (2.5, 9), (5, 0)]),
        siren("Up an octave and back, easy at the top.", [(0, 0), (3, 12), (6, 0)]),
    ]),
    lesson("2-open", "Ng to ah", [
        pair("A held \"ng\" opening into \"ah\" on the same note, heard then sung.", [(0, "ng", "ah", 2), (4, "ng", "ah", 2)]),
        selfcheck("Once more, then listen back.", [{"beat": 0, "length": 2, "step": 0, "lyric": "ng"}, {"beat": 2, "length": 2, "step": 0, "lyric": "ah"}],
                  ["Did the \"ah\" keep the buzz of the \"ng\"?"]),
    ]),
    lesson("2-challenge", "Siren loops", [
        learn("Two loops up and over on \"ng\", easy all the way.", [
            ("Light at the top", "Easy, never forced; stop if anything tightens or hurts"),
            ("One breath each", "Or a quick one between"),
        ]),
        siren("Two siren loops on \"ng\".", [(0, 0), (1.5, 7), (3, 0), (4.5, 7), (6, 0)], generous=True),
    ], challenge=True),
]

UNIT3 = [
    lesson("3-buzz", "A buzzing hum", [
        learn("Lips together, teeth apart, and hum. Feel for a buzz on your lips and around your nose: it's a good sign.", [
            ("Lips together", "Teeth apart"),
            ("Feel the buzz", "Lips and nose"),
            ("Easy", "Talking volume or quieter; stop if anything tightens or hurts"),
        ]),
        held("Hold an easy hum.", "mm"),
        selfcheck("Hum once more and listen back.", notes("0:4", "mm"), ["Did you feel a buzz on your lips?"]),
    ]),
    lesson("3-tune", "Hum a tune", [
        play("A short tune, hummed, heard then sung.", HUM_TUNE, "mm"),
    ]),
    lesson("3-open", "Hum to open", [
        pair("\"Mm\" opening into \"ah\" on one note, heard then sung.", [(0, "mm", "ah", 2)]),
        pair("Now on three notes going up.", [(0, "mm", "ah", 1), (2, "mm", "ah", 1), (4, "mm", "ah", 1)]),
    ]),
    lesson("3-challenge", "Hum a line", [
        learn("A longer hummed line. Keep the buzz all the way through.", [
            ("Lips together", "Teeth apart"),
            ("Easy", "Never forced; stop if anything tightens or hurts"),
        ]),
        play("Hear it, then hum it back.", "0:1 2:1 4:1 7:1 5:1 4:1 2:1 4:1 2:1 0:2", "mm"),
    ], challenge=True),
]

UNIT4 = [
    lesson("4-trill-line", "Trill into a line", [
        play(f"A line on a trill, heard then sung. {TRY_ANY}", TRILL_LINE, "brr", **TRILL),
        play("The same line on \"ah\".", TRILL_LINE, "ah"),
        selfcheck("Sing it on \"ah\" once more and listen back.", notes(TRILL_LINE, "ah"), ["Did the sung one feel as easy as the trill?"]),
    ]),
    lesson("4-words", "Hum into words", [
        play("A line hummed, heard then sung.", "0:1 2:1 4:1 5:1 4:2", "mm"),
        play("Now on its words.", "0:1 2:1 4:1 5:1 4:2", ["Good", "morn-", "ing,", "my", "voice"]),
    ]),
    lesson("4-warmup", "A three-minute warm-up", [
        trill_ride("A trill hill.", [(0, 0), (2, 5), (4, 0)]),
        siren("An \"ng\" siren.", [(0, 0), (2.5, 9), (5, 0)]),
        play("A hummed line.", HUM_TUNE, "mm"),
    ]),
    lesson("4-challenge", "Your warm-up", [
        learn("Your first roller coaster beside today's, then a line sung on a warmed-up voice.", [
            ("One bubble", "Up, down, up again"),
            ("Then sing", "Easy, at talking volume; stop if anything tightens or hurts"),
        ]),
        trill_ride("The roller coaster again, on one bubble.", COASTER, band=200, thenAndNow="humming.first-coaster"),
        play("A line on \"la\", heard then sung.", FIVE_UP, "la"),
    ], challenge=True),
]

course = {
    "id": "humming-and-lip-trills", "version": 1, "reviewed": False, "title": EN("Humming and lip trills"),
    "units": [
        {"id": "hum-trill", "title": EN("The lip trill"), "colour": 1, "lessons": UNIT1},
        {"id": "hum-ng", "title": EN("The \"ng\" siren"), "colour": 3, "lessons": UNIT2},
        {"id": "hum-hum", "title": EN("Resonant humming"), "colour": 5, "lessons": UNIT3},
        {"id": "hum-song", "title": EN("From warm-up to song"), "colour": 2, "lessons": UNIT4},
    ],
}

missing = [l["id"] for u in course["units"] for l in u["lessons"] if not l.get("challenge") and "fact" not in l]
if missing:
    print("facts still to come:", ", ".join(missing))
if WRITE:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(course, open(OUT, "w"), ensure_ascii=False)
