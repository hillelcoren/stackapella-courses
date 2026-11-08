"""Musical theatre (docs/courses/musical-theatre.md in the app's repo): writes
course/plus/musical-theatre/course.json from the score transcriptions in tools/mt_scores.json (each
read twice off a public scan) and the course's own song, songs/hail-poetry.json. Every line counts
from the singer's comfortable note (0). Under the solos the generator lays plain chords (I, IV, V7
a bar, picked from the tune's notes): chords to sing over, not Sullivan's accompaniment. Breaths a
beginner can take are written in by tools/breaths.py before the file is written.

    python3 -I tools/mt_course.py && python3 -I tools/coursefmt.py course/plus/musical-theatre/course.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/musical-theatre/course.json"
SCORES = json.loads((REPO / "tools/mt_scores.json").read_text())
HAIL = json.loads((REPO / "course/plus/musical-theatre/songs/hail-poetry.json").read_text())
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

BANNED = re.compile(r"\b(stars?|starring|showstopper|break a leg|curtain call)\b", re.I)
SAFETY = "Medium volume, the middle of your voice; never push to be heard. Stop if anything tightens, scratches or hurts."


def EN(text):
    assert not BANNED.search(text), f"a word the course doesn't use: {text}"
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="phrase", listen=None):
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}
    if listen:
        step["listen"] = listen
    return step


def fact(fid, text, source, url):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


def play(text, exercise, measures=None, kind="play"):
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def selfcheck(text, model, questions, tempo):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


def choose(text, rounds, tempo):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


# ---- The tunes, laid from the comfortable note ----

def laid(name, ref, first=0, last=None, start=0):
    """Notes `first` to `last` of a transcription as steps from `ref` (the pitch that sits on your
    comfortable note), moved so the first starts at beat `start`."""
    src = SCORES[name]["notes"][first:last]
    at = src[0]["beat"]
    out = []
    for n in src:
        note = {"beat": round(n["beat"] - at + start, 4), "length": n["length"], "step": n["pitch"] - ref}
        if n.get("lyric"):
            note["lyric"] = n["lyric"]
        out.append(note)
    return out


def upto(name, word, after=0):
    """The index just past the first note (from `after`) whose lyric starts with `word`."""
    notes = SCORES[name]["notes"]
    return next(i for i in range(after, len(notes)) if (notes[i].get("lyric") or "").lower().startswith(word.lower())) + 1


def chords_for(notes, beats_per_bar, bar_start, home_pc, key_pc):
    """A plain chord a bar (I, IV or V7 of the key), the one holding most of the bar's notes by
    length, its root as steps from the comfortable note (within an octave below)."""
    options = [(0, "maj", (0, 4, 7)), (5, "maj", (5, 9, 0)), (7, "dom7", (7, 11, 2, 5))]
    end = max(n["beat"] + n["length"] for n in notes)
    out, bar = [], bar_start
    while bar < end - 1e-6:
        inside = [n for n in notes if bar - 1e-6 <= n["beat"] < bar + beats_per_bar - 1e-6]
        def fit(o):
            return sum(n["length"] * (1.5 if abs(n["beat"] - bar) < 1e-6 else 1) for n in inside if (n["step"] + home_pc - key_pc) % 12 in o[2])
        root, quality, _ = max(options, key=fit)
        step = (key_pc + root - home_pc) % 12 - 12
        if bar >= 0:
            out.append({"beat": bar, "root": step, "quality": quality, "bass": None})
        bar += beats_per_bar
    return out


# Buttercup: C major, 3/4, the pickup "I'm" on beat 0; G4 sits on your note.
BC_REF, BC_KEY_PC, BC_HOME_PC = 67, 0, 7  # ref G4: the key's do (C) is 7 semitones below it


def buttercup(first=0, last=None, start=0):
    notes = laid("buttercup", BC_REF, first, last, start)
    return notes


def bar_start(name, first, notes, beats_per_bar, first_bar):
    """Where the first bar line falls in a slice from note `first`: the score's own bar lines
    (`first_bar` is the first one's beat in the score), moved with the slice."""
    at = SCORES[name]["notes"][first]["beat"]
    return notes[0]["beat"] + ((first_bar - at) % beats_per_bar)


WHOLE_THOUGHTS = []  # (notes, keep): lines whose commas are held over once breaths.py has run


def whole_thoughts(notes, keep=()):
    """A line sung a thought to a breath (unit 1's lesson): once breaths.py has written in its breaths,
    each comma's note is held on into the next (hold_commas), so `entry` judges only the breaths where
    thoughts end. A comma whose beat is in `keep` keeps its breath: one a long thought needs."""
    WHOLE_THOUGHTS.append((notes, keep))
    return notes


def hold_commas(notes, keep):
    for n, nxt in zip(notes, notes[1:]):
        if (n.get("lyric") or "").endswith(",") and n["beat"] not in keep and nxt["beat"] > n["beat"] + n["length"]:
            n["length"] = round(nxt["beat"] - n["beat"], 4)


def buttercup_chords(notes, first=0):
    # 3/4 with the pickup "I'm" on beat 0: the score's bar lines fall on beats 1, 4, 7 ...
    return chords_for(notes, 3, bar_start("buttercup", first, notes, 3, 1), BC_HOME_PC, BC_KEY_PC)


L1 = upto("buttercup", "cup,")                 # I'm called little Buttercup,
L2 = upto("buttercup", "cup.", L1)             # dear little Buttercup.
L3 = upto("buttercup", "why", L2)              # Though I could never tell why;
L4 = upto("buttercup", "cup,", L3)             # But still I'm call'd Buttercup,
L5 = upto("buttercup", "cup,", L4)             # Poor little Buttercup,
L6 = len(SCORES["buttercup"]["notes"])         # Sweet little Buttercup I.

# The Major-General: written B flat 4 sits on your note (sung an octave lower by a baritone; the
# course follows your voice either way).
MG_REF = 70
MG_LINE1 = upto("majorgeneral", "ral;")        # I am the very model of a modern Major-General;
# Tit-willow: as printed in A flat, 6/8; A flat 4 sits on your note.
TW_REF, TW_KEY_PC = 68, 8
# Play steps never score timing (exercise.js passes timing 'none'): the measures say pitch, and where the
# beat is the point (patter), the singer listens back for it.
PITCH = "Scored on your notes on pitch."
PITCH_STEADY = PITCH + " Listen back: did it stay steady?"


# ---- Unit 1: Speak it, then sing it ----

def mt_1_speak():
    line = buttercup(0, L2)
    do = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line), "keep": "mt.first-line", "generous": True}
    return {
        "id": "mt-1-speak", "title": EN("Say it, then sing it"), "strictness": "relaxed",
        "fact": fact("beggars-opera-borrowed-tunes", "The Beggar's Opera (London, 1728) set new words to tunes everyone already knew, such as \"Over the Hills and far away\" and \"Green Sleeves\".",
                     "Gay, The Beggar's Opera (the 1765 edition's airs)", "https://www.gutenberg.org/ebooks/25063"),
        "steps": [
            learn("In a show, a song is the moment speaking isn't enough. Buttercup is selling her wares to a ship full of sailors: say her line, then sing it.",
                  [("Say it", "In rhythm, as you'd tell it"), ("Sing it", "The same words, now on the notes"), ("Easy does it", SAFETY)]),
            play("Speak the line in rhythm, the words in front of you. No notes yet: just say it as Buttercup would.", {"tempo": 88, "notes": line, "turn": False}, None, kind="try"),
            play("Now sing it over the chords. Keep it sounding like you talking.", do,
                 "Scored on your notes on pitch. Listen back: did it still sound like you telling someone?"),
        ],
    }


