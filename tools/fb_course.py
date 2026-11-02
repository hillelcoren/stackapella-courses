"""First steps to belting (docs/courses/belting.md in the app's repo; its rules from
docs/courses/belting-voice-health.md): writes course/plus/belting/course.json. A bridge course of
bright, speech-like calls, low and easy, never full belt (Hillel, 2026-11-02).

The rules every line keeps:
- Belt notes (the calls) sit from 3 below to 2 above the comfortable note (0); light notes (a sigh, a
  hum, a light "hoo", a trill) may go to 4 above, and stay light.
- Every group of calls ends in a light tail, in the same line.
- Calls start on h, y, n, m or w; holds are 2 beats at most (1.5 s at 80).
- No loudness anywhere: the app can't hear it, and no step asks for it.

What's scored is only what pitch shows: the notes on pitch and on the beat, and a short hold steady
(`lock`). Brightness, loudness and strain are self-checks on the singer's playback.

The app's three Belting features (a daily cap, a lower-only key, a retry cap) are written in once
they're in the course format: set FEATURES = True then. Game mode's rules (GAME) are in already.

    python3 -I tools/fb_course.py && python3 -I tools/coursefmt.py course/plus/belting/course.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/belting/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

FEATURES = True  # dailyCap, keyRange and retries (in the format since main 096ca8e4)
GAME = True  # game mode's rules and the spiritual's quiet lesson (in the format since main dd133c6c)

BANNED = re.compile(r"\b(stars?|starring|loud(er|ly)?|power(ful)?|strong(er)?|push(ing)? it)\b|—|–", re.I)
ALLOWED_LOUD = ("Louder than talking?", "as loud as you'd call", "without being any louder", "without being loud", "not a shout")
TEMPO = 80
CEILING, FLOOR, LIGHT_TOP = 2, -3, 4
STOP = "Rest if anything tightens, scratches, tickles or hurts. Skip today if you're hoarse or tired."


def EN(text):
    checked = text
    for ok in ALLOWED_LOUD:
        checked = checked.replace(ok, "")
    assert not BANNED.search(checked), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="phrase"):
    """A lesson's first card always carries the stop line."""
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def first(headline, cards, visual="phrase"):
    return learn(headline, list(cards)[:2] + [("Stop if it hurts", STOP)], visual)


def fact(fid, text, source, url):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


