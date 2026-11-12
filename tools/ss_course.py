"""Sight-singing: writes course/plus/sight-singing/course.json. Rebuilt from the courses lead's build spec
(after a teacher's and a game designer's review): three lines a lesson, names on, then faint, then off;
a warm read before each challenge's cold line; Further from do (la, ti, the half steps, la as home);
and a Then and now from the first cold read to the finale. Every reading line is written in sol-fa.

    python3 -I tools/ss_course.py && python3 -I tools/coursefmt.py course/plus/sight-singing/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/sight-singing/course.json"

# The units' order. Further from do comes before Your part in a chord, so the songs' la and ti below do
# are taught before they're read. To keep the old order, swap the last two.
UNIT_ORDER = ["ss-find-do", "ss-leaps", "ss-reading-time", "ss-further", "ss-part-in-chord"]

BANNED = re.compile(r"\bstars?\b|—", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)
SOLFA = {"do": 0, "re": 2, "mi": 4, "fa": 5, "so": 7, "la": 9, "ti": 11}
BAR = {"4/4": 4, "3/4": 3}
PITCH = "Scored on each note's pitch."
TIMED = "Scored on each note's pitch, and when it starts."
COLD = "Hear it first is there if you need it; the top score is for reading it cold."
KEEP = "sight-singing.first-cold"  # the first cold read, kept for Then and now at the finale
LA = -3  # the drone in the minor lessons: la below do


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def W(text):
    """A fact's words: facts are about notation in general and may name letters."""
    return {"en": text}


def number(text):
    return float(text) if "." in text else int(text)


def sf(line, time="4/4", hold=False, bars=True):
    """Notes from sol-fa: `do re mi`, `so,` below do, `/2` two beats (one by default), `(rest)` a beat's
    silence, `|` a bar line (checked to fall on one). `hold`: the last note is held to its bar line. A line
    read in time (`bars`) must end on a bar line; a line read on pitch alone (units 1 and 2, and Further from
    do's lessons) keeps every note a crotchet and may end mid-bar, as the course's lines always have, so the
    stave shows no note value before Reading time teaches it (the courses lead, 2026-11-08)."""
    notes, beat, bar = [], 0, BAR[time]
    for token in line.split():
        if token == "|":
            assert beat % bar == 0, f"{line}: a bar line at beat {beat}"
            continue
        name, _, length = token.partition("/")
        length = number(length) if length else 1
        if name != "(rest)":
            below = name.endswith(",")
            notes.append({"beat": beat, "length": length, "step": SOLFA[name.rstrip(",")] - (12 if below else 0)})
        beat += length
    if hold and beat % bar:
        notes[-1]["length"] += bar - beat % bar
        beat += bar - beat % bar
    assert beat % bar == 0 or not bars, f"{line}: a {time} line fills whole bars, this one ends at beat {beat}"
    return notes


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards):
    assert len(cards) <= 3, headline
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "reviewed": False}


def staff(names, time=None):
    s = {"names": names, "look": 4}
    if time:
        s.update({"count": BAR[time], "time": time, "rhythm": True})
    return s


def drone(step=0):
    return {"step": step, "fadeAfter": 4}


def watch(text, line, tempo):
    """Watch it play on the stave, then sing it back."""
    return {"kind": "play", "text": EN(text), "exercise": {
        "tempo": tempo, "turn": True, "notes": sf(line, bars=False), "staff": staff("on"), "drone": drone()}}


def read(text, line, names, tempo, *, time=None, home=0, **extra):
    """A line read from the stave over the fading drone (on do, or la in the minor lessons), cold (no
    guide), Hear it first offered. With a time it's read in time, else on pitch alone."""
    ex = {"tempo": tempo, "turn": False, "guide": False, "notes": sf(line, time or "4/4", bars=bool(time)), "staff": staff(names, time),
          "droneAfter": 0, "drone": drone(home), "hearFirst": True, "score": "read", **extra}
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(TIMED if time else PITCH)}