def waltz_clip(long_on_one, step=0):
    """Four notes over a waltz bar and a half: the long note on the ONE, or on beat 2."""
    notes = ([{"beat": 0, "length": 2, "step": step}, {"beat": 2, "length": 1, "step": step + 2}] if long_on_one
             else [{"beat": 0, "length": 1, "step": step}, {"beat": 1, "length": 2, "step": step + 2}])
    notes.append({"beat": 3, "length": 3, "step": step + 4})
    return {"notes": notes, "chords": [{"beat": 0, "root": -12 + (step % 12), "quality": "maj", "bass": None}]}


def mt_1_stress():
    rounds = []
    for k, first_right in enumerate([True, False, True]):
        right, wrong = waltz_clip(True, (0, 2, -3)[k]), waltz_clip(False, (0, 2, -3)[k])
        rounds.append({"prompt": EN("Which tune puts its long note on the ONE?"), "clips": [right, wrong] if first_right else [wrong, right],
                       "answer": 0 if first_right else 1, "why": EN("In 3/4 the first beat is the strong one: the word that matters goes there.")})
    line = buttercup(L1, L2)
    sing = {"tempo": 88, "notes": line, "turn": True, "chords": buttercup_chords(line, L1)}
    return {
        "id": "mt-1-stress", "title": EN("The word that matters"),
        "fact": fact("gilbert-inflection", "Gilbert directed his own operas and insisted his words be delivered \"even to an inflection of the voice, as he dictates\", repeating them beside the actor \"over and over again\".", "Grossmith, A Society Clown (1888)", "https://www.gutenberg.org/ebooks/53225"),
        "steps": [
            learn("In every line one word matters most, and the music puts it on a strong beat. In a waltz that's the ONE of ONE-two-three.",
                  [("ONE-two-three", "The waltz's strong beat"), ("The word that matters", "\"dear\", \"little\", \"Buttercup\""), ("Then sing it", "Line two, leaning on the ONE")]),
            choose("Listen to each, then choose.", rounds, 88),
            play("Line two: listen, then sing it, leaning on the ONE.", sing, PITCH),
        ],
    }