def play(text, exercise, measures=None):
    step = {"kind": "play", "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def selfcheck(text, model, questions, tempo=TEMPO):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


def choose(rounds, tempo=TEMPO):
    return {"kind": "choose", "text": EN("Listen to each, then choose."), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


ONLY_PITCH = " Pitch and timing only: the app can't hear brightness, loudness or strain."
CALLS = "Scored on each call and its light tail on pitch and on the beat." + ONLY_PITCH
HELD = "Scored on each short hold staying steady on its pitch." + ONLY_PITCH


# ---- Calls, and the light tail after each group ----

def call(word, step, beat, length=1.0, start=True):
    assert FLOOR <= step <= CEILING, (word, step)
    assert length <= 2, (word, length)
    if not word:  # the same word going on (a call's fall), no new start
        return {"beat": beat, "length": length, "step": step}
    assert not start or re.match(r"[hymnwHYMNW]", word), word  # a call starts easy: never a vowel or a hard attack
    return {"beat": beat, "length": length, "step": step, "lyric": word}


TAILS = {
    "oo": [("oo", 4, 0.5), ("", 1, 0.5), ("", -1, 1.5)],   # a sigh down
    "mm": [("mm", 2, 1), ("", -2, 1.5)],                   # a hum gliding down
    "hoo": [("hoo", 4, 1.5)],                               # a light echo above
    "brr": [("brr", 4, 0.5), ("", 2, 0.5), ("", 0, 0.5), ("", -2, 1)],  # a lip trill (or hum) down
}


def tail(kind, beat):
    notes = []
    for word, step, length in TAILS[kind]:
        assert step <= LIGHT_TOP
        note = {"beat": beat, "length": length, "step": step}
        if word:
            note["lyric"] = word
        notes.append(note)
        beat += length
    return notes, beat


def calls(groups, kind, gap=1):
    """Groups of (word, step[, length]) calls, each group followed by a light tail."""
    notes, beat = [], 0
    for group in groups:
        for k, c in enumerate(group):
            word, step, length = (c + (1.0,))[:3]
            notes.append(call(word, step, beat, length, start=k == 0))
            beat += length
        beat += gap
        light, beat = tail(kind, beat)
        notes += light
        beat += gap
    return notes


def ex(notes, score=None, tempo=TEMPO, **extra):
    e = {"tempo": tempo, "notes": notes, "turn": True}
    if score:
        e["score"] = score
    if FEATURES:
        e["keyRange"] = {"down": 4, "up": 0}
        e["retries"] = 3
    e.update(extra)
    return e


def warmup(kind):
    """The light start every lesson opens with: a hum or trill sliding down, no calls."""
    light, _ = tail(kind, 0)
    second, _ = tail(kind, 4)
    return play("Warm up light first: a gentle " + {"mm": "hum on \"mm\"", "brr": "lip trill (or a hum)", "oo": "\"oo\" sighing down", "hoo": "\"hoo\""}[kind] + ", twice.",
                ex(light + second), "Scored on the notes on pitch: just a light start.")


# ---- The library's lines, written out so the key can't rise: the tune's top at +2 ----

def excerpt(slug, phrase, count=None, partners=(), until=None):
    d = json.loads((REPO / f"templates/library/{slug}.json").read_text())
    spans = [span for sec in d["sections"] for span in sec["phrases"]]
    a, b = spans[phrase]
    parts = {p["key"]: [n for n in p["guide"]["notes"] if a - 1e-6 <= n["beat"] < b - 1e-6 and n.get("pitch") is not None] for p in d["parts"]}
    mel = next(p["key"] for p in d["parts"] if p.get("melody"))
    tune = parts[mel][:count] if count else parts[mel]
    top = max(n["pitch"] for n in tune)
    end = until if until is not None else max(n["beat"] + n["length"] for n in tune)  # partners stop here (beats from the phrase's start)

    def lay(ns, cut=False):
        return [dict({"beat": round(n["beat"] - a, 4), "length": n["length"], "step": n["pitch"] - top + CEILING},
                     **({"lyric": n["lyric"]} if n.get("lyric") else {}))
                for n in ns if not cut or n["beat"] - a < end - 1e-6]

    notes = lay(tune)
    assert all(FLOOR <= n["step"] <= CEILING for n in notes), (slug, [n["step"] for n in notes])
    with_ = [{"notes": lay(parts[k], cut=True), "volume": 0.45} for k in partners if parts.get(k)]
    return notes, with_


def song_line(slug, phrase, count=None, partners=(), light="oo", until=None):
    notes, with_ = excerpt(slug, phrase, count, partners, until)
    end = max([n["beat"] + n["length"] for n in notes] + [m["beat"] + m["length"] for w in with_ for m in w["notes"]])
    tail_notes, _ = tail(light, end + 1)
    e = ex(notes + tail_notes)
    if with_:
        e["with"] = with_
    return e


# ---- Unit 1: Calls from speech ----

def b_1_call():
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]
    return {
        "id": "belting-1-call", "title": EN("The call"), "strictness": "relaxed",
        "fact": fact("roll-yell-belt", "Studying the teachers behind Broadway's belters, Christianne Roll found they built belt as a blend, always working the light voice beside it: \"a full chest voice 'yell belt' was never encouraged\".",
                     "Roll, The Evolution of the Female Broadway Belt Voice, Journal of Voice (2016)", "https://www.nats.org/_Library/Science_Informed_Voice_Pedagogy_Resource/Article_Evolution_of_the_Female_Broadway_Belt_Voice-_Implications_for_Teachers_and_Singers.pdf"),
        "steps": [
            first("Belt starts as a call: the way you'd call a friend across a room. Bright and easy, never a shout.",
                  [("Speak it first", "\"Hey!\", across a room"), ("Then sing it", "Two notes, falling, short")], visual="echo"),
            warmup("mm"),
            selfcheck("Say \"Hey!\" as if calling a friend across a room, then sing it on the two notes. Hear both.", model,
                      ["Did the sung one sound like your spoken one?", "Louder than talking? Then call it softer next time."]),
            play("\"Hey!\" sung, three times, each followed by a light \"oo\" sighing down.",
                 ex(calls([[("hey!", 2), ("", -1)]] * 3, "oo"), keep="belting.first-call", generous=True), CALLS),
            play("Now in a round from 1609: \"Hey, ho, nobody home\", with another voice coming in on your \"Hey, ho\".",
                 song_line("hey-ho-nobody-home", 0, partners=("alto",)), CALLS),
        ],
    }


def b_1_onset():
    model = [{"beat": k * 2, "length": 1, "step": s, "lyric": w} for k, (w, s) in enumerate([("hey", 2), ("yeah", 0), ("no", 2), ("my", 0)])]
    return {
        "id": "belting-1-onset", "title": EN("Start on h, y, n"),
        "steps": [
            first("Every call starts on a sound that eases the voice in: h, y, n, m or w. Never a vowel on its own, which can start with a click.",
                  [("Easy starts", "hey, yeah, no, my, whoa"), ("No click", "The sound slides in")]),
            warmup("mm"),
            selfcheck("\"Hey, yeah, no, my\": hear them back.", model, ["Did any call start with a click?"]),
            play("Calls in pairs, each pair followed by a light \"oo\".",
                 ex(calls([[("hey!", 2), ("yeah!", 0)], [("no!", 2), ("my!", 0)], [("whoa!", 1), ("nah!", -1)]], "oo")), CALLS),
        ],
    }


def b_1_easy():
    right = {"notes": [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]}
    wrong = {"notes": [{"beat": 0, "length": 3, "step": 2, "lyric": "hey!"}]}
    rounds = [{"prompt": EN("Which call is short and falls at the end, like speech?"), "clips": [right, wrong] if k % 2 == 0 else [wrong, right],
               "answer": 0 if k % 2 == 0 else 1, "why": EN("The other holds its top note: that's where calls turn into pushing.")} for k in range(3)]
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]
    return {
        "id": "belting-1-easy", "title": EN("As easy as talking"),
        "fact": fact("popeil-perceived-volume", "Brightness, ring and a little nasality make a voice sound bigger to listeners without being any louder: one reason a bright call carries across a room.",
                     "Popeil, NATS Chat handout (2017)", "https://www.nats.org/_Library/NATS_Chat_2014_15/NATS_Chat_LisaPopeil_handout_April_9_2017.pdf"),
        "steps": [
            first("A bright call carries without being loud: brightness does the work, so your voice doesn't have to.",
                  [("Short", "A beat, then it falls"), ("Easy", "Could you do it all day?")]),
            warmup("oo"),
            choose(rounds),
            selfcheck("\"Hey!\" once more, then hear it.", model, ["Louder than talking? Then go lighter: a call, not a shout."]),
            play("\"Hey, yeah!\" calls, each pair with its light \"oo\".", ex(calls([[("hey!", 2), ("yeah!", -1)]] * 3, "oo")), CALLS),
        ],
    }


