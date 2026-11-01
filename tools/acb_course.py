"""A cappella bass (docs/courses/a-cappella-bass.md in the app's repo): writes
course/plus/a-cappella-bass/course.json. Every step counts from the singer's comfortable note (0);
the four chords' roots are do 0, la below -3, fa below -7 and so below -5, and nothing goes lower
than fa below. The group above you is three guide voices (partner lines). Breaths a beginner can
take are written in by tools/breaths.py before the file is written.

    python3 -I tools/acb_course.py && python3 -I tools/coursefmt.py course/plus/a-cappella-bass/course.json
"""
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/a-cappella-bass/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402


def EN(text):
    return {"en": text}


ROOT = {"I": 0, "vi": -3, "IV": -7, "V": -5}
# The group's three voices over each chord (steps from the comfortable note), voiced close above you.
UPPER = {"I": (4, 7, 12), "vi": (4, 9, 12), "IV": (5, 9, 12), "V": (2, 7, 11)}
FOUR = ["I", "vi", "IV", "V"]
SAFETY = "Low and easy: never press, growl or tuck your chin to reach a note. Keep your throat where it is when you speak. If it rumbles or tickles, sing it higher: the app follows."
SHORT_SAFETY = "Low and easy, never pressed."
VOLUME = 0.5


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, listen=None, visual="bass"):
    step = {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}
    if listen:
        step["listen"] = listen
    return step


def note(beat, length, step, lyric=None):
    n = {"beat": beat, "length": length, "step": step}
    if lyric:
        n["lyric"] = lyric
    return n


def group(chords, start=0, beats=2, skip=()):
    """The three guide voices: one held "oo" chord per entry of `chords`, `beats` long, from `start`;
    `skip` names chord indexes the group sits out (the bass carries on alone)."""
    lines = [[], [], []]
    for k, name in enumerate(chords):
        if k in skip:
            continue
        for v in range(3):
            lines[v].append(note(start + k * beats, beats, UPPER[name][v], "oo"))
    return [{"notes": line, "volume": VOLUME} for line in lines]


def roots(chords, start=0, beats=2, lyric="doo", length=None):
    return [note(start + k * beats, length or beats, ROOT[name], lyric) for k, name in enumerate(chords)]


def play(text, exercise, measures, kind="play"):
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def fact(fid, text, source, url, distinct=None):
    f = {"id": fid, "text": EN(text), "source": EN(source), "url": url}
    if distinct:
        f["distinct"] = distinct
    return f


PITCH_BEAT = "Scored on your notes on pitch and on the beat."

# ---- Unit 1: The floor ----

def acb_1_root():
    hear = {"tempo": 80, "notes": [note(4, 4, 0, "doo")], "turn": False, "with": group(["I"], 0, 8)}
    line = {"tempo": 80, "notes": roots(FOUR, 0), "turn": False, "with": group(FOUR, 0)}
    return {
        "id": "acb-1-root", "title": EN("Under the group"), "strictness": "relaxed",
        "fact": fact("rameau-fundamental-bass", "Rameau's Treatise on Harmony (Paris, 1722) built harmony on the bass. Its 1779 London translation puts the \"grand Art or Mystery in Composition\" \"in the Bass, which we call Fundamental\".",
                     "Rameau, A Treatise of Music (London, 1779)", "https://archive.org/details/traitdelharmon00rame", ["otj-bernstein-berlin"]),
        "steps": [
            learn("The bass sings the chord's root, the note it's named after, and the whole group stands on it. Listen: a chord with no floor, then with one.",
                  [("The root", "The note at the bottom of the chord"), ("Under the group", "Three voices above, you underneath"), ("Low and easy", SAFETY)], hear),
            play("Sing the four chords' roots on \"doo\", with the guide bass singing along. Just try it.", line, None, kind="try"),
            play(f"Now on your own: hear the line, then sing it under the group. {SHORT_SAFETY}",
                 dict(line, turn=True, keep="acb.first-line", generous=True),
                 "Scored on your notes on pitch and on the beat. Listen back: does the chord sound solid now?"),
        ],
    }