def breath_clip(at_comma):
    """Buttercup's first two lines on their notes, with a breath at the comma or only at the full stop."""
    notes = buttercup(0, L2)
    if at_comma:
        for n in notes:
            if n["beat"] >= notes[L1]["beat"] - 1e-6:
                n["beat"] += 1
    return {"notes": notes, "label": EN("A breath at \"Buttercup,\"" if at_comma else "One breath, after \"Buttercup.\"")}


def mt_1_thought():
    rounds = []
    for k in range(3):
        comma_first = k % 2 == 0
        clips = [breath_clip(True), breath_clip(False)] if comma_first else [breath_clip(False), breath_clip(True)]
        rounds.append({"prompt": EN("\"I'm called Little Buttercup, dear Little Buttercup\" is one thought. Which keeps it whole?"),
                       "clips": clips, "answer": 1 if comma_first else 0,
                       "why": EN("A breath at the comma cuts the thought in two. Breathe where it ends.")})
    line = buttercup(0, L3)
    sing = {"tempo": 88, "notes": whole_thoughts(line), "turn": False, "chords": buttercup_chords(line), "score": "entry"}
    return {
        "id": "mt-1-thought", "title": EN("Breathe where the thought ends"),
        "fact": fact("buttercup-bumboat-poem", "Little Buttercup grew out of Gilbert's own comic poem \"The Bumboat Woman's Story\", about a woman who sold the ships \"apples and cakes, and fowls, and beer\".", "Wikipedia, H.M.S. Pinafore", "https://en.wikipedia.org/wiki/H.M.S._Pinafore"),
        "steps": [
            learn("A breath belongs at the end of a thought, not at every comma. Breathing mid-thought cuts the sense in two.",
                  [("One thought", "Dear Little Buttercup, all of it"), ("Then breathe", "Where the thought ends"), ("Back in", "On time for the next one")]),
            choose("Listen to each, then choose.", rounds, 88),
            play("Lines one to three, a breath only where each thought ends.", sing, "Scored on coming back in on time and on pitch after each breath."),
        ],
    }


def mt_1_challenge():
    verse = buttercup(0, L6)
    # "But still I'm call'd Buttercup, Poor little Buttercup, Sweet little Buttercup I" is 22 beats, about
    # 15 s at 88 on one breath: it keeps one breath, after "Poor little Buttercup," (beat 36), so no
    # phrase runs over about 10 s.
    breath = verse[L5 - 1]["beat"]  # "Poor little Buttercup,"
    ex = {"tempo": 88, "notes": whole_thoughts(verse, keep=(breath,)), "turn": False, "chords": buttercup_chords(verse), "score": "entry", "thenAndNow": "mt.first-line"}
    return {
        "id": "mt-1-challenge", "title": EN("Little Buttercup"), "challenge": True,
        "steps": [
            learn("Buttercup's first verse, sold to the sailors: who she is, why they should buy.",
                  [("To the sailors", "You're selling, so tell them"), ("Breathe with the sense", "Where each thought ends"), ("Then and now", "Lesson 1 beside today")]),
            play("Once with the guide, to learn it.", {k: v for k, v in ex.items() if k not in ("thenAndNow", "score")}, None, kind="try"),
            play("Now the verse over the chords.", ex, "Scored on coming back in on time and on pitch after each breath."),
        ],
    }