def read_song(text, template, part, phrases, time, *, names="off", others=False):
    song = {"template": template, "part": part, "phrases": phrases}
    if others:
        song["with"] = "others"
    return {"kind": "play", "text": EN(text), "exercise": {
        "song": song, "tempo": 72, "turn": False, "guide": False, "staff": staff(names, time),
        "droneAfter": 0, "drone": drone(), "hearFirst": True, "score": "read"},  # do sounds through the look and the count-in, as read() does
        "measures": EN(TIMED)}


def name_it(text, echoes, measures):
    """Hear a note or two, then sing the note named: [(call, sing, label)]."""
    return {"kind": "bullseye", "text": EN(text), "exercise": {
        "tempo": 72, "think": 1, "echoes": [{"call": call, "sing": sing, "label": EN(label)} for call, sing, label in echoes], "named": True},
        "measures": EN(measures)}


def wait_for_me(text, line, tempo):
    """Off the stave: each note plays and waits until it's found (unscored)."""
    names = [n.rstrip(",") for n in line.split()]
    notes = [{**n, "beat": n["beat"] + 1, "lyric": name} for n, name in zip(sf(line, bars=False), names)]  # from beat 1, as the lane's tries are
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes, "drone": {"step": 0}}}


def lesson(lid, title, steps, **extra):
    """A lesson; its "Did you know?" comes from FACTS by its id (the explicit fact(lid) calls give the same)."""
    if "fact" not in extra and lid in FACTS:
        extra = {"fact": FACTS[lid], **extra}
    return {"id": lid, "title": EN(title), **extra, "steps": steps}


def unit_number(uid):
    return UNIT_ORDER.index(uid) + 1