def acb_1_low():
    # Down to fa, a breath at the bottom, then back up: two lines of about 5 seconds.
    notes = [note(0, 2, 0, "doo")] + [note(2 + k, 1, s, "doo") for k, s in enumerate([-1, -3, -5, -7])]
    notes += [note(7 + k, 1, s, "doo") for k, s in enumerate([-5, -3, -1])] + [note(10, 2, 0, "doo")]
    ex = {"tempo": 72, "notes": notes, "turn": True, "drone": {"step": 0}}
    return {
        "id": "acb-1-low", "title": EN("Low and easy"), "strictness": "relaxed",
        "steps": [
            learn("A bass's low notes come from ease, not effort. They're quieter than your middle notes, and that's right: the mic does the work.",
                  [("Step down", "Do, ti, la, so, fa, one at a time"), ("Hold only do", "The low notes are short"), ("Easy throat", "Where it sits when you speak")]),
            play("Try it slowly with the guide, down to fa and back.", dict(ex, turn=False), None, kind="try"),
            play(f"Now on your own: down by step and back, holding do at each end. {SHORT_SAFETY}", ex,
                 "Scored on your notes on pitch, and do held on its note at each end."),
        ],
    }


def chord_clip(bass, upper, key=0):
    """A clip of a bass under two upper notes, all at once."""
    return {"notes": [note(0, 3, bass + key)] + [note(0, 3, u + key) for u in upper]}


def acb_1_hear():
    rounds = []
    for k, (key, minor_first) in enumerate([(0, False), (2, True), (-3, False), (5, True), (-2, True), (3, False)]):
        major, minor = chord_clip(-12, (0, 4), key), chord_clip(-15, (0, 4), key)
        clips = [minor, major] if minor_first else [major, minor]
        ask_minor = k % 2 == 1
        answer = (0 if minor_first else 1) if ask_minor else (1 if minor_first else 0)
        rounds.append({"prompt": EN("Which one is darker, sadder (minor)?" if ask_minor else "Which one is bright (major)?"),
                       "clips": clips, "answer": answer,
                       "why": EN("The top two notes never move. Only the bass changed, and it decided the chord.")})
    sing = {"tempo": 72, "notes": [note(0, 4, -3, "doo")], "turn": False, "with": group(["vi"], 0, 4)}
    return {
        "id": "acb-1-hear", "title": EN("Bright or dark?"),
        "fact": fact("bass-overtones-chord", "A sung bass note is a stack of overtones, and two of them, the third and fifth harmonics, are notes of its own major chord. That's part of why a chord sounds built on its bass.",
                     "UNSW, Physics of music: chords and harmonics", "https://newt.phys.unsw.edu.au/jw/chords.html"),
        "steps": [
            learn("The same notes on top can make a bright chord or a dark one. The bass decides.",
                  [("Two notes on top", "They never move"), ("A new bass", "And the chord changes"), ("Then you", "Sing the root of a dark chord")], visual="harmony"),
            {"kind": "choose", "text": EN("Listen to each, as often as you like, then choose."), "exercise": {"tempo": 60, "rounds": rounds},
             "measures": EN("Scored on the rounds you got right first time.")},
            play("Now be the bass that makes it dark: hold la, the root, under the group.", sing, PITCH_BEAT),
        ],
    }


def acb_1_challenge():
    first = {"tempo": 80, "notes": roots(FOUR, 0) + roots(FOUR, 9), "turn": False, "with": group(FOUR, 0) + group(FOUR, 9)}
    order = ["I", "IV", "V", "I"]
    second = {"tempo": 92, "notes": roots(order, 0), "turn": False, "guide": False, "with": group(order, 0), "thenAndNow": "acb.first-line"}
    return {
        "id": "acb-1-challenge", "title": EN("The four chords"), "challenge": True,
        "steps": [
            learn("Twice through the four chords with the guide, then a new order with no guide bass: find each root by ear.",
                  [("With the guide", "The line you know, twice"), ("On your own", "Do, fa, so, do, a little quicker"), ("Listen up", "The group's chord tells you the root")]),
            play("Twice through with the guide bass, a breath between.", first, PITCH_BEAT),
            play("Now no guide bass, and a new order: I, IV, V, I. Find each root under the group.", second,
                 "Scored on your notes on pitch and on the beat, found by ear."),
        ],
    }