# ---- Unit 2: Words first: patter ----

def major_general(first=0, last=None, start=0):
    return laid("majorgeneral", MG_REF, first, last, start)


def mt_2_two():
    one = major_general(0, MG_LINE1)
    steps = [learn("The Major-General knows everything but soldiering, and he can't stop showing it off. Patter: lots of words on two neighbouring notes.",
                   [("Two notes", "A step apart"), ("One word a beat", "Slowly first"), ("Echo", "The guide sings a bar, you answer")], visual="echo")]
    bars = [(0, 9), (9, MG_LINE1)]
    for k, (a, b) in enumerate(bars):
        ex = {"tempo": 60, "notes": major_general(a, b), "turn": True}
        steps.append(play(f"Bar {k + 1}: listen, then answer, slowly.", ex, PITCH_STEADY))
    steps.append(play("Now the whole line, slowly.", {"tempo": 60, "notes": one, "turn": True}, PITCH_STEADY))
    return {
        "id": "mt-2-two", "title": EN("Two notes, many words"),
        "fact": fact("grossmith-audition-1877", "At George Grossmith's audition in 1877, Sullivan told him \"Sing it out as loud as you can\". Gilbert said that a big voice \"is just what we don't want\".",
                     "Grossmith, A Society Clown (1888)", "https://www.gutenberg.org/ebooks/53225"),
        "steps": steps,
    }


def mt_2_consonants():
    one = major_general(0, MG_LINE1)
    return {
        "id": "mt-2-consonants", "title": EN("Consonant first"),
        "fact": fact("ruddigore-unintelligible-patter", "Gilbert joked about patter nobody can follow. A trio in Ruddigore (1887) sings: \"This particularly rapid, unintelligible patter isn't generally heard, and if it is, it doesn't matter!\"", "Wikipedia, Patter song", "https://en.wikipedia.org/wiki/Patter_song"),
        "steps": [
            learn("Put the consonant just before the beat, so the vowel lands on it. The app hears the vowel; so does the audience.",
                  [("Consonant early", "A hair before the beat"), ("Vowel on the beat", "That's the note"), ("Loose jaw", "Small, quick, easy")]),
            play("The line on the beat, consonants just ahead.", {"tempo": 66, "notes": one, "turn": True}, PITCH_STEADY),
            selfcheck("Once more, then play it back with the words shown.", one,
                      ["Which word got lost, if any?", "Did your jaw stay loose?"], 66),
        ],
    }


def rush_clip(rushed):
    notes = [{"beat": k * 0.5 - (0.12 if rushed and k in (5, 9, 13) else 0), "length": 0.5, "step": (0, 2)[k % 2]} for k in range(16)]
    return {"notes": notes}


def mt_2_quicker():
    one = major_general(0, MG_LINE1)
    rounds = [{"prompt": EN("Which patter rushed?"), "clips": [rush_clip(r), rush_clip(not r)], "answer": 0 if r else 1,
               "why": EN("A few of its words came early: clear patter stays even.")} for r in (True, False, True)]
    return {
        "id": "mt-2-quicker", "title": EN("A little quicker"),
        "fact": fact("patter-pater-noster", "The word \"patter\" comes from the Pater Noster, the Lord's Prayer said in Latin: people's habit of rushing through its words as quickly as possible gave English the word.", "Wikipedia, Patter song", "https://en.wikipedia.org/wiki/Patter_song"),
        "steps": [
            learn("Clear first, then quicker. Here the top speed is three words a second; the real thing is about twice that.",
                  [("Slow", "Every word clear"), ("Listen", "Which one rushed?"), ("Quicker", "Three words a second, even")], visual="echo"),
            play("Slowly first.", {"tempo": 66, "notes": one, "turn": True}, None, kind="try"),
            choose("Listen to each, then choose.", rounds, 90),
            play("Now at three words a second, even and clear.", {"tempo": 90, "notes": one, "turn": True}, PITCH_STEADY),
        ],
    }