FACTS = {
    # Each lesson page's "Did you know?" (2026-11-08): read in its source, then checked again.
    "ss-1-do": {"id": "guido-lines-a-third-apart", "text": W("In the 1000s Guido of Arezzo set staff lines a third apart, so lines and spaces each hold a note, and coloured two lines red and yellow. Chant books still use his four lines."), "source": W("Encyclopedia.com, Guido of Arezzo (New Catholic Encyclopedia)"), "url": "https://www.encyclopedia.com/religion/encyclopedias-almanacs-transcripts-and-maps/guido-arezzo"},
    "ss-1-up": {"id": "neumes-showed-only-rise-and-fall", "text": W("Early Western chant notation, from the 800s, had no staff. Its marks showed a tune's general rise and fall, not its exact notes, probably as reminders of melodies singers had already learned by ear."), "source": W("Hanning, Concise History of Western Music, Norton, chapter 2"), "url": "https://nerd.wwnorton.com/ebooks/epub/concisehwm5anth/EPUB/content/1.2.2-chapter02.xhtml"},
    "ss-2-chord": {"id": "taps-home-chord", "text": W("Taps, the US Army's lights-out call, was worked out in July 1862 by a Union general and his bugler. A bugle plays only its harmonic series, so Taps uses just one major chord: so, do and mi."), "source": W("Oliver W. Norton, Army Letters, 1861-1865 (1903)"), "url": "https://archive.org/details/armyletters1861100nort"},
    "ss-2-below": {"id": "ledger-lines-printers-disliked", "text": W("Ledger lines came late in notation and at first looked awkward, so old music avoided them where it could. Vocal music used many different clefs instead, to keep each part on the stave."), "source": W("C. F. Abdy Williams, The Story of Notation (1903)"), "url": "https://archive.org/details/storyofnotation00willuoft"},
    "ss-3-long": {"id": "minim-was-the-smallest", "text": W("The minim's Latin name, minima, means \"smallest\": it was once the shortest note value. And the breve, now worth two semibreves, was named from the Latin for \"short\", the root of \"brief\"."), "source": W("C. F. Abdy Williams, The Story of Notation (1903)"), "url": "https://archive.org/details/storyofnotation00willuoft"},
    "ss-3-quick": {"id": "beams-meant-one-syllable", "text": W("Vocal scores traditionally beamed quavers only when they shared one syllable, so each new syllable got its own flag. Today it's more common to beam by the beat and show shared syllables with slurs."), "source": W("Music Publishers' Association, Standard Music Notation Practice (1993)"), "url": "https://web.archive.org/web/20080407014159/http://www.mpa.org/music_notation/standard_practice.pdf"},
    "ss-5-la": {"id": "four-syllables-king-lear", "text": W("In the 1600s, English singers named notes with just four syllables, mi, fa, sol and la, singing fa, sol, la twice to fill a scale. In King Lear's 1623 Folio, Edmund adds \"Fa, sol, la, me.\""), "source": W("John Playford, An Introduction to the Skill of Musick (1694 edition)"), "url": "https://archive.org/details/introductiontosk00play"},
    "ss-5-half": {"id": "kodaly-half-steps-later", "text": W("Kodály teachers start children on the five pentatonic notes, do, re, mi, so and la, which hold no half steps. Fa and ti, the notes that make the half steps, come later."), "source": W("Organization of American Kodály Educators, \"The Kodály Concept\""), "url": "https://www.oake.org/the-kodaly-concept/"},
    "ss-5-minor": {"id": "shape-notes-minor-on-la", "text": W("In shape-note singing each syllable has its own note-head shape, and a minor key's first note is always la, as yours is now. Little and Smith printed the shapes in 1801."), "source": W("Sacred Harp Musical Heritage Association (fasola.org), shape-note timeline"), "url": "https://fasola.org/introduction/timeline.html"},
    "ss-4-alto": {"id": "choirbook-each-part-its-own-patch", "text": W("A Renaissance choir could sing four parts from one book. In the Vatican's Chigi Codex, a Kyrie puts two parts on the left page and two on the right, each in its own patch."), "source": W("Vatican Library, Chigi Codex (Chig. C.VIII.234), ff. 19v-20r"), "url": "https://digi.vatlib.it/view/MSS_Chig.C.VIII.234"},
    "ss-1-challenge": {"id": "treble-clef-g", "text": W("The treble clef is a fancy letter G. Its curl wraps around the line where G sits, which is why it's also called the G clef."), "source": W("Concise Oxford Dictionary of Music, \"clef\" (Encyclopedia.com)"), "url": "https://www.encyclopedia.com/arts/dictionaries-thesauruses-pictures-and-press-releases/clef"},
    "ss-2-challenge": {"id": "bass-clef-f", "text": W("The bass clef is a fancy letter F. Its two dots sit either side of the line where F sits, which is why it's also called the F clef."), "source": W("Concise Oxford Dictionary of Music, \"clef\" (Encyclopedia.com)"), "url": "https://www.encyclopedia.com/arts/dictionaries-thesauruses-pictures-and-press-releases/clef"},
    "ss-3-challenge": {"id": "maelzel-metronome-1815", "text": W("A tempo mark like \"M.M. = 72\" stands for Maelzel's Metronome. Johann Maelzel began making his metronome in Paris in 1816, and composers such as Beethoven wrote their speeds in its beats."), "source": W("Concise Oxford Dictionary of Music, \"metronome\" (Encyclopedia.com)"), "url": "https://www.encyclopedia.com/arts/dictionaries-thesauruses-pictures-and-press-releases/metronome"},
    "ss-4-signature": {"id": "order-of-sharps", "text": W("Sharps in a key signature always come in the same order, F, C, G, D, A, E, B, and flats in the reverse order. Each new key a fifth higher adds the next sharp."), "source": W("Open Music Theory, \"Key signatures\""), "url": "https://openmusictheory.github.io/keySignatures.html"},
    "ss-4-challenge": {"id": "flat-sharp-from-b", "text": W("The flat, sharp and natural signs all grew from the letter b: the flat from a round b, the sharp and natural from a square one."), "source": W("Frederick Niecks, \"The Flat, Sharp, and Natural\", Proceedings of the Musical Association (1890)"), "url": "https://archive.org/details/bub_gb_RdYPAAAAYAAJ"},
}


def fact(lid):
    return {"fact": FACTS[lid]} if lid in FACTS else {}


FIRST_COLD = "do re mi re | mi fa so fa | mi re do"  # ss-1-challenge's line, read again at the finale

UNITS = {}