def b_1_challenge():
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]
    return {
        "id": "belting-1-challenge", "title": EN("Calls"), "challenge": True,
        "steps": [
            first("Lesson 1's call beside today's, then the unit's calls in a row.",
                  [("Then and now", "Which sounds easier?"), ("Calls in a row", "Each pair with its light tail")]),
            warmup("mm"),
            play("Lesson 1's call.", ex(calls([[("hey!", 2), ("", -1)]] * 3, "oo"), thenAndNow="belting.first-call"), CALLS),
            selfcheck("Hear both back.", model, ["Which sounded easier, then or now?"]),
            play("\"Hey, yeah\" and \"no, my\", each pair with its light \"oo\".",
                 ex(calls([[("hey!", 2), ("yeah!", 0)], [("no!", 2), ("my!", -1)]], "oo")), CALLS),
        ],
    }


# ---- Unit 2: Say it, then sing it (the light tail: a hum) ----

def phrase_clip(even):
    lengths, steps = ([1, 1, 1], [1, 1, 1]) if even else ([0.5, 0.5, 1.5], [2, 1, -2])
    notes, beat = [], 0
    for k, (length, step) in enumerate(zip(lengths, steps)):
        note = {"beat": beat, "length": length, "step": step}
        if k == 0:
            note["lyric"] = "No you don't!"
        notes.append(note)
        beat += length
    return {"notes": notes}