def mt_2_challenge():
    first = major_general(0, MG_LINE1)              # up to "ral;", without "I've"
    second = major_general(MG_LINE1, None, first[-1]["beat"] + 2.5)      # "I've" after a breath
    ex = {"tempo": 90, "notes": first + second, "turn": False, "score": "entry", "thenAndNow": "mt.first-line"}
    return {
        "id": "mt-2-challenge", "title": EN("I am the very model"), "challenge": True,
        "steps": [
            learn("Both lines, showing off, with a breath after \"General\" where the first thought ends (unit 1).",
                  [("Line one", "I am the very model"), ("Breathe", "After \"General\""), ("Line two", "Information vegetable")], visual="echo"),
            play("Once with the guide.", {k: v for k, v in ex.items() if k not in ("thenAndNow", "score")}, None, kind="try"),
            play("Both lines, clear and even.", ex, "Scored on coming back in on time and on pitch after your breath."),
        ],
    }

# ---- Unit 3: Bright and legit ----

def mt_3_bright():
    line = buttercup(L2, L3)
    ex = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line, L2), "keep": "mt.bright"}
    return {
        "id": "mt-3-bright", "title": EN("Bright, like talking"),
        "fact": fact("higgins-spoken-melody", "When My Fair Lady opened on Broadway in 1956, Rex Harrison's music as Henry Higgins was \"written without sustained notes and with natural tonal patterns\": \"a spoken part that happens to have a melody\".", "Wikipedia, My Fair Lady", "https://en.wikipedia.org/wiki/My_Fair_Lady"),
        "steps": [
            learn("Say the line as if calling to a friend across a room, at speaking volume, then sing it that way. Bright is not belt. First steps to belting is the first step; full belt is for later, with a teacher.",
                  [("Call across the room", "Speaking volume, speech vowels"), ("Then sing it", "Near your comfortable note"), ("Stop if", "It scratches or tickles: sing it the legit way")]),
            play("The line, bright and easy, over the chords.", ex, PITCH),
            selfcheck("Once more, then hear yours beside the guide's.", line,
                      ["Did your throat feel as easy as when you talk?", "Did you get louder?"], 88),
        ],
    }


def why_clip(steady):
    n = {"beat": 0, "length": 3, "step": 0}
    if not steady:
        n["bend"] = [[0, 0], [2.2, 0], [3, -50]]
    return {"notes": [n]}


def mt_3_legit():
    line = buttercup(L2, L3)
    rounds = [{"prompt": EN("Which held \"why\" stayed steady?"), "clips": [why_clip(s), why_clip(not s)], "answer": 0 if s else 1,
               "why": EN("One sags at its end. Legit holds the note to its value, steady.")} for s in (True, False, True)]
    ex = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line, L2), "score": "release"}
    return {
        "id": "mt-3-legit", "title": EN("Tall and steady"),
        "fact": fact("singers-formant", "Trained operatic voices carry a strong energy peak near 3,000 hertz, the singer's formant. An orchestra makes relatively little sound up there, so the voice can be heard above it.", "National Center for Voice and Speech, The Singer's Formant", "https://ncvs.org/tutorials/the-singers-formant/"),
        "steps": [
            learn("Legit is the classic sound: tall vowels and long notes held to their full value. On \"why\", stay on \"ah\" and turn to \"ee\" only at the end.",
                  [("Tall vowels", "Space inside, jaw easy"), ("Stay on ah", "Why: ah, then ee at the cutoff"), ("Held to its value", "Then let go on time")]),
            choose("Listen to each, then choose.", rounds, 88),
            play("\"Though I could never tell why\", the \"why\" held tall to its end.", ex, "Scored on holding the long note to its end, steady, and letting go on time."),
            selfcheck("Once more, then hear yours beside the guide's.", line, ["Did \"why\" stay on \"ah\" until the end?", "Did your jaw stay easy?"], 88),
        ],
    }