# ---- Unit 2: Bass syllables ----

def acb_2_doom():
    steady = {"notes": [note(0, 2, 0)], "drone": {"step": -12}}
    late = {"notes": [note(0, 2.7, 0)], "drone": {"step": -12}}
    rounds = [{"prompt": EN("Which doom stopped on the beat?"), "clips": [c, d], "answer": a, "why": EN(w)}
              for c, d, a, w in [(steady, late, 0, "A stops on beat 3. B hangs on past it."),
                                 (late, steady, 1, "B stops on time; A runs over."),
                                 (steady, late, 0, "A lands its stop on the beat.")]]
    notes = []
    for k, name in enumerate(FOUR):
        notes.append(note(k * 4, 2, ROOT[name], "doom"))
    ex = {"tempo": 80, "notes": notes, "turn": False, "with": group(FOUR, 0, 4), "score": "release"}
    return {
        "id": "acb-2-doom", "title": EN("Doom"),
        "steps": [
            learn("\"Doom\" is \"doo\" closing to a hum. A bass's long note is only as good as its stop.",
                  [("Doo, then m", "Lips close, the hum goes on"), ("Then stop", "The hum ends on the beat"), ("A rest", "Two beats of quiet")]),
            {"kind": "choose", "text": EN("Listen to each, then choose."), "exercise": {"tempo": 80, "rounds": rounds},
             "measures": EN("Scored on the rounds you got right first time.")},
            play("\"Doom\" on each root for two beats, then rest. Close to m, then stop the hum on beat 3.", ex,
                 "Scored on stopping each note on time, steady to its end."),
        ],
    }


def acb_2_dm():
    one = {"tempo": 88, "notes": [note(k, 0.5, 0, "dm") for k in range(8)], "turn": False, "drone": {"step": 0}}
    four = {"tempo": 88, "notes": [note(c * 4 + k, 0.5, ROOT[name], "dm") for c, name in enumerate(FOUR) for k in range(3)],
            "turn": False, "with": group(FOUR, 0, 4)}
    model = {"tempo": 88, "model": {"notes": [note(k, 0.5, 0, "dm") for k in range(4)]},
             "questions": [EN("Did your lips close before the note, with no scoop up to it?"), EN("Were your teeth apart inside the hum?")]}
    return {
        "id": "acb-2-dm", "title": EN("Dm dm"),
        "steps": [
            learn("\"Dm\" is the bass's drum: a light tap of the tongue, then a short hum with lips closed and teeth apart.",
                  [("A tap", "The tongue, light, behind the teeth"), ("A hum", "Lips closed, teeth apart"), ("On the beat", "Exactly, every time")]),
            play("\"Dm\" on every beat, on do.", one, PITCH_BEAT),
            play("Now three \"dm\"s on each chord's root, a rest on beat 4, under the group.", four, PITCH_BEAT),
            {"kind": "selfcheck", "text": EN("Four more, then hear yours beside the guide's."), "exercise": model},
        ],
    }


def call(pattern, chord, start=0):
    return [note(start + b, length, ROOT[chord] + up, lyric) for b, length, up, lyric in pattern]


DOOM_DM = [(0, 2, 0, "doom"), (2, 0.5, 0, "dm"), (3, 0.5, 0, "dm")]
BUH = [(0, 1, 0, "buh"), (1, 0.5, 0, "buh"), (1.5, 0.5, 0, "buh"), (2, 1, 0, "buh")]


def acb_2_buh():
    calls = [(DOOM_DM, "I"), (BUH, "vi"), (DOOM_DM, "IV"), (BUH, "V")]
    steps = [learn("Call and response: the guide sings a bar, and you sing it straight back. \"Buh\" is lips just touching, with no puff of air.",
                   [("Listen", "One bar from the guide"), ("Answer", "The same bar, on the same root"), ("Buh", "Lips just touching, no puff")])]
    for k, (pattern, chord) in enumerate(calls[:3]):
        ex = {"tempo": 88, "notes": call(pattern, chord) + call(pattern, calls[k + 1][1], 4), "turn": True, "with": group([chord, calls[k + 1][1]], 0, 4)}
        steps.append(play(f"Call {k + 1}: listen, then answer.", ex, PITCH_BEAT))
    return {
        "id": "acb-2-buh", "title": EN("Call and response"),
        "fact": fact("fisk-1872-basses", "The first Fisk Jubilee Singers had as many basses as tenors: their 1872 songbook names two basses, Isaac P. Dickerson and Greene Evans.",
                     "Jubilee Songs, as sung by the Jubilee Singers of Fisk University (1872)", "https://archive.org/details/jubileesongsassu00jubi", ["swing-low-fisk-1872"]),
        "steps": steps,
    }


