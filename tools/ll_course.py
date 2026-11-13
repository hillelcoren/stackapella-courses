"""Live looping (docs/courses/live-looping.md in the courses repo): writes course/plus/live-looping/course.json.
Built from the courses lead's build spec, on the reviewers' rewritten lessons (a voice teacher who loops, then
a game designer): a bass you loop from lesson 1, parts that sit in its gaps, a pad and a rhythm part, then
three tunes on loops (Row, Row, Row Your Boat; Are You Sleeping; Drunken Sailor), and your own picks kept as a
song. Every note counts from the singer's comfortable note (0) and sits from -5 to +9.

Layers use `exercise.under: { steps: [n | { step, loop }], loop? }`: each earlier take loops from its beat 0.
So every take that becomes a layer starts singing on beat 0 and stops half a beat or more before the loop
comes round (the seam); a top part, never looped, may listen once round first (loops of up to 16 beats).
The course's own overdubs (gap parts, pads, rhythm parts, picks) never sing a note a loop is sounding at the
same moment; only the songs' own tunes meet their bass, as those songs do.

    python3 -I tools/ll_course.py && python3 -I tools/coursefmt.py course/plus/live-looping/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/live-looping/course.json"
ROW = REPO / "templates/library/row-row-row.json"
FRERE = REPO / "templates/free/are-you-sleeping.json"

BANNED = re.compile(r"\bstars?\b|—", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)
SOLFA = {"do": 0, "re": 2, "mi": 4, "fa": 5, "fi": 6, "so": 7, "la": 9, "ti": 11}
LOW, HIGH = -5, 9  # the span: steps from the singer's comfortable note
LISTEN_UP_TO = 16  # a top part listens once round first when the loop is this many beats or fewer
COLOUR = 4

SAFETY = "Easy volume, your middle notes, the bass light; stop if anything tightens or hurts."
BASS_SAFETY = "Easy volume, light, never pressed; stop if anything tightens or hurts."
# Said once, after the course's first layer: from then on Sing it again is simply there.
RESING = "Not happy with it? Sing it again: the next step loops your latest take."
HEADPHONES = ("Headphones on", "Through a speaker, your loops rest while you sing")
# A play step scores pitch alone unless it opts into timing: the bass, gap and rhythm layers, where the
# loop's beat is the point, take `rhythm` (pitch 70, timing 30; docs/play-timing-plan.md in the app's repo)
# and say so. The pads and the tunes stay on pitch.
PITCH = "Scored on your notes on pitch."
PITCH_BEAT = "Scored on your notes on pitch and on the beat."
LIT_BEAT = "Scored on landing either lit note, on pitch and on the beat."
ENTRY = "Scored on coming back in on time and on pitch after the rest."
RELEASE = "Scored on stopping each note on time, steady to its end, before the loop comes round."
CHOSE = "Scored on the rounds you got right first time."
KEEP = "looping.first-loop"


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def num(x):
    """Beats to six decimals (the templates' rule), whole numbers as ints."""
    x = round(x, 6)
    return int(x) if x == int(x) else x


def sf(name, home=0):
    """A sol-fa name to steps from the singer's note: `so,` is below do; `home` moves do (Row's is -5)."""
    below = name.endswith(",")
    return SOLFA[name.rstrip(",")] - (12 if below else 0) + home


def note(beat, length, step, lyric=None, choices=None):
    n = {"beat": num(beat), "length": num(length), "step": step}
    if lyric:
        n["lyric"] = lyric
    if choices:
        assert choices[0] == step, choices
        n["choices"] = choices
    return n


def line(tokens, lyric=None, home=0):
    """[(beat, length, name, lyric?)] in sol-fa, or with a list of names for lit choices."""
    out = []
    for beat, length, name, *word in tokens:
        if isinstance(name, list):
            steps = [sf(x, home) for x in name]
            out.append(note(beat, length, steps[0], (word or [lyric])[0], steps))
        else:
            out.append(note(beat, length, sf(name, home), (word or [lyric])[0]))
    return out


def passes(notes, loop, count, start=0, bar=4):
    """A one-pass line sung `count` times round a `loop` of whole bars, from `start` beats."""
    assert loop % bar == 0, f"a loop of {loop} beats is not whole bars of {bar}"
    assert start % bar == 0, f"a line starting at {start} is not on a bar line"
    end = max(n["beat"] + n["length"] for n in notes)
    assert end <= loop + 1e-9, f"a pass ends at {end}, past its loop of {loop}"
    return [{**n, "beat": num(n["beat"] + start + k * loop)} for k in range(count) for n in notes]


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual, listen=None):
    assert len(cards) <= 3, headline
    assert HEADPHONES in cards, f"every learn step says headphones on: {headline}"
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}
    if listen:
        step["listen"] = listen
    return step