def b_2_phrase():
    rounds = [{"prompt": EN("Which one sounds like speech?"), "clips": [phrase_clip(False), phrase_clip(True)] if k % 2 == 0 else [phrase_clip(True), phrase_clip(False)],
               "answer": 0 if k % 2 == 0 else 1, "why": EN("Speech is quick, then falls on the last word; the other plods on one note.")} for k in range(3)]
    model = [{"beat": 0, "length": 0.5, "step": 2, "lyric": "No"}, {"beat": 0.5, "length": 0.5, "step": 1, "lyric": "you"}, {"beat": 1, "length": 1.5, "step": -2, "lyric": "don't!"}]
    return {
        "id": "belting-2-phrase", "title": EN("No you don't"),
        "fact": fact("roll-no-you-dont", "One of the master teachers in Roll's study had singers call a phrase like \"No you don't\" in bright, forward speech, and then sing it the same way.",
                     "Roll, Journal of Voice (2016)", "https://www.nats.org/_Library/Science_Informed_Voice_Pedagogy_Resource/Article_Evolution_of_the_Female_Broadway_Belt_Voice-_Implications_for_Teachers_and_Singers.pdf"),
        "steps": [
            first("Now a phrase: \"No you don't!\", teasing a friend across the room. Say it, then sing it the same way.",
                  [("Speech shape", "Quick, then falling"), ("Same voice", "The sung one sounds like the spoken one")]),
            warmup("mm"),
            choose(rounds),
            selfcheck("Say \"No you don't!\", then sing it. Hear both.", model, ["Did the sung one keep your speaking voice?"]),
            play("\"No you don't!\" sung, three times, each followed by a hum.",
                 ex(calls([[("No", 2, 0.5), ("you", 1, 0.5), ("don't!", -2, 1.5)]] * 3, "mm")), CALLS),
        ],
    }


def b_2_come():
    model = [{"beat": 0, "length": 0.5, "step": 2, "lyric": "Hey,"}, {"beat": 0.5, "length": 0.5, "step": 1, "lyric": "come"}, {"beat": 1, "length": 1, "step": -1, "lyric": "here!"}]
    return {
        "id": "belting-2-come", "title": EN("Hey, come here"),
        "steps": [
            first("Two- and three-word calls, each falling at the end, the way speech does.",
                  [("Hey, come here!", "Three notes, down"), ("Hello! Whoa there!", "Two notes, down")]),
            warmup("mm"),
            selfcheck("\"Hey, come here!\": hear it back.", model, ["Did it fall at the end, like speech?"]),
            play("Three calls, each followed by a hum.",
                 ex(calls([[("Hey,", 2, 0.5), ("come", 1, 0.5), ("here!", -1, 1)], [("Hel-", 1, 0.5), ("lo!", -1, 1)], [("Whoa", 2, 0.5), ("there!", -1, 1)]], "mm")), CALLS),
        ],
    }