def acb_2_challenge():
    notes = []
    for k, name in enumerate(FOUR):
        notes += call([(0, 2, 0, "doom")], name, k * 4)
    for k, name in enumerate(FOUR):
        notes += call([(0, 0.5, 0, "dm"), (1, 0.5, 0, "dm"), (2, 0.5, 0, "dm")], name, 17 + k * 4)
    ex = {"tempo": 88, "notes": notes, "turn": False, "with": group(FOUR, 0, 4) + group(FOUR, 17, 4), "thenAndNow": "acb.first-line"}
    return {
        "id": "acb-2-challenge", "title": EN("Talk like a bass"), "challenge": True,
        "steps": [
            learn("Unit 1's four roots, now in bass syllables: \"doom\" once through, then \"dm\" three to a chord.",
                  [("Doom", "Stop each one on time"), ("Then dm", "Exactly on the beat"), ("Then and now", "Hear lesson 1 beside today")]),
            play("Once with the guide, to learn it.", {k: v for k, v in ex.items() if k != "thenAndNow"}, None, kind="try"),
            play("Now the whole groove under the group.", ex, PITCH_BEAT),
        ],
    }

# ---- Unit 3: Root and fifth ----

FIFTH = {"I": -5, "vi": 4, "IV": 0, "V": 2}  # each root's fifth, up wherever down would pass fa below


def groove(chords, start=0, lyric="dm", rest_last=True):
    notes = []
    for k, name in enumerate(chords):
        b = start + k * 4
        notes += [note(b, 1, ROOT[name], lyric), note(b + 1, 1, FIFTH[name], lyric), note(b + 2, 1, ROOT[name], lyric)]
        if not rest_last:
            notes.append(note(b + 3, 1, FIFTH[name], lyric))
    return notes


def acb_3_fifth():
    held = {"tempo": 84, "notes": [note(k, 1, 0 if k % 2 == 0 else -5, "dm") for k in range(7)], "turn": False, "with": group(["I"], 0, 8)}
    every = {"tempo": 84, "notes": groove(FOUR), "turn": True, "with": group(FOUR, 0, 4)}
    return {
        "id": "acb-3-fifth", "title": EN("Root and fifth"),
        "steps": [
            learn("The most common bass move: the root, then the chord's fifth. On low chords the fifth goes up, so you never go below fa.",
                  [("Root", "The chord's own note"), ("Fifth", "Its fifth, up or down"), ("Back", "Home to the root")]),
            play("Do and so below, back and forth, over one chord.", held, None, kind="try"),
            play("Each chord's root and fifth: do and so, la and mi, fa and do, so and re. Listen, then sing.", every, PITCH_BEAT),
        ],
    }


def acb_3_time():
    ex = {"tempo": 84, "notes": groove(FOUR), "turn": False, "with": group(FOUR, 0, 4, skip=(2,))}
    return {
        "id": "acb-3-time", "title": EN("Keep the time"),
        "fact": fact("seward-no-triple-time", "Writing down the Fisk Jubilee Singers' songs in 1872, Theodore Seward found none in triple time. He put it down to \"the beating of the foot and the swaying of the body\".",
                     "Jubilee Songs, as sung by the Jubilee Singers of Fisk University (1872), preface", "https://archive.org/details/jubileesongsassu00jubi", ["swing-low-fisk-1872", "fisk-1872-basses"]),
        "steps": [
            learn("The group listens to you for the beat. In bar 3 they stop, you carry on, and they come back in on your beat.",
                  [("Your groove", "Root and fifth, steady"), ("Bar 3", "Just you"), ("Bar 4", "They're back: be where they expect")]),
            play("Root and fifth under the group; keep going when they stop.", ex, PITCH_BEAT),
        ],
    }