def mt_3_diphthongs():
    words = [("why", 0), ("I", 2), ("my", 4), ("day", 3)]
    notes = []
    for k, (w, s) in enumerate(words):
        notes.append({"beat": k * 3, "length": 2, "step": s, "lyric": w})
    ex = {"tempo": 72, "notes": notes, "turn": True, "drone": {"step": 0}}
    return {
        "id": "mt-3-diphthongs", "title": EN("Hold the first vowel"),
        "fact": fact("sullivan-rhythm-first", "Sullivan said the first thing he decided in a song was its rhythm: \"I arrange the rhythm before I come to the question of melody.\"",
                     "Lawrence, Sir Arthur Sullivan (1899)", "https://archive.org/details/sirarthursulliva00lawruoft"),
        "steps": [
            learn("Why, I, my, day: each is two vowels. Hold the first, and give the second only at the very end. On high notes vowels bend; down here, keep them true.",
                  [("Why", "Ah, then a touch of ee"), ("Day", "Eh, then a touch of ee"), ("At the end", "The second vowel, quickly")]),
            play("Each word held two beats, the first vowel all the way.", ex, PITCH),
        ],
    }


TW_FIRST = upto("titwillow", "Wil-") - 1      # "Willow, tit-willow, tit-willow!"


def tit_willow():
    return laid("titwillow", TW_REF, TW_FIRST, upto("titwillow", "low!", TW_FIRST + 1))


def mt_3_challenge():
    line = tit_willow()
    # 6/8 as three quarter-note beats a bar; the score's pickup ("On a") is half a beat long.
    chords = chords_for(line, 3, bar_start("titwillow", TW_FIRST, line, 3, 0.5), TW_REF % 12, TW_KEY_PC)
    ex = {"tempo": 60, "notes": line, "turn": False, "chords": chords, "score": "entry", "thenAndNow": "mt.first-line"}
    return {
        "id": "mt-3-challenge", "title": EN("Tit-willow"), "challenge": True,
        "steps": [
            learn("Ko-Ko spins a sad tale of a little bird to win Katisha's heart. The time is 6/8: feel it in two big beats, not six small ones.",
                  [("In two", "ONE-and-a TWO-and-a"), ("Legit", "Tall vowels, held notes steady"), ("Then and now", "Lesson 1 beside today")]),
            play("Once with the guide, gently. On stage it moves a little quicker; clear first.", {k: v for k, v in ex.items() if k not in ("thenAndNow", "score")}, None, kind="try"),
            play("\"Willow, tit-willow, tit-willow\", over the chords.", ex, "Scored on coming back in on time and on pitch after each breath."),
        ],
    }

# ---- Unit 4: Sell the song ----

def mt_4_button():
    line = buttercup(L5, L6)
    ex = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line, L5), "score": "release"}
    return {
        "id": "mt-4-button", "title": EN("The button"),
        "fact": fact("gilbert-hands-wrists", "Henry Lytton asked Gilbert what to do with his hands on stage. \"Cut them off at the wrists, Lytton,\" came the quick reply, \"and forget you've got any hands!\"", "Lytton, The Secrets of a Savoyard (1922)", "https://www.gutenberg.org/ebooks/39392"),
        "steps": [
            learn("The button is a song's last note, held to its value, stopped on the beat, then stillness while the thought lands.",
                  [("Hold it", "To its full value"), ("Stop", "Exactly on the beat"), ("Stay still", "A moment after")]),
            play("\"Sweet Little Buttercup I\", the \"I\" held and stopped on the beat.", ex, "Scored on holding the last note to its end, steady, and stopping on time."),
            selfcheck("Once more, then play it back.", line, ["Did you stay still and keep the thought for a moment after the note?", "Did the last note stay steady to its end?"], 88),
        ],
    }


def mt_4_someone():
    line = buttercup(0, L2)
    ex = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line)}
    return {
        "id": "mt-4-someone", "title": EN("Sing it to someone"),
        "fact": fact("clear-speech-17-points", "In a 1985 study, five listeners with hearing loss heard sentences said clearly or conversationally. The clear ones were understood on average 17 percentage points better, at every playback level tested.", "Picheny, Durlach and Braida, Journal of Speech and Hearing Research (1985)", "https://doi.org/10.1044/jshr.2801.96"),
        "steps": [
            learn("Henry Irving told the young Henry Lytton to picture a friend who couldn't afford the stalls, at the back of the gallery: \"Let him hear every line you have to say.\" Sing to them, not louder.",
                  [("Pick someone", "At the very back"), ("Tell them", "This line is for them"), ("Not louder", "Clearer and meant")]),
            play("The first line, sung to your friend at the back.", ex, PITCH),
            selfcheck("Once more, then play it back.", line, ["Did it sound like you were telling them something?", "Was your voice as easy as in your first take?"], 88),
        ],
    }