def b_2_twang():
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "nyeah"}, {"beat": 1, "length": 1, "step": -2, "lyric": "nyeah"}]
    return {
        "id": "belting-2-twang", "title": EN("Nyeah"),
        "steps": [
            first("A small, silly \"nyeah\", like a kid teasing: it brightens the sound with no effort at all. If it pinches, drop it and go on.",
                  [("Small and silly", "Low, short, spoken first"), ("Then \"yeah\"", "The same brightness, without the nasal")]),
            warmup("mm"),
            selfcheck("Say \"nyeah-nyeah\", then sing it. Hear it back.", model, ["Any pinch or squeeze? Then leave it: this one is optional."]),
            play("\"Nyeah\", then \"yeah\" from it, each pair with a hum.",
                 ex(calls([[("nyeah", 0), ("yeah!", -2)]] * 3, "mm")), CALLS),
        ],
    }


def b_2_challenge():
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]
    return {
        "id": "belting-2-challenge", "title": EN("Say it, sing it"), "challenge": True,
        "steps": [
            first("The unit's phrases, said then sung.",
                  [("No you don't!", "Teasing, across a room"), ("Hey, come here!", "Falling at the end")]),
            warmup("brr"),
            selfcheck("Say each phrase once, then sing \"hey!\". Hear it.", model, ["Did the sung voice match the spoken one?"]),
            play("\"No you don't!\", \"Hey, come here!\", \"Whoa there!\", each with a hum.",
                 ex(calls([[("No", 2, 0.5), ("you", 1, 0.5), ("don't!", -2, 1.5)], [("Hey,", 2, 0.5), ("come", 1, 0.5), ("here!", -1, 1)], [("Whoa", 2, 0.5), ("there!", -1, 1)]], "mm")), CALLS),
        ],
    }


# ---- Unit 3: Short holds, and letting go (the light tail: a "hoo" above) ----

def b_3_hold():
    right = {"notes": [{"beat": 0, "length": 2, "step": 0, "lyric": "hey"}]}
    wrong = {"notes": [{"beat": 0, "length": 4, "step": 0, "lyric": "hey"}]}
    rounds = [{"prompt": EN("Which hold stayed short?"), "clips": [right, wrong] if k % 2 == 0 else [wrong, right],
               "answer": 0 if k % 2 == 0 else 1, "why": EN("Short holds are easy; long ones are where pressing creeps in.")} for k in range(3)]
    model = [{"beat": 0, "length": 2, "step": 0, "lyric": "hey"}]
    return {
        "id": "belting-3-hold", "title": EN("A short hold"),
        "fact": fact("voice-recovery-hours", "After two hours of reading aloud, voices in a University of Utah study had made 90% of their recovery within 4 to 6 hours, and recovered fully in 12 to 18.",
                     "Hunter and Titze, Annals of Otology, Rhinology and Laryngology (2009)", "https://iro.uiowa.edu/esploro/outputs/journalArticle/Quantifying-Vocal-Fatigue-Recovery-Dynamic-Vocal/9984446403802771"),
        "steps": [
            first("A call held two beats, steady and easy, then let go into a light \"hoo\" above.",
                  [("Two beats", "Never longer"), ("Low first", "Then the middle, then a little higher")]),
            warmup("hoo"),
            choose(rounds),
            selfcheck("\"Hey\" held two beats: hear it.", model, ["Could you do that ten more times, easily? If not, rest."]),
            play("\"Hey\" held at three heights, low first, each followed by a light \"hoo\".",
                 ex(calls([[("hey", -2, 2)], [("hey", 0, 2)], [("hey", 2, 2)]], "hoo"), "lock", generous=True), HELD),
        ],
    }


def b_3_colours():
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "hey"}, {"beat": 2, "length": 1, "step": 0, "lyric": "hoo"}]
    notes = []
    for k, step in enumerate([-2, 0, 2]):
        notes += [call("hey", step, k * 5, 1), {"beat": k * 5 + 2, "length": 1.5, "step": step, "lyric": "hoo"}]
    return {
        "id": "belting-3-colours", "title": EN("Same note, two colours"),
        "steps": [
            first("The same note two ways: \"hey\" bright, then \"hoo\" light. Singers who belt well always keep the light voice beside it.",
                  [("Bright", "\"hey\", like a call"), ("Light", "\"hoo\", like an owl")]),
            warmup("brr"),
            selfcheck("\"Hey\", then \"hoo\" on the same note: hear them.", model, ["Did the \"hoo\" stay light?"]),
            play("Bright, then light, on three notes.", ex(notes), CALLS),
        ],
    }