def acb_3_hear():
    steady = {"notes": [note(k, 0.5, 0 if k % 2 == 0 else -5) for k in range(8)]}
    rushed = {"notes": [note(k - (0.15 if k in (3, 5, 7) else 0), 0.5, 0 if k % 2 == 0 else -5) for k in range(8)]}
    rounds = []
    for k in range(6):
        first_rushed = k % 2 == 0
        rounds.append({"prompt": EN("Which one rushed?"), "clips": [rushed, steady] if first_rushed else [steady, rushed],
                       "answer": 0 if first_rushed else 1, "why": EN("Some of its notes came a little early, and the groove leaned forward.")})
    ex = {"tempo": 84, "notes": groove(FOUR[:2]), "turn": False, "with": group(FOUR[:2], 0, 4)}
    return {
        "id": "acb-3-hear", "title": EN("Steady or rushing?"),
        "fact": fact("missing-fundamental-bass", "Your ear can hear a low note even when its lowest frequency is missing, from the overtones above it. That's how a small speaker still sounds a bass.",
                     "Journal of the Acoustical Society of America (2012), via PMC", "https://pmc.ncbi.nlm.nih.gov/articles/PMC3316681/"),
        "steps": [
            learn("A bass that rushes pulls the whole group forward. Hear it, then be the steady one.",
                  [("Two grooves", "One of them rushes"), ("Choose", "Which leaned forward?"), ("Then you", "The groove, steady")]),
            {"kind": "choose", "text": EN("Listen to each, as often as you like, then choose."), "exercise": {"tempo": 84, "rounds": rounds},
             "measures": EN("Scored on the rounds you got right first time.")},
            play("Now your groove, steady as a clock.", ex, PITCH_BEAT),
        ],
    }


def acb_3_challenge():
    notes = groove(FOUR, 0, "dm") + groove(FOUR, 17, "doom")
    ex = {"tempo": 84, "notes": notes, "turn": False, "with": group(FOUR, 0, 4) + group(FOUR, 17, 4), "score": "entry", "thenAndNow": "acb.first-line"}
    return {
        "id": "acb-3-challenge", "title": EN("The groove"), "challenge": True,
        "steps": [
            learn("The four chords' root and fifth with a rest on beat 4: once on \"dm\", once on unit 2's \"doom\".",
                  [("Root, fifth, root", "Then a rest"), ("Back in", "On the next downbeat, every time"), ("Then and now", "Lesson 1 beside today")]),
            play("Once with the guide, to learn it.", {k: v for k, v in ex.items() if k not in ("thenAndNow", "score")}, None, kind="try"),
            play("Now the whole groove under the group.", ex, "Scored on coming back in on time and on pitch after each rest."),
        ],
    }

# ---- Unit 4: Walking ----

def acb_4_walk():
    down = [0, -1, -3, -5, -7]
    chords = ["I", "I", "vi", "V", "IV"]
    notes = [note(k, 1, s, "doo") for k, s in enumerate(down)] + [note(5 + k, 1, s, "doo") for k, s in enumerate(reversed(down[:-1]))]
    notes[-1]["length"] = 2
    ex = {"tempo": 76, "notes": notes, "turn": True, "with": group(chords, 0, 1) + group(["V", "vi", "I", "I"], 5, 1)}
    return {
        "id": "acb-4-walk", "title": EN("Walk down"),
        "steps": [
            learn("A walking bass steps from one root to the next, landing on each chord as it changes.",
                  [("Step down", "Do, ti, la, so, fa"), ("Land", "On each new chord"), ("Walk back", "Up to do")]),
            play("Down from do to fa and back up, one step a beat. Listen, then walk.", ex, PITCH_BEAT),
        ],
    }


