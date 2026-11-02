"""Diction for singers (docs/courses/diction.md in the app's repo): writes
course/plus/diction/course.json. Every line counts from the singer's comfortable note (0); the songs'
lines come from the library's own templates (public domain), laid round their middle pitch. Breaths a
beginner can take are written in by tools/breaths.py before the file is written.

What is scored is only what a pitch tracker honestly hears: a pure vowel's pitch (`lock`), the vowel's
start after an unvoiced consonant (`entry`, against your own vowel-word entries), a final unvoiced
consonant on a held note before a rest (`release`), and an n or m on its note (`landing`). Vowel
quality and consonant clarity are self-checks.

    python3 -I tools/di_course.py && python3 -I tools/coursefmt.py course/plus/diction/course.json
"""
import json
import re
import statistics
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/diction/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

BANNED = re.compile(r"\b(stars?|starring)\b", re.I)
SAFETY = "A loose jaw and an easy tongue: the tongue does t, d, n, l and s, and the jaw barely moves. Light consonants, never pushed. Stop if anything tightens."
TEMPO = 72


def EN(text):
    assert not BANNED.search(text), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="phrase"):
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def fact(fid, text, source, url):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


def play(text, exercise, measures=None, kind="play"):
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def selfcheck(text, model, questions, tempo=TEMPO):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


def choose(text, rounds, tempo=60):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


PITCH_BEAT = "Scored on your notes on pitch and on the beat."
LOCKED = "Scored on each held note staying on its pitch."
RELEASED = "Scored on each held note ending on time, steady to its end: the final consonant on the beat."
ENTRY = "Scored on each vowel starting on the beat, measured against your own vowel-word starts."
LANDED = "Scored on each note starting on its pitch, the n or m on the note, not sliding up into it."


def held_words(words, step=0, beats=2, rest=2, start=0):
    return [{"beat": start + k * (beats + rest), "length": beats, "step": step, "lyric": w} for k, w in enumerate(words)]


# ---- The library's songs, laid round their middle pitch ----

def tune(path, phrases):
    d = json.loads((REPO / path).read_text())
    mel = next(p for p in d["parts"] if p.get("melody"))
    spans = d["sections"][0]["phrases"]
    a, b = spans[phrases[0]][0], spans[phrases[-1]][1]
    notes = [n for n in mel["guide"]["notes"] if a - 1e-6 <= n["beat"] < b - 1e-6]
    ref = round(statistics.median(n["pitch"] for n in notes))
    out = []
    for n in notes:
        note = {"beat": round(n["beat"] - a, 4), "length": n["length"], "step": n["pitch"] - ref}
        if n.get("lyric"):
            note["lyric"] = n["lyric"]
        out.append(note)
    return out, d["tempo"]


GRACE = "templates/free/amazing-grace.json"
DANNY = "templates/library/danny-boy.json"
SHEN = "templates/library/shenandoah.json"


def song_ex(path, phrases, **extra):
    notes, tempo = tune(path, phrases)
    ex = {"tempo": min(tempo, 80), "notes": notes, "turn": False}
    ex.update(extra)
    return ex


def first_line(**extra):
    return song_ex(GRACE, [0], **extra)

# ---- Unit 1: Vowels that carry ----

def di_1_heard():
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "A-"}, {"beat": 1, "length": 2, "step": 5, "lyric": "maz-"}, {"beat": 3, "length": 1, "step": 9, "lyric": "ing"}]
    return {
        "id": "di-1-heard", "title": EN("Be heard"), "strictness": "relaxed",
        "steps": [
            learn("Diction is being understood. The note lives on the vowel. Sing Amazing Grace's first line as you normally would.",
                  [("Just sing it", "As you normally would"), ("Then again", "With one change"), ("Hear both", "Side by side")]),
            play("\"Amazing grace, how sweet the sound\", as you'd normally sing it.", first_line(keep="di.first-line", generous=True), PITCH_BEAT),
            learn("Now the stressed vowels full and pure, a-MA-zing, the small words light: \"the\" is just \"thuh\". Start \"Amazing\" easily: no click, no breathy h.",
                  [("Stressed vowels full", "a-MA-zing, SOUND"), ("Small words light", "\"the\" as \"thuh\""), ("An easy start", "No click, no h")]),
            play("The same line again, stressed vowels full, small words light.", first_line(), PITCH_BEAT),
            selfcheck("Once more, just \"Amazing\", then hear yours.", model, ["Did \"Amazing\" start cleanly, without a click?", "Was \"the\" light?"]),
        ],
    }