def b_3_lighter():
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "hey"}, {"beat": 2, "length": 1.5, "step": 4, "lyric": "hoo"}]
    notes = []
    for k in range(3):
        notes += [call("hey", 0, k * 6, 1), {"beat": k * 6 + 2, "length": 1.5, "step": 4, "lyric": "hoo"}]
    return {
        "id": "belting-3-lighter", "title": EN("Lighter higher"),
        "fact": fact("titze-belt-top", "The highest belt note for women is usually around C5, Ingo Titze explains: the point where the voice can no longer keep its bright resonance above the note, and it flips.",
                     "Titze, Belting and a High Larynx Position, Journal of Singing (2007)", "https://www.nats.org/_Library/Science_Informed_Voice_Pedagogy_Resource/Article_Titze_Belting_and_a_High_Larynx_JOS-063-5-2007-557_1_.pdf"),
        "steps": [
            first("When a note won't stay bright and easy, let it go lighter, or let it flip. That's your voice telling you where today's top is.",
                  [("The call", "\"hey\", in the middle"), ("Higher, light", "\"hoo\", never the call word up there")]),
            warmup("hoo"),
            selfcheck("\"Hey\", then \"hoo\" higher: hear them.", model, ["Did the high one stay light, or did it get heavy?"]),
            play("A call, then a light \"hoo\" higher, three times. A flip on the \"hoo\" is fine.", ex(notes, generous=True), CALLS),
        ],
    }


def b_3_challenge():
    model = [{"beat": 0, "length": 2, "step": 0, "lyric": "hey"}]
    return {
        "id": "belting-3-challenge", "title": EN("Holds and letting go"), "challenge": True,
        "steps": [
            first("Two short holds, then the light voice above, which this time ends the lesson.",
                  [("Then and now", "Lesson 1's call"), ("Holds, then light", "The last note is the light one")]),
            warmup("hoo"),
            play("Lesson 1's call.", ex(calls([[("hey!", 2), ("", -1)]] * 3, "oo"), thenAndNow="belting.first-call"), CALLS),
            selfcheck("A held \"hey\": hear it.", model, ["Which sounded easier, then or now?"]),
            play("\"Hey\" and \"yeah\" held, each with its light \"hoo\" above.", ex(calls([[("hey", 0, 2)], [("yeah", 2, 2)]], "hoo"), generous=True), CALLS),
        ],
    }


# ---- Unit 4: Calls in songs (the light tail: a trill) ----

SPIRITUAL = ("Wade in the Water is a spiritual: a sacred song made by enslaved Black Americans, printed by the Fisk Jubilee Singers. "
             "It's sung many ways, by congregations, concert choirs and gospel singers; here you borrow one line, at speaking volume, as a way in.")


def b_4_heyho():
    model = [{"beat": 0, "length": 2, "step": 2, "lyric": "Hey"}, {"beat": 2, "length": 2, "step": 0, "lyric": "ho"}]
    return {
        "id": "belting-4-heyho", "title": EN("Hey, ho"),
        "steps": [
            first("Hey, Ho, Nobody Home is a round printed in 1609: every voice sings the same tune, coming in one after another. Its \"Hey, ho\" is a call.",
                  [("Hey, ho", "A call, falling"), ("Nobody home", "Easy, down to the end")]),
            warmup("brr"),
            selfcheck("\"Hey, ho\": hear it back.", model, ["Did your call sit with the other voice, or stick out above it?"]),
            play("\"Hey, ho, nobody home\", twice, with the round's next voice, then a light trill.",
                 song_line("hey-ho-nobody-home", 0, partners=("alto",), light="brr"), CALLS),
        ],
    }