def acb_4_lead():
    arrivals = [(-1, "From ti, a half step below"), (2, "From re, a step above"), (-5, "From so below, the leap from V to I")]
    notes, upper_v, upper_i = [], [], []
    for k, (start, _) in enumerate(arrivals):
        b = k * 4
        notes += [note(b, 1, start, "doo"), note(b + 1, 2, 0, "doo")]
    ex = {"tempo": 76, "notes": notes, "turn": True,
          "with": [{"notes": [note(k * 4, 1, UPPER["V"][v], "oo") for k in range(3)] + [note(k * 4 + 1, 2, UPPER["I"][v], "oo") for k in range(3)], "volume": VOLUME} for v in range(3)],
          "score": "landing"}
    return {
        "id": "acb-4-lead", "title": EN("Arrive home"),
        "steps": [
            learn("A bass brings the group home: the last note lands on do, right on the downbeat.",
                  [("From ti", "A half step below"), ("From re", "A step above"), ("From so", "The leap from V to I")]),
            play("Three arrivals on do. Listen, then sing each one home.", ex, "Scored on where each note landed, and whether it slid in."),
        ],
    }


def acb_4_swing():
    song = {"template": "swing-low", "part": "bass", "phrases": [0, 1], "with": "others"}
    return {
        "id": "acb-4-swing", "title": EN("Swing Low, rehearsed"),
        "fact": fact("barbershop-chorus-bass-share", "A barbershop chorus aims for about 40 percent of its singers on bass, more than on any other part, and many go as high as half.",
                     "Barbershop Harmony Society, What is barbershop music?", "https://www.barbershop.org/music/about-our-music"),
        "steps": [
            learn("A real song now: the bass of Swing Low, Sweet Chariot, the roots under a whole group.",
                  [("Roots on oo", "Long notes, steady"), ("Under three voices", "The tune on top"), ("Balance", "The tune should float over you")], visual="harmony"),
            play("The chorus's first line, with the guide.", {"song": dict(song, phrases=[0]), "tempo": 76, "turn": False}, None, kind="try"),
            play("The chorus's first two lines, under the other parts.", {"song": song, "tempo": 76, "turn": False},
                 "Scored on your notes on pitch and on the beat. Listen back: could you hear the top voice over you?"),
        ],
    }


def acb_4_challenge():
    home = [-5, -3, -1, 0]
    line = roots(FOUR, 0) + [note(8 + k, 1, s, "doo") for k, s in enumerate(home)]
    line[-1]["length"] = 2
    ex = {"tempo": 80, "notes": line, "turn": False, "with": group(FOUR[:3], 0), "score": "keyDrift", "thenAndNow": "acb.first-line"}
    return {
        "id": "acb-4-challenge", "title": EN("The floor"), "challenge": True,
        "steps": [
            learn("Everything at once: lesson 1's line, the walk home, the key held on your own, then Swing Low's bass in Sing.",
                  [("The line", "And the walk home: so, la, ti, do"), ("On your own", "The group drops out: hold the key"), ("Then Sing", "Your bass under a whole song")]),
            play("Lesson 1's line and the walk home. The group drops out for the last bars: keep the key.", ex,
                 "Scored on your intervals and on holding the key on your own."),
            {"kind": "record", "text": EN("The finale: record Swing Low's bass in Sing, over the three guides. Add the other parts too if you like."),
             "template": "swing-low", "singers": 4, "part": "bass", "measures": EN("Scored on the notes of your bass.")},
        ],
    }


course = {
    "id": "a-cappella-bass", "version": 1, "reviewed": False, "title": EN("A cappella bass"),
    "units": [
        {"id": "acb-the-floor", "title": EN("The floor"), "colour": 3, "lessons": [acb_1_root(), acb_1_low(), acb_1_hear(), acb_1_challenge()]},
        {"id": "acb-bass-syllables", "title": EN("Bass syllables"), "colour": 3, "lessons": [acb_2_doom(), acb_2_dm(), acb_2_buh(), acb_2_challenge()]},
        {"id": "acb-root-and-fifth", "title": EN("Root and fifth"), "colour": 3, "lessons": [acb_3_fifth(), acb_3_time(), acb_3_hear(), acb_3_challenge()]},
        {"id": "acb-walking", "title": EN("Walking"), "colour": 3, "lessons": [acb_4_walk(), acb_4_lead(), acb_4_swing(), acb_4_challenge()]},
    ],
}
for where in add_breaths(course):
    print("no room to breathe:", where)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"))