def di_1_pure():
    vowels = ["ah", "eh", "ee", "oh", "oo"]
    ex = {"tempo": TEMPO, "notes": held_words(vowels), "turn": False, "drone": {"step": 0}, "score": "lock"}
    return {
        "id": "di-1-pure", "title": EN("Pure vowels"),
        "fact": fact("high-vowels-misheard", "When 18 professional singers sang vowels very high, listeners often heard a different vowel: one whose first formant sits just above the sung note.", "Hollien, Mendes-Schwartz and Nielsen, Journal of Voice (2000)", "https://pubmed.ncbi.nlm.nih.gov/10875582/"),
        "steps": [
            learn("Hold each vowel pure, the same from start to end. Singers tend to drift sharp on \"ee\" and flat on \"oo\": the app hears that.",
                  [("One vowel", "The same all through"), ("On the note", "Ee not sharp, oo not flat"), ("A loose jaw", SAFETY)]),
            play("Ah, eh, ee, oh, oo, each held on the drone's note.", ex, LOCKED),
        ],
    }


def di_1_two():
    words = ["night", "day", "how", "boy"]
    ex = {"tempo": TEMPO, "notes": held_words(words), "turn": False, "drone": {"step": 0}, "score": "lock"}
    return {
        "id": "di-1-two", "title": EN("Two vowels, one note"),
        "steps": [
            learn("Night, day, how and boy each glide between two vowels. Hold the first and give the second only at the very end.",
                  [("Night", "Ah, then a touch of ee"), ("Day", "Eh, then a touch of ee"), ("How", "Ah, then a touch of oo")]),
            play("Each word held two beats, its first vowel all the way.", ex, LOCKED),
            selfcheck("\"Night\" once more, then hear yours.", held_words(["night"], beats=2, rest=0), ["Did \"night\" stay on \"ah\" until the end?", "Did your jaw stay loose?"]),
        ],
    }


def di_1_challenge():
    return {
        "id": "di-1-challenge", "title": EN("Amazing Grace, every vowel"), "challenge": True,
        "steps": [
            learn("Lesson 1's line again, then two lines: stressed vowels full, small words light. \"Lost but\" with nothing between, \"now am\" joined. Drop an r before a consonant.",
                  [("Then and now", "Lesson 1's line, today"), ("Two lines", "Stress and pure vowels"), ("Joined", "\"lost but\", \"now am\"")]),
            play("Lesson 1's line.", first_line(thenAndNow="di.first-line"), PITCH_BEAT),
            play("The first two lines.", song_ex(GRACE, [0, 1]), PITCH_BEAT),
        ],
    }

# ---- Unit 2: Consonants in time ----

ONSET = ["ah", "I", "two", "oh", "ah", "cold", "I", "oh", "past"]


def di_2_onset():
    ex = {"tempo": TEMPO, "notes": held_words(ONSET, beats=1, rest=1), "turn": False, "drone": {"step": 0}, "score": "entry"}
    return {
        "id": "di-2-onset", "title": EN("The vowel on the beat"),
        "fact": fact("vowel-onset-beat", "On commercial recordings, pianists most often played their notes with the singer's vowel, not with the consonant before it: the consonant comes just before the beat, the vowel on it.", "Sundberg and Bauer-Huppmann, When does a sung tone start?, Journal of Voice (2007)", "https://pubmed.ncbi.nlm.nih.gov/16564674/"),
        "steps": [
            learn("Hand on your throat: \"zzz\" buzzes, \"sss\" doesn't. The app hears only what buzzes. So for t, k, p and s, put the consonant just before the beat, and the vowel on it.",
                  [("Zzz, then sss", "One buzzes, one doesn't"), ("Consonant early", "Just before the beat"), ("Vowel on the beat", "That's what's heard")]),
            play("Each word on its beat, a rest between: the vowel words on the beat, and \"two\", \"cold\" and \"past\" with their consonant just before.", ex, ENTRY),
        ],
    }