def b_4_haul():
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "Way,"}, {"beat": 1, "length": 1, "step": 2, "lyric": "haul"}, {"beat": 2, "length": 2, "step": -3, "lyric": "away"}]
    return {
        "id": "belting-4-haul", "title": EN("Way, haul away"),
        "steps": [
            first("Sailors hauled a rope to a shanty: the shantyman sang a line, and the crew answered together. Their answer is a call: \"Way, haul away\".",
                  [("The crew's answer", "Bright, together, short"), ("Not a shout", "A crew works all day")]),
            warmup("brr"),
            selfcheck("\"Way, haul away\": hear it back.", model, ["Did your call sit with the crew, or stick out above it?"]),
            play("\"Way, haul away\", with the crew's other voices, then a light trill.",
                 song_line("haul-away-joe", 1, count=4, partners=("alto", "tenor", "bass"), light="brr"), CALLS),
        ],
    }


def b_4_wade():
    model = [{"beat": 0, "length": 1.25, "step": -1, "lyric": "Wade"}, {"beat": 1.25, "length": 0.5, "step": 2, "lyric": "in"}, {"beat": 1.75, "length": 0.25, "step": 1, "lyric": "the"},
             {"beat": 2, "length": 0.5, "step": 2, "lyric": "wa-"}, {"beat": 2.5, "length": 0.5, "step": -1, "lyric": "ter,"}]
    return {
        "id": "belting-4-wade", "title": EN("Wade in the water"),
        "steps": [
            first(SPIRITUAL, [("One line", "\"Wade in the water,\""), ("At speaking volume", "A call that invites, never a shout")], visual="harmony"),
            warmup("brr"),
            selfcheck("\"Wade in the water\": hear it back.", model, ["Did it sound like an invitation, easy and bright?"]),
            play("\"Wade in the water,\" with the other voices, then a light trill. Once is enough.",
                 song_line("wade-in-the-water", 0, partners=("alto", "tenor", "bass"), light="brr", until=4), CALLS),  # the bass finishes its bar (the arranger)
        ],
    }


def b_4_challenge():
    model = [{"beat": 0, "length": 1, "step": 2, "lyric": "hey!"}, {"beat": 1, "length": 1, "step": -1}]
    return {
        "id": "belting-4-challenge", "title": EN("Your calls"), "challenge": True,
        "steps": [
            first("Lesson 1's call beside today's, then the round, with another voice coming in.",
                  [("Then and now", "Which is easier?"), ("The round", "Hey, ho, nobody home")]),
            warmup("brr"),
            play("Lesson 1's call.", ex(calls([[("hey!", 2), ("", -1)]] * 3, "oo"), thenAndNow="belting.first-call"), CALLS),
            selfcheck("Hear both back.", model, ["Which sounded easier, then or now?"]),
            play("\"Hey, ho, nobody home\", with the round's next voice.", song_line("hey-ho-nobody-home", 0, partners=("alto",), light="brr"), CALLS),
        ],
    }


course = {
    "id": "belting", "version": 1, "reviewed": False, "title": EN("First steps to belting"),
    "units": [
        {"id": "belting-calls", "title": EN("Calls from speech"), "colour": 6, "lessons": [b_1_call(), b_1_onset(), b_1_easy(), b_1_challenge()]},
        {"id": "belting-phrases", "title": EN("Say it, then sing it"), "colour": 6, "lessons": [b_2_phrase(), b_2_come(), b_2_twang(), b_2_challenge()]},
        {"id": "belting-holds", "title": EN("Short holds, and letting go"), "colour": 6, "lessons": [b_3_hold(), b_3_colours(), b_3_lighter(), b_3_challenge()]},
        {"id": "belting-songs", "title": EN("Calls in songs"), "colour": 6, "lessons": [b_4_heyho(), b_4_haul(), b_4_wade(), b_4_challenge()]},
    ],
}
if FEATURES:
    course["dailyCap"] = {"minutes": 10}
if GAME:
    course["game"] = {"replayXp": False, "combo": False, "streak": False, "meter": "plain"}
    next(l for u in course["units"] for l in u["lessons"] if l["id"] == "belting-4-wade")["quiet"] = True

for where in add_breaths(course):
    print("no room to breathe:", where)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"), ensure_ascii=False)