HAIL_REF = 72  # C5 sits on your comfortable note: the tune's middle (the song is in C, after the arranger's check)


def hail_part(key, a, b, start=0):
    part = next(p for p in HAIL["parts"] if p["key"] == key)
    src = [n for n in part["guide"]["notes"] if a - 1e-6 <= n["beat"] < b - 1e-6]
    out = []
    for n in src:
        note = {"beat": round(n["beat"] - a + start, 4), "length": n["length"], "step": n["pitch"] - HAIL_REF}
        if n.get("lyric"):
            note["lyric"] = n["lyric"]
        out.append(note)
    return out


def mt_4_hail():
    phrases = HAIL["sections"][0]["phrases"]
    steps = [learn("\"Hail, Poetry\" is the chorus the pirates sing, moved to tears by a line of verse, and Sullivan marks it \"Voices only\": no orchestra. Your line is the tune, with the others around you.",
                   [("Voices only", "Just the company"), ("Phrase by phrase", "The first half today"), ("The last Hail", "Held, then let go on time")], visual="harmony")]
    for k, (a, b) in enumerate(phrases[:2]):
        ex = {"tempo": 72, "notes": hail_part("soprano", a, b), "turn": False,
              "with": [{"notes": hail_part(p, a, b), "volume": 0.5} for p in ("alto", "tenor", "bass")]}
        if k == 1:
            ex["score"] = "release"
        steps.append(play(f"Phrase {k + 1}, your tune with the company.", ex,
                          "Scored on holding the last note to its end and letting go on time." if k == 1 else PITCH))
    return {
        "id": "mt-4-hail", "title": EN("Hail, Poetry, the first half"),
        "fact": fact("pirates-new-york-1879", "The Pirates of Penzance opened in New York in December 1879, so Gilbert, Sullivan and Carte would have their own production on stage before the pirates of the stage could copy it.",
                     "Victoria and Albert Museum, The Pirates of Penzance silk programme", "https://collections.vam.ac.uk/item/O1370508/the-pirates-of-penzance-silk-programme-seer-a-s/"),
        "steps": steps,
    }


def mt_4_challenge():
    line = buttercup(L5, L6)
    ex = {"tempo": 88, "notes": line, "turn": False, "chords": buttercup_chords(line, L5), "score": "release", "thenAndNow": "mt.first-line"}
    return {
        "id": "mt-4-challenge", "title": EN("The company"), "challenge": True,
        "steps": [
            learn("Your button, then your part in the company: the tune of \"Hail, Poetry\", recorded in Sing over the guides.",
                  [("The button", "Buttercup's last line, then stillness"), ("Then and now", "Lesson 1 beside today"), ("Then Sing", "The tune in your own octave")], visual="harmony"),
            play("Buttercup's last line with its button.", ex, "Scored on holding the last note to its end and stopping on time."),
            {"kind": "record", "text": EN("The finale: record the tune of \"Hail, Poetry\" in Sing, over the guides. Add the other parts too if you like."),
             "courseSong": "songs/hail-poetry.json", "singers": 4, "part": "soprano", "measures": EN("Scored on the notes of your part.")},
        ],
    }


course = {
    "id": "musical-theatre", "version": 1, "reviewed": False, "title": EN("Musical theatre"),
    "units": [
        {"id": "mt-speak-then-sing", "title": EN("Speak it, then sing it"), "colour": 1, "lessons": [mt_1_speak(), mt_1_stress(), mt_1_thought(), mt_1_challenge()]},
        {"id": "mt-patter", "title": EN("Words first: patter"), "colour": 1, "lessons": [mt_2_two(), mt_2_consonants(), mt_2_quicker(), mt_2_challenge()]},
        {"id": "mt-bright-and-legit", "title": EN("Bright and legit"), "colour": 1, "lessons": [mt_3_bright(), mt_3_legit(), mt_3_diphthongs(), mt_3_challenge()]},
        {"id": "mt-sell-the-song", "title": EN("Sell the song"), "colour": 1, "lessons": [mt_4_button(), mt_4_someone(), mt_4_hail(), mt_4_challenge()]},
    ],
}
for where in add_breaths(course):
    print("no room to breathe:", where)
for notes, keep in WHOLE_THOUGHTS:
    hold_commas(notes, keep)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"))