def di_2_finals():
    ex = {"tempo": TEMPO, "notes": held_words(["night", "light", "past", "bright", "cold", "found"]), "turn": False, "drone": {"step": 0}, "score": "release"}
    return {
        "id": "di-2-finals", "title": EN("The end on the beat"),
        "steps": [
            learn("A word's last consonant goes exactly where the note ends. A final t, k, p or s is quick and light; a final d is light too, never \"found-uh\".",
                  [("Hold the vowel", "To the end of the note"), ("Then the consonant", "Right on the beat"), ("Light", "A short s, a soft d")]),
            play("Six held words, each consonant exactly on the note's end.", ex, RELEASED),
        ],
    }


def stop_clip(gap):
    return {"notes": [{"beat": 0, "length": 2, "step": 0, "lyric": "night"}, {"beat": 0, "length": 2 + gap, "step": 4}]}


def di_2_together():
    rounds = []
    for k, gap in enumerate([0.25, 0.15, 0.1, 0.06]):
        together_first = k % 2 == 0
        clips = [stop_clip(0), stop_clip(gap)] if together_first else [stop_clip(gap), stop_clip(0)]
        rounds.append({"prompt": EN("Which choir stopped together on \"night\"?"), "clips": clips, "answer": 0 if together_first else 1,
                       "why": EN("In one, a voice hangs on after the other has stopped.")})
    words = held_words(["night", "light", "past"])
    partner = [{"notes": [dict(n, step=4) for n in words], "volume": 0.5}]
    ex = {"tempo": TEMPO, "notes": words, "turn": False, "with": partner, "score": "release"}
    return {
        "id": "di-2-together", "title": EN("Together"),
        "steps": [
            learn("A choir's words end together, or a stray t or s sticks out. Listen for it, then end with the voice beside you.",
                  [("Listen", "Did they stop together?"), ("Then you", "With a partner voice"), ("Together", "Your end with its end")]),
            choose("Listen to each, then choose.", rounds),
            play("Three held words, your ends with the partner's.", ex, RELEASED),
        ],
    }


def di_2_challenge():
    return {
        "id": "di-2-challenge", "title": EN("Danny Boy"), "challenge": True,
        "steps": [
            learn("Lesson 1's line, then Danny Boy's first line: \"Danny\", \"boy\" and \"pipes\" start like t and p, the consonant just before the beat. Then three of its words held, their ends on the beat.",
                  [("Then and now", "Lesson 1's line, today"), ("The pipes", "Consonants early, vowels on the beat"), ("The ends", "On the beat")]),
            play("Lesson 1's line.", first_line(thenAndNow="di.first-line"), PITCH_BEAT),
            play("\"Oh Danny boy, the pipes, the pipes are calling\".", song_ex(DANNY, [0]), PITCH_BEAT),
            play("Three held words, a rest after each, their ends on the beat.", {"tempo": TEMPO, "notes": held_words(["boy", "pipes", "calling"]), "turn": False, "drone": {"step": 0}, "score": "release"}, RELEASED),
        ],
    }

# ---- Unit 3: On the consonant ----