UNITS["ss-find-do"] = {"id": "ss-find-do", "title": EN("Find do on the stave"), "lessons": [
    lesson("ss-1-do", "Do on the stave", [
        learn("A stave is five lines. Every line and every space is one note, and higher on the stave is higher in pitch. Your do sits where your own note is.", [
            ("Do is home", "Every line here starts on it"),
            ("The signs at the start", f"The clef, set for your voice, and the key's sharps or flats: more on them in unit {unit_number('ss-part-in-chord')}"),
            ("Easy voice", "Medium volume; stop if anything tightens or hurts"),
        ]),
        watch("Watch the stave while it plays, then sing it back: do, re, mi, re, do.", "do re mi re do", 60),
        read("Your turn to read. Look first, then sing it as the notes light: the names are under them.", "do re do re mi re do", "on", 60, generous=True),
        read("Names faint now: read the stave. The same line or space twice is the same note again.", "do re mi mi re re do", "faint", 60, generous=True),
    ]),
    lesson("ss-1-up", "Steps up and down", [
        learn("A step goes from a line to the next space, or a space to the next line. Up the stave is up in pitch.", [
            ("Count the steps", "Line, space, line: three notes in a row"),
            ("Up to so", "Do, re, mi, fa, so"),
            ("Then back", "The same steps, down"),
        ]),
        read("Read up to so, names under the notes.", "do re mi fa so", "on", 60),
        read("Now back down. The names are faint: read the stave first.", "so fa mi re do", "faint", 60),
        read("The whole climb, up to so and back down, with no names.", "do re mi fa so fa mi re do", "off", 60),
    ]),
    lesson("ss-1-turns", "Lines that turn", [
        learn("Real tunes turn: up a little, back, then on. Follow the notes, not a pattern.", [
            ("Not starting on do?", "Hear do, then step up to the first note in your head"),
            ("Find the turns", "Where it changes direction"),
            ("Then sing", "Steady; a slip? Go on to the next note"),
        ]),
        read("A line that turns, names faint.", "do re mi re mi fa mi re do", "faint", 66),
        read("Another, with no names at all.", "mi re do re mi fa mi re do", "off", 66),
        read("This one starts on so: hear do, step up to so in your head, then read. No names.", "so fa mi fa so fa mi re do", "off", 66),
    ]),
    lesson("ss-1-challenge", "A line, read cold", [
        learn(f"Three bars you haven't heard. Look, find do, then read them straight through. {COLD}", [
            ("Find do first", "Where your note sits"),
            ("Look for the top", "The highest note"),
            ("Read it cold", "No names, no help"),
        ]),
        read("First its last two bars, to warm up: names faint.", "mi fa so fa mi re do", "faint", 66),
        read("Now the whole line, cold: no names.", FIRST_COLD, "off", 66, keep=KEEP),
    ], challenge=True, **fact("ss-1-challenge")),
]}