def under(*layers, loop=None):
    """Layers to sing over: step numbers, or (step, loop) for a layer with its own loop."""
    steps = [n if isinstance(n, int) else {"step": n[0], "loop": n[1]} for n in layers]
    u = {"steps": steps}
    if loop:
        u["loop"] = loop
    return u


def play(text, notes, tempo, measures, *, tune=False, **extra):
    """A sung step over the loop (turn: false). `tune`: a song's own tune, which may meet its bass."""
    step = {"kind": "play", "text": EN(text), "exercise": {"tempo": tempo, "turn": False, "notes": notes, **extra}, "measures": EN(measures)}
    if tune:
        step["_tune"] = True
    return step


def bass(text, notes, tempo, home=0, measures=PITCH_BEAT, **extra):
    """A bass layer: from beat 0, the drone on home for a bar then gone, so you lock to yourself. Scored on
    the beat too, unless it has its own `score`."""
    assert BASS_SAFETY in text, text
    if "score" not in extra:
        extra["rhythm"] = True
    return play(text, notes, tempo, measures, drone={"step": home, "fadeAfter": 4}, **extra)


def wait_for_me(text, notes, tempo):
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes}}


def choose(text, tempo, rounds):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": [
        {"prompt": EN(p), "clips": [{"notes": c} for c in clips], "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


# Each lesson page's "Did you know?" (2026-11-08): read in its source, then checked again.
FACTS = {
    "1-loop": {"id": "closed-groove", "text": EN("Pierre Schaeffer looped sound on records before tape. In Paris from 1948 he used records with a \"closed groove\" to repeat bits of sound; in the early 1950s he moved the idea to magnetic tape loops."), "source": EN("Levaux, The Forgotten History of Repetitive Audio Technologies, Organised Sound (2017)"), "url": "https://doi.org/10.1017/S1355771817000097"},
    "1-lock": {"id": "predict-not-react", "text": EN("Reacting to a sound takes about 160 milliseconds on average, a 2013 paper notes, yet trained ensemble musicians typically land 30 to 50 milliseconds apart: too close for reacting alone, which suggests they predict."), "source": EN("van der Steen and Keller, Frontiers in Human Neuroscience (2013)"), "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3677131"},
    "1-longer": {"id": "rhythm-changes", "text": EN("Your four-bar loop moves through chords on do, la, re and so. The A sections of jazz's \"rhythm changes\", from Gershwin's I Got Rhythm (1930), repeat that same sequence: I, vi, ii, V."), "source": EN("Mark Watkins, Rhythm Changes, Brigham Young University-Idaho (2010)"), "url": "https://content.byui.edu/file/be14498b-aa3f-4b2a-b9e6-4fb3fdbd1d12/1/10%20Rhythm%20Changes.pdf"},
    "2-pad": {"id": "mellotron-eight-seconds", "text": EN("The Mellotron, made in England from 1963, played a strip of recorded tape under each key, with a choir among its sounds. A held note usually lasted about eight seconds before the tape ran out."), "source": EN("Reid, Mellotron MkVI, Sound On Sound (2002)"), "url": "https://www.soundonsound.com/sos/Aug02/articles/mellotron.asp"},
    "2-rhythm": {"id": "puirt-a-beul", "text": EN("Scotland's puirt à beul, \"tunes from a mouth\", set Gaelic words to dance tunes. In 1911 the Gaelic song collector Frances Tolmie wrote that they were \"sung as a substitute for instrumental dance-music\"."), "source": EN("Frances Tolmie, Journal of the Folk-Song Society 4, no. 16 (1911), Internet Archive"), "url": "https://archive.org/details/sim_folk-song-society-journal_1911_4_16"},
    "2-three": {"id": "chipmunks-one-voice", "text": EN("The Chipmunks, first heard on a 1958 record, were human voices sung slowly onto tape. Played back faster, they came out high and quick: a trick Ross Bagdasarian built with his tape recorder."), "source": EN("Jon O'Brien, The Chipmunk Song facts, Recording Academy, GRAMMY.com (2023)"), "url": "https://www.grammy.com/news/the-chipmunk-song-christmas-dont-be-late-anniversary-legacy-facts"},
    "3-row": {"id": "barcarolle-stroke", "text": EN("A barcarolle, a boat song of Venice's gondoliers, is nearly always in 6/8: perhaps to suggest the boat's rise and fall, or the steady strokes of the oars. Offenbach's opera The Tales of Hoffmann (1881) has one, sung as a duet."), "source": EN("Grove, A Dictionary of Music and Musicians, vol. 1 (1904), Barcarole"), "url": "https://archive.org/details/dictionaryofmusi01grov_1"},
    "3-frere": {"id": "sumer-pes", "text": EN("Sumer Is Icumen In, an English round copied in the 13th century, has a part for two lower voices beneath it, marked \"pes\", Latin for \"foot\", repeated over and over under the tune."), "source": EN("Grove, A Dictionary of Music and Musicians, vol. 4 (1908), Sumer is icumen in"), "url": "https://archive.org/details/dictionaryofmusi04grov_1", "distinct": ["patter-pater-noster"]},
    "3-sailor": {"id": "up-she-rises-1841", "text": EN("Drunken Sailor's earliest known printing is in an 1841 whaling book, as just \"Ho! Ho! and up she rises... Early in the morning\". One man usually struck up the song; the rest joined in."), "source": EN("Olmsted, Incidents of a Whaling Voyage (1841), Internet Archive"), "url": "https://archive.org/details/incidentsofwhali00olmsrich"},
    "4-bass": {"id": "la-folia", "text": EN("La Folia, an old Spanish dance, gave Europe a favourite ground: a bass and chords to vary over and over. Corelli ended his 12 violin sonatas (Rome, 1700) with variations on it, and Vivaldi wrote a set too."), "source": EN("Grove, A Dictionary of Music and Musicians, vol. 2 (1906), Follia"), "url": "https://archive.org/details/dictionaryofmusi02grov_1"},
    "4-layers": {"id": "dido-ground", "text": EN("In Dido's Lament, from Purcell's opera Dido and Aeneas, the same short falling bass line repeats eleven times through the aria, and Dido sings her own line over it."), "source": EN("Purcell, Dido and Aeneas, ed. Edward J. Dent (Oxford, 1925), score, Internet Archive"), "url": "https://archive.org/details/31761058016775"},
}


def lesson(lid, title, steps, **extra):
    check(lid, steps)
    if "fact" not in extra and lid in FACTS:
        extra = {"fact": FACTS[lid], **extra}
    return {"id": f"ll-{lid}", "title": EN(title), **extra, "steps": steps}


# ---- The checks: the span, the seam, beat 0, and no unison over your own loop ----

def all_notes(value):
    """Every note anywhere in a step (exercise, listen, partner lines, clips, model)."""
    if isinstance(value, dict):
        if "beat" in value and "step" in value:
            yield value
        for v in value.values():
            yield from all_notes(v)
    elif isinstance(value, list):
        for v in value:
            yield from all_notes(v)


def pitches(n):
    return set(n.get("choices") or [n["step"]])


def check(lid, steps):
    for step in steps:
        for n in all_notes(step):
            for p in pitches(n):
                assert LOW <= p <= HIGH, f"ll-{lid}: step {p} is outside {LOW} to {HIGH}"
    for i, step in enumerate(steps):
        ex = step.get("exercise", {})
        if "under" not in ex:
            continue
        shared = ex["under"].get("loop")
        sung = ex["notes"]
        end = max(n["beat"] + n["length"] for n in sung)
        for d in ex.get("with", []):
            end = max(end, end + d.get("delay", 0))
        sounding = []
        for layer in ex["under"]["steps"]:
            idx, loop = (layer, shared) if isinstance(layer, int) else (layer["step"], layer.get("loop", shared))
            assert idx < i and loop, f"ll-{lid} step {i + 1}: a layer is an earlier step, looped"
            take = steps[idx]["exercise"]["notes"]
            assert min(n["beat"] for n in take) == 0, f"ll-{lid} step {idx + 1}: a layer starts singing on beat 0"
            first = [n for n in take if n["beat"] < loop]
            for n in first:
                assert n["beat"] + n["length"] <= loop - 0.5 + 1e-9, f"ll-{lid} step {idx + 1}: a layer stops half a beat before its loop of {loop} comes round"
            k = 0
            while k * loop < end:
                sounding += [(n["beat"] + k * loop, n["beat"] + n["length"] + k * loop, pitches(n)) for n in first]
                k += 1
        if step.get("_tune"):
            continue
        for n in sung:
            a, b = n["beat"], n["beat"] + n["length"]
            for x, y, ps in sounding:
                assert not (min(b, y) - max(a, x) > 1e-9 and ps & pitches(n)), f"ll-{lid} step {i + 1}: a unison with your own loop at beat {a}"


def strip(value):
    if isinstance(value, dict):
        return {k: strip(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [strip(v) for v in value]
    return value


# ---- The loops (units 1 and 2 at 80, do 0) ----

T12 = 80
TWO = 8  # the two-bar loop, in beats
FOUR = 16
TWO_BASS = line([(0, 1, "do"), (2, 1, "do"), (4, 1, "so,"), (6, 1, "so,")], "doom")
FOUR_BASS = line([(0, 1, "do"), (2, 1, "do"), (4, 1, "la,"), (6, 1, "la,"), (8, 1, "re"), (10, 1, "re"), (12, 1, "so,"), (14, 0.75, "so,")], "doom")
TWO_GAPS = line([(1, 0.5, "mi"), (3, 0.5, "mi"), (5, 0.5, "re"), (7, 0.5, "re")], "doo")
FOUR_GAPS = line([(1, 0.5, "mi"), (3, 0.5, "mi"), (5, 0.5, "mi"), (7, 0.5, "mi"), (9, 0.5, "fa"), (11, 0.5, "fa"), (13, 0.5, "re"), (15, 0.5, "re")], "doo")
TWO_PAD = line([(0, 3.5, "mi"), (4, 3.5, "re")], "oo")
FOUR_PAD = line([(0, 3.5, "mi"), (4, 3.5, "mi"), (8, 3.5, "fa"), (12, 3.5, "re")], "oo")


def doo_doos(names):
    """A rhythm part: "doo-doo" twice a bar, in the bass's gaps, on each bar's note."""
    return line([(4 * b + o, 0.5, name) for b, name in enumerate(names) for o in (1, 1.5, 3, 3.5)], "doo")


TWO_RHYTHM = doo_doos(["so", "so"])
FOUR_RHYTHM = doo_doos(["so", "so", "la", "so"])


def overdub(notes, loop, count, rest=None):
    """A top part: once round to listen (short loops), then `count` passes; `rest`: the pass index sat out."""
    start = loop if loop <= LISTEN_UP_TO else 0
    out = []
    for k in range(count):
        if k != rest:
            out += passes(notes, loop, 1, start + k * loop)
    return out


# ---- Unit 1: A loop that lines up ----

UNIT1 = {"id": "ll-a-loop", "title": EN("A loop that lines up"), "colour": COLOUR, "lessons": [
    lesson("1-loop", "The loop", [
        learn("A looper sings a short part, lets it repeat, and sings over it: a band made of one voice. Hear one: a bass four times round, and a second part over it.", [
            ("The app sets the loop's length", "Your job is to fit your notes inside it"),
            HEADPHONES,
            ("Low and easy", SAFETY),
        ], "bass", listen={"tempo": T12, "turn": False, "notes": passes(TWO_BASS, TWO, 4),
                           "with": [{"notes": passes(TWO_GAPS, TWO, 2, 2 * TWO)}]}),
        bass(f"Sing the bass on \"doom\", twice round: do, do, then low so, low so, a rest after each. Do is your home note, and low so sits below it. {BASS_SAFETY}",
             passes(TWO_BASS, TWO, 2), T12, measures=f"{PITCH_BEAT} {RESING}", generous=True),
        play(f"Now your bass loops: listen once round, then fill its gaps with short \"doo\"s, on mi, then re, both just above do.",
             overdub(TWO_GAPS, TWO, 2), T12, "Scored on your notes in the gaps, on pitch and on the beat. That's your loop under you.",
             under=under(1, loop=TWO), generous=True, rhythm=True),
    ]),
    lesson("1-lock", "Lock to yourself", [
        learn("A looper's first test: drop out, keep the loop in your head, and come back in on time.", [
            ("Sing, rest, sing", "Fill the gaps once round, listen a round, then back in"),
            ("Back in on time", "Your loop is the band: be where it expects you"),
            HEADPHONES,
        ], "bass"),
        bass(f"The bass once round: do, do, low so, low so. {BASS_SAFETY}", passes(TWO_BASS, TWO, 1), T12),
        play(f"Listen once round, fill the gaps once round, rest a round, then come back in.",
             overdub(TWO_GAPS, TWO, 3, rest=1), T12, ENTRY, under=under(1, loop=TWO), score="entry"),
    ]),
    lesson("1-longer", "A longer loop", [
        learn("Four bars now, four notes: do, low la, re, low so. A loop that moves through four chords.", [
            ("The last note stops early", "That's your breath, and the loop's seam"),
            ("Each note twice", "Then a rest"),
            HEADPHONES,
        ], "bass"),
        wait_for_me("Find each note of the four-bar bass: each waits until you're on it.", passes(FOUR_BASS, FOUR, 1), T12),
        choose("Hear each loop come round, then choose.", T12, [
            ("Which loop closes cleanly?", [line([(0, 1, "so,"), (2, 0.75, "so,"), (4, 1, "do"), (6, 1, "do")]),
                                            line([(0, 1, "so,"), (2, 2, "so,"), (4, 1, "do"), (6, 1, "do")])],
             0, "The first stops early, so there's a breath before the loop comes round. The second runs right into it."),
            ("Which loop closes cleanly?", [line([(0, 1, "so,"), (2, 0.75, "so,"), (4.3, 0.7, "do"), (6, 1, "do")]),
                                            line([(0, 1, "so,"), (2, 0.75, "so,"), (4, 1, "do"), (6, 1, "do")])],
             1, "In the first, the note after the seam comes in late, and the loop stumbles."),
            ("Which loop closes cleanly?", [line([(0, 1, "so,"), (2, 2, "so,"), (4, 1, "do"), (6, 1, "do")]),
                                            line([(0, 1, "so,"), (2, 0.75, "so,"), (4, 1, "do"), (6, 1, "do")])],
             1, "The second leaves a gap at the seam. The first holds on into the next round."),
        ]),
        bass(f"The four-bar bass, twice round. Stop the last note early, before the loop comes round. {BASS_SAFETY}",
             passes(FOUR_BASS, FOUR, 2), T12, measures=RELEASE, score="release"),
    ]),
    lesson("1-first", "Your first loop", [
        learn("Your first loop, kept for the end of the course: the four-bar bass once, then the gap part over it, with a rest in the middle.", [
            ("Kept for later", "The course's last lesson plays it beside your new bass"),
            ("Sing, rest, back in", "After one round of listening"),
            HEADPHONES,
        ], "bass"),
        bass(f"The four-bar bass, once round. {BASS_SAFETY}", passes(FOUR_BASS, FOUR, 1), T12, keep=KEEP),
        play(f"Listen once round, fill the gaps once round, rest a round, then come back in: mi, then fa, then re.",
             overdub(FOUR_GAPS, FOUR, 3, rest=1), T12, ENTRY, under=under(1, loop=FOUR), score="entry"),
    ], challenge=True),
]}

# ---- Unit 2: Stacking parts ----

MIX_GOOD = TWO_BASS + TWO_PAD + TWO_RHYTHM
MIX_PAD_ON_TOP = TWO_BASS + line([(0, 3.5, "so"), (4, 3.5, "so")]) + TWO_RHYTHM
MIX_ON_THE_BASS = TWO_BASS + line([(b + o, 0.5, "so") for b in (0, 4) for o in (0, 0.5, 2, 2.5)])

UNIT2 = {"id": "ll-stacking", "title": EN("Stacking parts"), "colour": COLOUR, "lessons": [
    lesson("2-pad", "The pad", [
        learn("A pad is a soft held note over the bass: the chord's middle. Over your loop, \"oo\" on mi, then re.", [
            ("Softer than the bass", "A pad is felt more than heard"),
            ("Each layer its own sound", "Bass on \"doom\", pad on \"oo\", so you can hear them all"),
            HEADPHONES,
        ], "harmony"),
        bass(f"The floor first, every time: the bass once round. {BASS_SAFETY}", passes(TWO_BASS, TWO, 1), T12),
        play(f"Listen once round, then a soft \"oo\" over your loop: mi for a bar, then re, each stopped half a beat early.",
             overdub(TWO_PAD, TWO, 2), T12, PITCH, under=under(1, loop=TWO)),
    ]),
    lesson("2-rhythm", "A rhythm part", [
        learn("A rhythm part is short and bright: \"doo-doo\" on so, in the bass's gaps.", [
            ("In the gaps", "Two quick doos after each bass note"),
            ("Bright and short", "Like a drum, not a tune"),
            HEADPHONES,
        ], "harmony"),
        choose("Listen to each, then choose.", T12, [
            ("Which mix lets the doo-doos through?", [MIX_GOOD, MIX_PAD_ON_TOP], 0,
             "In the second, the pad holds the doo-doos' own note, and they vanish into it."),
            ("Which rhythm part leaves room for the bass?", [MIX_ON_THE_BASS, TWO_BASS + TWO_RHYTHM], 1,
             "The second sits in the bass's gaps. The first lands on the bass's notes and covers them."),
            ("Which mix lets the doo-doos through?", [MIX_PAD_ON_TOP, MIX_GOOD], 1,
             "In the second, the pad sits lower, on other notes, so the doo-doos stand out."),
        ]),
        bass(f"The bass once round. {BASS_SAFETY}", passes(TWO_BASS, TWO, 1), T12),
        play(f"Listen once round, then \"doo-doo\" on so in the gaps, twice round.",
             overdub(TWO_RHYTHM, TWO, 2), T12, PITCH_BEAT, under=under(2, loop=TWO), rhythm=True),
    ]),
    lesson("2-three", "Three layers", [
        learn("Now the four-bar loop, three layers deep: the bass, a pad over it, then a rhythm part over both.", [
            ("Once round each", "The pad starts with your bass, on its first beat"),
            ("Never push", "Never sing louder to hear yourself: lower your headphones instead"),
            HEADPHONES,
        ], "harmony"),
        bass(f"The four-bar bass, once round. {BASS_SAFETY}", passes(FOUR_BASS, FOUR, 1), T12),
        play(f"The pad, from your loop's first beat, once round: mi, mi, fa, re, each held soft on \"oo\".",
             passes(FOUR_PAD, FOUR, 1), T12, PITCH, under=under(1, loop=FOUR)),
        play(f"Listen once round to your two layers, then \"doo-doo\" in the gaps: on so, so, la, so.",
             overdub(FOUR_RHYTHM, FOUR, 1), T12, PITCH_BEAT, under=under(1, 2, loop=FOUR), rhythm=True),
        {"kind": "selfcheck", "text": EN("The top part once more on its own, then hear yours beside the guide's."),
         "exercise": {"tempo": T12, "model": {"notes": passes(FOUR_RHYTHM, FOUR, 1)},
                      "questions": [EN("In your last take, could you hear all three layers?"), EN("Did you push to hear yourself?")]}},
    ]),
    lesson("2-band", "The band", [
        learn("The band: all three layers on the four-bar loop, nothing lit while you sing. From memory, as a looper on stage.", [
            ("Nothing lit", "Your notes show after each take, not during it"),
            ("Once round each", "Then the top part twice"),
            HEADPHONES,
        ], "harmony"),
        bass(f"The bass, once round, from memory. {BASS_SAFETY}", passes(FOUR_BASS, FOUR, 1), T12, lights="off"),
        play(f"The pad from the first beat, once round, from memory.",
             passes(FOUR_PAD, FOUR, 1), T12, PITCH, under=under(1, loop=FOUR), lights="off"),
        play(f"Listen once round, then the rhythm part twice round, from memory.",
             overdub(FOUR_RHYTHM, FOUR, 2), T12, "Scored on the top part on pitch and on the beat, from memory, over your band.",
             under=under(1, 2, loop=FOUR), lights="off", rhythm=True),
    ], challenge=True),
]}

# ---- Unit 3: A tune on top ----

def template_tune(path, beats, do):
    """A free or library song's tune (the first part), its first `beats`, in steps from the singer's note."""
    tune = json.loads(path.read_text())["parts"][0]["guide"]["notes"]
    return [note(n["beat"], n["length"], n["pitch"] - do, n["lyric"]) for n in tune if n["beat"] < beats]


ROW_HOME = -5  # Row's do: the singer's low so, so the tune tops out at +7
ROW_T, ROW_BAR, ROW_LOOP = 60, 2, 4  # 6/8 in dotted-quarter beats, two a bar; a two-bar loop
ROW_BASS = line([(0, 0.67, "do"), (1, 0.67, "do"), (2, 0.67, "do")], "doom", home=ROW_HOME)
ROW_TUNE = template_tune(ROW, 16, 60 - ROW_HOME)

FRERE_T, FRERE_LOOP = 96, 4
FRERE_BASS = line([(0, 1, "do", "ding"), (1, 1, "so,", "dang"), (2, 1.5, "do", "dong")])
FRERE_PAD = line([(0, 3.5, "so")], "oo")
FRERE_TUNE = template_tune(FRERE, 32, 63)  # in Eb (63) as written: do at 0

SAILOR_T, SAILOR_LOOP = 88, 32  # low la (-3) as home; one chord a bar, so eight bars
SAILOR_ROOTS = ["la,", "la,", "so,", "so,", "la,", "la,", "so,", "la,"]
SAILOR_BASS = line([(4 * b + o, 1, r) for b, r in enumerate(SAILOR_ROOTS) for o in (0, 2)], "doom")


def sailor_line(start, notes, words):
    """One line of the verse: Folk's rhythm (folk-1-crew), its steps moved up 4 to sit on low la. The tune is Terry,
    The Shanty Book Part I (1921) No. 14, checked against Whall (1913) p. 107; "lor?" stops early for a breath (the
    print gives it a full beat)."""
    rhythm = [1, 0.5, 0.5, 1, 0.5, 0.5, 1, 1, 1, 0.25] if len(notes) == 10 else [1, 1, 1, 1, 2, 2]
    out, beat = [], start
    for length, name, word in zip(rhythm, notes, words):
        out.append(note(beat, length, sf(name), word))
        beat += 1 if length == 0.25 else length
    assert beat == start + 8, beat
    return out


VERSE = "What shall we do with a drunk- en sai- lor?".split()
SAILOR_TUNE = (sailor_line(0, ["mi"] * 7 + ["la,", "do", "mi"], VERSE)
               + sailor_line(8, ["re"] * 7 + ["so,", "ti,", "re"], VERSE)
               + sailor_line(16, ["mi"] * 7 + ["fi", "so", "la"], VERSE)
               + sailor_line(24, ["so", "mi", "re", "ti,", "la,", "la,"], "Ear- ly in the morn- ing.".split()))

UNIT3 = {"id": "ll-tune-on-top", "title": EN("A tune on top"), "colour": COLOUR, "lessons": [
    lesson("3-row", "Row, Row, Row Your Boat", [
        learn("Row, Row, Row Your Boat sits on one chord all the way, so its loop is one note. The song sits low here: home is your low so.", [
            ("One chord, one note", "The simplest loop there is"),
            ("Two beats a bar", "A rocking beat, like oars"),
            HEADPHONES,
        ], "round"),
        bass(f"The bass on \"doom\": three short notes and a rest, twice round. It's at the bottom of your voice. {BASS_SAFETY}",
             passes(ROW_BASS, ROW_LOOP, 2, bar=ROW_BAR), ROW_T, home=ROW_HOME),
        play(f"Listen once round, then sing the tune over your loop.",
             passes(ROW_TUNE, 16, 1, ROW_LOOP, bar=ROW_BAR), ROW_T, "Scored on the tune's notes on pitch.",
             tune=True, under=under(1, loop=ROW_LOOP)),
    ]),
    lesson("3-frere", "Are You Sleeping (Frère Jacques)", [
        learn("The round's last line, \"ding, dang, dong\", is its own bass: looped, it fits under every bar of the tune.", [
            ("The round's last line", "Is its own bass"),
            ("A pad on so", "Held soft over every bar"),
            HEADPHONES,
        ], "round"),
        bass(f"\"Ding, dang, dong\": do, low so, do, twice round. {BASS_SAFETY}", passes(FRERE_BASS, FRERE_LOOP, 2), FRERE_T),
        play(f"The pad from your loop's first beat: a soft \"oo\" on so, held each bar, twice round.",
             passes(FRERE_PAD, FRERE_LOOP, 2), FRERE_T, PITCH, under=under(1, loop=FRERE_LOOP)),
        play(f"Listen once round, then the tune over your bass and pad.",
             passes(FRERE_TUNE, 32, 1, FRERE_LOOP), FRERE_T, "Scored on the tune's notes on pitch.",
             tune=True, under=under(1, 2, loop=FRERE_LOOP)),
    ]),
    lesson("3-sailor", "Drunken Sailor", [
        learn("Drunken Sailor moves between two chords, one a bar, so its loop is eight bars: a whole verse.", [
            ("Home is low la", "A minor song, so home is la, not do"),
            ("One note a bar", "Low la or low so, on beats 1 and 3"),
            HEADPHONES,
        ], "round"),
        wait_for_me("The bass's eight notes, one a bar: each waits until you're on it.",
                    line([(1 + k, 1, r) for k, r in enumerate(SAILOR_ROOTS)], "doom"), SAILOR_T),
        bass(f"The bass on \"doom\", eight bars once round: low la, low la, low so, low so, low la, low la, low so, low la. {BASS_SAFETY}",
             passes(SAILOR_BASS, SAILOR_LOOP, 1), SAILOR_T, home=-3),
        play(f"Now the tune over your loop. It starts with your bass, on its first beat.",
             passes(SAILOR_TUNE, SAILOR_LOOP, 1), SAILOR_T, "Scored on the tune's notes on pitch.",
             tune=True, under=under(2, loop=SAILOR_LOOP)),
    ]),
    lesson("3-round", "A round with yourself", [
        learn("A round with yourself: \"ding, dang, dong\", the tune over it, then the tune again two bars late, over your first. The guide comes in as a third voice.", [
            ("Your first entry", "The tune over your bass, from its first beat"),
            ("Your second entry", "Two bars late, over your bass and your first"),
            HEADPHONES,
        ], "round"),
        bass(f"\"Ding, dang, dong\", twice round. {BASS_SAFETY}", passes(FRERE_BASS, FRERE_LOOP, 2), FRERE_T),
        play(f"Your first entry: the tune over your bass, from its first beat.",
             passes(FRERE_TUNE, 32, 1), FRERE_T, "Scored on the tune's notes on pitch.",
             tune=True, under=under(1, loop=FRERE_LOOP)),
        play(f"Your second entry, two bars late, over your bass and your first entry. Then the guide comes in, two bars after you.",
             passes(FRERE_TUNE, 32, 1, 8), FRERE_T, "Scored on your second entry on pitch, over your bass and your first.",
             tune=True, under=under((1, FRERE_LOOP), (2, 32)), **{"with": [{"delay": 8}]}),
    ], challenge=True),
]}

# ---- Unit 4: Your own loop (Drunken Sailor; every lit pair fits its bar's chord) ----

PICKS = {"la,": ["la,", "do"], "so,": ["so,", "ti,"]}  # the bass: the root, or the chord's third
PAD_PICKS = {"la,": ["mi", "la"], "so,": ["re", "so"]}  # the pad: never a note of either bass pick
OWN_BASS = line([(4 * b + o, 1, PICKS[r]) for b, r in enumerate(SAILOR_ROOTS) for o in (0, 2)], "doom")
OWN_PAD = line([(4 * b, 3.5, PAD_PICKS[r]) for b, r in enumerate(SAILOR_ROOTS)], "oo")
TUNE_WITH = [{"notes": SAILOR_TUNE}]

UNIT4 = {"id": "ll-your-own", "title": EN("Your own loop"), "colour": COLOUR, "lessons": [
    lesson("4-bass", "Choose your bass", [
        learn("Your own bass for Drunken Sailor: in every bar two notes light, and either one fits. Pick as you go.", [
            ("Two notes a bar", "Low la or do in la's bars, low so or low ti in so's"),
            ("Every pick works", "Each is a note of that bar's chord"),
            HEADPHONES,
        ], "harmony"),
        {"kind": "try", "text": EN("Once with the guide singing the lower note of each pair, to learn the bars. Just try it."),
         "exercise": {"tempo": SAILOR_T, "turn": False, "notes": passes(OWN_BASS, SAILOR_LOOP, 1), "with": TUNE_WITH}},
        bass(f"Now your bass under the guide's tune: in each bar, sing either lit note. {BASS_SAFETY}",
             passes(OWN_BASS, SAILOR_LOOP, 1), SAILOR_T, home=-3, measures=LIT_BEAT,
             **{"with": TUNE_WITH}),
    ]),
    lesson("4-layers", "Choose your layers", [
        learn("Your bass again, then your own pad over it: two notes light in every bar, and neither meets your bass.", [
            ("Your bass", "Picked as before, once round"),
            ("Your pad", "Mi or la in la's bars, re or so in so's"),
            HEADPHONES,
        ], "harmony"),
        bass(f"Your bass, once round: either lit note in each bar. {BASS_SAFETY}", passes(OWN_BASS, SAILOR_LOOP, 1), SAILOR_T, home=-3,
             measures=LIT_BEAT),
        play(f"Your pad, from your loop's first beat: a soft \"oo\", either lit note, held each bar.",
             passes(OWN_PAD, SAILOR_LOOP, 1), SAILOR_T, "Scored on landing either lit note, on pitch.",
             under=under(1, loop=SAILOR_LOOP)),
    ]),
    lesson("4-song", "Your song", [
        learn("Your song: your bass, your pad, then Drunken Sailor's tune over them, kept as a song in Sing.", [
            ("Three layers, all yours", "Bass, then pad, then the tune"),
            ("Then and now", "Your first loop beside your new bass"),
            HEADPHONES,
        ], "harmony"),
        bass(f"Your bass, once round. {BASS_SAFETY}", passes(OWN_BASS, SAILOR_LOOP, 1), SAILOR_T, home=-3,
             measures=LIT_BEAT, thenAndNow=KEEP),
        play(f"Your pad from the first beat, once round.",
             passes(OWN_PAD, SAILOR_LOOP, 1), SAILOR_T, "Scored on landing either lit note, on pitch.",
             under=under(1, loop=SAILOR_LOOP)),
        play(f"The tune on top, from the first beat: your band of you.",
             passes(SAILOR_TUNE, SAILOR_LOOP, 1), SAILOR_T, "Scored on the tune's notes on pitch, over your bass and pad.",
             tune=True, under=under(1, 2, loop=SAILOR_LOOP)),
    ], challenge=True, keepSong={"title": EN("My loop song"), "takes": [
        {"step": 1, "name": EN("Bass")}, {"step": 2, "name": EN("Pad")}, {"step": 3, "name": EN("Tune")}]}),
]}

course = {
    "id": "live-looping",
    "version": 1,
    "headphones": "needed",  # what plays under you rests through a speaker (steps.json courseHeadphones)
    "reviewed": False,
    "title": EN("Live looping"),
    "units": [UNIT1, UNIT2, UNIT3, UNIT4],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(strip(course), open(OUT, "w"), ensure_ascii=False)