def di_3_hum():
    hum = {"tempo": TEMPO, "notes": [{"beat": 0, "length": 4, "step": 0, "lyric": "mm"}], "turn": False, "drone": {"step": 0}, "score": "lock"}
    words = [{"beat": 0, "length": 1, "step": 0, "lyric": "ma-"}, {"beat": 1, "length": 1, "step": 2, "lyric": "ma"},
             {"beat": 4, "length": 1, "step": 2, "lyric": "sum-"}, {"beat": 5, "length": 1, "step": 0, "lyric": "mer"},
             {"beat": 8, "length": 2, "step": 0, "lyric": "home"}]
    return {
        "id": "di-3-hum", "title": EN("On the m"),
        "fact": fact("english-voiced-consonants", "In English, r, l, w, y, m, n and ng are always voiced: the vocal folds vibrate right through them, and none has a voiceless twin.", "Russell, Describing consonants, University of Manitoba", "https://home.cc.umanitoba.ca/~krussll/phonetics/articulation/describing-consonants.html"),
        "steps": [
            learn("An m has pitch: it's on the note, short, and the vowel gets the length. Only a final m hums through to the end. This one is kinder.",
                  [("The hum", "On the note"), ("Short", "The vowel gets the length"), ("A final m", "Hums to the end")]),
            play("A hum on the drone's note.", hum, LOCKED),
            play("\"mama\", \"summer\", \"home\": each m on the note.", {"tempo": TEMPO, "notes": words, "turn": False, "drone": {"step": 0}}, PITCH_BEAT),
        ],
    }


def di_3_n_l():
    words = held_words(["nine", "only", "long", "all"])
    return {
        "id": "di-3-n-l", "title": EN("The n on the note"),
        "steps": [
            learn("n and l have pitch too. Put them on the note, not below it sliding up. \"Long\" has no g after the ng; \"all\" ends on a light l.",
                  [("On the note", "Not under it"), ("No g", "\"long\", not \"long-g\""), ("A light l", "The tongue tip")]),
            play("Four held words, each n or l on the note.", {"tempo": TEMPO, "notes": words, "turn": False, "drone": {"step": 0}, "score": "landing"}, LANDED),
        ],
    }


def di_3_buzz():
    words = held_words(["very", "zoo", "love"])
    return {
        "id": "di-3-buzz", "title": EN("Buzz, not hiss"),
        "steps": [
            learn("v and z can buzz on the note, or hiss without it. Buzz them.",
                  [("Very", "A buzzing v"), ("Zoo", "A buzzing z"), ("Love", "A light v at the end")]),
            play("Three held words, the v and z buzzing on the note.", {"tempo": TEMPO, "notes": words, "turn": False, "drone": {"step": 0}}, "Scored on the vowels' pitch."),
            selfcheck("\"Zoo\" once more, then hear yours.", held_words(["zoo"], rest=0), ["Did the z buzz, or hiss?", "Did your jaw stay still?"]),
        ],
    }


def di_3_challenge():
    return {
        "id": "di-3-challenge", "title": EN("Shenandoah"), "challenge": True,
        "steps": [
            learn("Lesson 1's line, then Shenandoah's first line, full of n's: each one on the note, not sliding up.",
                  [("Then and now", "Lesson 1's line, today"), ("Shenandoah", "Every n on the note"), ("Long", "No g after the ng")]),
            play("Lesson 1's line.", first_line(thenAndNow="di.first-line"), PITCH_BEAT),
            play("\"Oh Shenandoah, I long to hear you\".", song_ex(SHEN, [0], score="landing"), LANDED),
        ],
    }

# ---- Unit 4: Words for an audience ----

def di_4_heard():
    line, _ = tune(GRACE, [1])
    return {
        "id": "di-4-heard", "title": EN("Would they understand?"),
        "fact": fact("sung-words-errors", "Listeners writing down words sung by advanced voice students made 7.3 times as many mistakes as with the same words spoken.", "Johnson, Huron and Collister, Empirical Musicology Review (2014)", "https://doi.org/10.18061/emr.v9i1.3729"),
        "steps": [
            learn("You always understand your own words. Would a stranger? Sing a line, then listen with the words hidden.",
                  [("Sing it", "For someone at the back"), ("Hide the words", "And listen"), ("Not louder", SAFETY)]),
            play("\"That saved a wretch like me\".", song_ex(GRACE, [1]), PITCH_BEAT),
            selfcheck("Once more, then hear yours with the words hidden.", line, ["Pick one word: did you hear its last consonant?", "Did your jaw stay still for the t and n?"]),
        ],
    }