UNITS["ss-leaps"] = {"id": "ss-leaps", "title": EN("Leaps you can see"), "lessons": [
    lesson("ss-2-chord", "Do, mi, so", [
        learn("Do, mi and so are the notes of your home chord. On the stave each sits two steps above the last: line to line, or space to space.", [
            ("A skip", "Jumps over one line or space"),
            ("Do, mi, so", "Each a skip apart"),
            ("Hear it in your head", "Before you sing it"),
        ]),
        watch("Watch the skips while they play, then sing them back.", "do mi so mi do", 72),
        name_it("Hear do, then sing the note named. Hear it in your head first.", [
            ([0], [7], "Sing so"),
            ([0], [4], "Sing mi"),
            ([0, 7], [4], "Sing mi"),
        ], "Scored on singing each note named, close to its middle."),
        read("Read the skips, names under the notes.", "do mi so mi | do so mi do", "on", 72),
        read("More skips through the chord, names faint.", "do so mi do mi so do", "faint", 72),
    ]),
    lesson("ss-2-below", "So below do", [
        learn("Many tunes start below do, on the so beneath it, and leap up home. On the stave it's a skip and a step lower.", [
            ("So below", "A fourth under do"),
            ("Leap up home", "So to do, like a call"),
            ("Below the stave", "A short extra line counts like the stave's own"),
        ]),
        read("So below do, then up by step and home: names under the notes.", "so, do re mi re do", "on", 72),
        read("So below do, then home: names faint.", "so, do so, do mi do", "faint", 72),
        read("Down to so, up through the chord, no names.", "do so, do mi so mi do", "off", 72),
    ]),
    lesson("ss-2-mixed", "Steps and skips", [
        learn("Now lines mix steps and skips. A step goes to the very next line or space; a skip jumps one.", [
            ("Spot the skips", "Before you start"),
            ("Steps fill in", "Between them"),
            ("Keep the beat", "Even when it leaps"),
        ]),
        read("Steps and skips, names faint.", "do mi re fa mi so fa mi re do", "faint", 72),
        read("And again, no names.", "so mi fa re mi do re do", "off", 72),
        read("From so below do this time, steps and skips, no names.", "so, do mi re fa mi re do", "off", 72),
    ]),
    lesson("ss-2-challenge", "Leaps, read cold", [
        learn(f"Three bars you haven't heard, with leaps you can see: so below do, and skips through the home chord. {COLD}", [
            ("Find do", "Then the so below it"),
            ("Spot the skips", "Line to line, or space to space"),
            ("Read it cold", "No names, no help"),
        ]),
        read("First the leaps to warm up: names faint.", "do mi so mi | do so, do", "faint", 80),
        read("Now the whole line, cold: no names.", "so, do mi re | do mi so fa | mi re do", "off", 80),
    ], challenge=True, **fact("ss-2-challenge")),
]}

UNITS["ss-reading-time"] = {"id": "ss-reading-time", "title": EN("Reading time"), "lessons": [
    lesson("ss-3-long", "Long and short", [
        learn("Now the notes' shapes tell you how long. A filled note with a stem is one beat; a hollow one with a stem is two. A rest is silence that still counts: this one, a beat.", [
            ("Crotchet", "Filled, with a stem: one beat"),
            ("Minim", "Hollow, with a stem: two beats"),
            ("Semibreve", "Hollow, no stem: four beats"),
        ]),
        read("Count in with the clicks, then read it: names under the notes.", "do re mi/2 | re (rest) do/2", "on", 72, time="4/4"),
        read("Again, names faint. Hold each long note its full two beats.", "mi/2 re do | re mi do/2", "faint", 72, time="4/4"),
        read("Three bars, no names: long notes, and a rest that counts.", "do mi so/2 | fa mi re (rest) | mi re do/2", "off", 72, time="4/4"),
    ]),
    lesson("ss-3-quick", "Quick notes", [
        learn("A quaver is half a beat. It has a flag, or it's joined to its neighbour by a beam, and two fit in one beat.", [
            ("Quaver", "Half a beat"),
            ("In pairs", "Two to a beat"),
            ("Say it", "One-and, two-and"),
        ]),
        read("Quick notes in pairs: names under the notes.", "do/0.5 re/0.5 mi re/0.5 do/0.5 re | mi/0.5 fa/0.5 so mi do", "on", 76, time="4/4"),
        read("Quick and long together, with a rest that counts. No names.", "so fa/0.5 mi/0.5 re do | re/0.5 mi/0.5 re/0.5 do/0.5 (rest) do", "off", 76, time="4/4"),
        read("Quick notes up to so, then home. No names.", "do/0.5 re/0.5 mi/0.5 fa/0.5 so mi | re/0.5 mi/0.5 re do/2", "off", 76, time="4/4"),
    ]),
    lesson("ss-3-dotted", "Dotted notes", [
        learn("A dot makes a note half as long again. A dotted minim is three beats, a whole bar of a waltz.", [
            ("Dotted minim", "Three beats"),
            ("In threes", "Count 1, 2, 3"),
            ("A tie", "A curve joining two of the same note: sing it once and hold through"),
        ]),
        read("A waltz in threes: names faint.", "do/2 re | mi/3 | re mi re | do/3", "faint", 72, time="3/4"),
        read("A dotted crotchet, then a short note: long, short. No names.", "do/1.5 re/0.5 mi fa | so/2 mi/2", "off", 72, time="4/4"),
        read("Ode to Joy's second line: you know how it goes; read its long-short.", "mi mi fa so | so fa mi re | do do re mi | re/1.5 do/0.5 do/2", "off", 72, time="4/4"),
    ]),
    lesson("ss-3-challenge", "A line in time", [
        learn(f"Four bars with long, short and quick notes, a long-short, and a rest. Look, count in, then read it in time. {COLD}", [
            ("Find do", "Then the longest notes"),
            ("Spot the rests", "They count too"),
            ("Keep going", "A slip? Catch the next beat"),
        ]),
        read("First its middle two bars, to warm up: names faint.", "fa/1.5 mi/0.5 (rest) re | mi/0.5 fa/0.5 so mi re", "faint", 80, time="4/4"),
        read("The whole line, in time, no names.", "do re mi/2 | fa/1.5 mi/0.5 (rest) re | mi/0.5 fa/0.5 so mi re | re do/3", "off", 80, time="4/4"),
    ], challenge=True, **fact("ss-3-challenge")),
]}

UNITS["ss-further"] = {"id": "ss-further", "title": EN("Further from do"), "lessons": [
    lesson("ss-5-la", "Up to la", [
        learn("La is a step above so: on the stave, the next line or space up. There's a low la too, a skip below do, just above low so.", [
            ("Up to la", "A step above so"),
            ("Low la", "A skip below do"),
            ("So, la, so, mi", "The notes of a playground chant"),
        ]),
        name_it("Hear the guide's notes, then sing la, a step above so.", [
            ([7], [9], "Sing la: a step above so"),
            ([0, 7], [9], "Sing la"),
        ], "Scored on singing la each time, close to its middle."),
        read("Up to la and back, then home: names under the notes.", "so la so mi | re re do/2", "on", 72),
        read("Down to low la and low so, then home: names faint.", "mi re do la, | so, la, do/2", "faint", 72),
        read("Up to la and back down, with no names.", "do re mi so | la so mi do", "off", 72),
    ]),
    lesson("ss-5-half", "The two half steps", [
        learn("Ti sits just below do. Mi to fa and ti to do look like every other step on the stave, but they're half as far: sing them close.", [
            ("Mi to fa", "Half a step: sing it close"),
            ("Ti to do", "Half a step: ti leans into do"),
            ("On the stave", "They look like every other step"),
        ]),
        wait_for_me("Off the stave for a moment: each note waits until you're on it. Keep fa close to mi.", "mi fa mi fa so", 72),
        read("Both half steps, names under the notes.", "mi fa mi re | do ti, do/2", "on", 72),
        read("Ti below do, then up to fa and back: names faint.", "do ti, do re | mi fa mi re | do", "faint", 72),
        read("From so down through both half steps, with no names.", "so la so fa | mi re do ti, | do", "off", 72),
    ]),
    lesson("ss-5-minor", "La is home", [
        learn("Start and end on la and the same notes sound minor. The signature doesn't change: find do, then la a skip below it. The drone now sounds la, your new home.", [
            ("Same signature", "Find do first"),
            ("La is home", "A skip below do"),
            ("La, do, mi", "The minor home chord"),
        ]),
        read("Out from la and home again, over the drone on la: names under the notes.", "la, ti, do ti, la,", "on", 72, home=LA),
        read("Up through the minor home chord and back: names faint.", "la, do mi do ti, la,", "faint", 72, home=LA),
        read("Up to mi and home to la, with no names.", "la, do re mi re do ti, la,", "off", 72, home=LA),
    ]),
    lesson("ss-5-challenge", "A minor line, read cold", [
        learn(f"Four bars in minor you haven't heard, steps and skips, in time. Find do, then la below it. {COLD}", [
            ("Find la", "A skip below do"),
            ("Count in", "Then keep the beat"),
            ("Keep going", "A slip? Catch the next beat"),
        ]),
        read("First a short minor line, to warm up: names faint.", "la, do mi re | do ti, la,/2", "faint", 72, time="4/4", home=LA),
        read("Now the whole line, cold, in time: no names.", "la,/1 do/1 mi/2 | re/1 do/1 ti,/2 | do/1 re/1 mi/0.5 re/0.5 do/1 | ti,/1 ti,/1 la,/2", "off", 72, time="4/4", home=LA),
    ], challenge=True),
]}