def di_4_choir():
    line, tempo = tune(GRACE, [1])
    oo = {"tempo": TEMPO, "notes": [{"beat": 0, "length": 3, "step": 0, "lyric": "oo"}], "turn": False, "with": [{"notes": [{"beat": 0, "length": 3, "step": 0, "lyric": "oo"}], "volume": 0.6}]}
    ex = {"tempo": min(tempo, 80), "notes": line, "turn": False, "with": [{"notes": [dict(n) for n in line], "volume": 0.5}]}
    return {
        "id": "di-4-choir", "title": EN("One choir, one vowel"),
        "steps": [
            learn("A choir is understood when it sings the same vowel at the same time. Match the voice beside you.",
                  [("Match its oo", "The same shape"), ("Then the words", "In unison"), ("Together", "Vowels and ends")]),
            play("Match the guide's \"oo\".", oo, None, kind="try"),
            play("The line in unison with a partner voice.", ex, PITCH_BEAT),
            selfcheck("Once more, then hear yours beside the partner.", line[:4], ["Did your vowels match the partner's?", "Did your ends land with its ends?"]),
        ],
    }


def di_4_lining():
    notes, tempo = tune(GRACE, [0, 1, 2, 3])
    spans = json.loads((REPO / GRACE).read_text())["sections"][0]["phrases"]
    for n in notes:
        line = next(k for k, (a, b) in enumerate(spans) if a - 1e-6 <= n["beat"] < b - 1e-6)
        if line % 2 == 0:
            n["listenOnly"] = True
    return {
        "id": "di-4-lining", "title": EN("Lining out"),
        "steps": [
            learn("In lining out, a leader sings a line and the group answers. The guide sings lines 1 and 3; you answer with 2 and 4, every word.",
                  [("The leader", "Lines 1 and 3"), ("You", "Lines 2 and 4"), ("Every word", "Stress, vowels, ends")]),
            play("Amazing Grace's first verse, taking turns with the guide.", {"tempo": min(tempo, 80), "notes": notes, "turn": False}, PITCH_BEAT),
        ],
    }


def di_4_challenge():
    line, _ = tune(SHEN, [0])
    return {
        "id": "di-4-challenge", "title": EN("Every word, heard"), "challenge": True,
        "steps": [
            learn("Lesson 1's line to hear how far you've come, then the end of Shenandoah's verse, every word for the back of the room.",
                  [("Then and now", "Lesson 1's line, today"), ("The verse's end", "Stress, pure vowels, the n on the note"), ("Not louder", "Clearer")]),
            play("Lesson 1's line.", first_line(thenAndNow="di.first-line"), PITCH_BEAT),
            selfcheck("Shenandoah's first line, then hear it with the words hidden.", line, ["Could a stranger write the line down?", "Did your jaw stay loose?"]),
            # The verse's second half (phrases 2 to 4): a whole sentence ending home, -4 to +5 round
            # your note. The first two lines span 17 semitones, an octave below to a fourth above (the arranger, 2026-11-02).
            play("\"Oh Shenandoah, I long to hear you, away, I'm bound away, 'cross the wide Missouri.\"", song_ex(SHEN, [2, 3, 4]), PITCH_BEAT),
        ],
    }


course = {
    "id": "diction", "version": 1, "reviewed": False, "title": EN("Diction for singers"),
    "units": [
        {"id": "di-vowels", "title": EN("Vowels that carry"), "colour": 2, "lessons": [di_1_heard(), di_1_pure(), di_1_two(), di_1_challenge()]},
        {"id": "di-consonants", "title": EN("Consonants in time"), "colour": 2, "lessons": [di_2_onset(), di_2_finals(), di_2_together(), di_2_challenge()]},
        {"id": "di-on-the-consonant", "title": EN("On the consonant"), "colour": 2, "lessons": [di_3_hum(), di_3_n_l(), di_3_buzz(), di_3_challenge()]},
        {"id": "di-for-an-audience", "title": EN("Words for an audience"), "colour": 2, "lessons": [di_4_heard(), di_4_choir(), di_4_lining(), di_4_challenge()]},
    ],
}
for where in add_breaths(course):
    print("no room to breathe:", where)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"))