UNITS["ss-part-in-chord"] = {"id": "ss-part-in-chord", "title": EN("Your part in a chord"), "lessons": [
    lesson("ss-4-signature", "Sharps and flats at the start", [
        learn("Real music starts each line with a key signature: the sharps or flats there say which notes are always raised or lowered. Do moves with the key: it's the key's home note.", [
            ("Count them", "The sharps or flats at the start of every line"),
            ("All the way through", "Those notes stay raised or lowered"),
            ("A pickup", "The tune can start before the first bar line: count from its beat"),
        ]),
        learn("Do is home, and the signature tells you where it sits: look at its last sharp or flat.", [
            ("Sharps", "The last sharp sits on ti: do is the next line or space up"),
            ("Flats", "The last flat sits on fa; with two or more, do sits on the next-to-last flat"),
            ("None", "Do sits where the lesson's lines have always shown it"),
        ]),
        read_song("Amazing Grace's first line. Find do from the signature, then read: names faint.", "amazing-grace", "soprano", [0], "3/4", names="faint"),
        read_song("Its second line, with the same signature.", "amazing-grace", "soprano", [1], "3/4"),
        read_song("Its last line. It starts like the first: spot where it changes.", "amazing-grace", "soprano", [3], "3/4"),
    ], **fact("ss-4-signature")),
    lesson("ss-4-alto", "A part of its own", [
        learn("A choir part rarely has the tune. Read the alto of Michael, Row the Boat Ashore: its own line, mostly one held note under the tune, then a line that moves on its own.", [
            ("Your clef", "It follows your voice, not the part's name"),
            ("Look for the shape", "Long notes on one line or space, then a climb down and back"),
            ("Its signature", "Find do from it first"),
        ]),
        read_song("The alto's first line, on its own, the chords under you.", "michael-row", "alto", [0], "4/4"),
        read_song("The alto's second line: it climbs down below the stave's lowest notes so far, then back. Names faint.", "michael-row", "alto", [1], "4/4", names="faint"),
        read_song("Another song's alto, cold: Amazing Grace's first line, on its own.", "amazing-grace", "alto", [0], "3/4"),
    ]),
    lesson("ss-4-chord", "Inside the chord", [
        learn("Now the other parts sing while you read yours. Keep your eyes on your line and let the chord sound around you.", [
            ("Headphones on", "So the mic hears only you"),
            ("Don't follow the tune", "Your notes are on the stave"),
            ("Lost your place?", "Find the next bar's first note"),
        ]),
        read_song("The alto's first line, the other parts singing with you.", "michael-row", "alto", [0], "4/4", others=True),
        read_song("Amazing Grace's alto, its second line, the other parts singing with you.", "amazing-grace", "alto", [1], "3/4", others=True),
        read_song("Back to Michael, Row: its second line, inside the chord.", "michael-row", "alto", [1], "4/4", others=True),
    ]),
    lesson("ss-4-challenge", "Your part, read", [
        learn("The whole alto part of Michael, Row, read from the stave while the other parts sing. No names, no guide: you're reading in a choir.", [
            ("Find do", "From the signature"),
            ("Look ahead", "At the shape, not each note"),
            ("Keep going", "A slip? Catch the next beat"),
        ]),
        read("First, the line you read cold in your first challenge, read again. Then hear how far you've come.", FIRST_COLD, "off", 66, thenAndNow=KEEP),
        read_song("The whole alto part, inside the chord.", "michael-row", "alto", [0, 1], "4/4", others=True),
    ], challenge=True, **fact("ss-4-challenge")),
]}

assert sorted(UNIT_ORDER) == sorted(UNITS), UNIT_ORDER

course = {
    "id": "sight-singing",
    "version": 1,
    "reviewed": False,
    "title": EN("Sight-singing"),
    "units": [UNITS[u] for u in UNIT_ORDER],
}

OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"), ensure_ascii=False)
