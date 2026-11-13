"""Gospel and soul runs (docs/courses/gospel-runs.md in the app's repo): writes
course/plus/gospel-runs/course.json. Every line counts from the singer's comfortable note (0). Runs are
built from a key's pentatonic and placed on a held word; the songs' lines come from the library's
own templates (public-domain spirituals), slowed to 60 to the quarter for practice, with our runs
marked as ours. Breaths are checked by tools/breaths.py before the file is written.

    python3 -I tools/gr_course.py && python3 -I tools/coursefmt.py course/plus/gospel-runs/course.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/gospel-runs/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

BANNED = re.compile(r"\b(stars?|starring|grit|gritty|preach\w*|hallelujah)\b", re.I)
SAFETY = "Runs need a light voice: a medium volume, the middle of your voice, no pushing. The run happens in the voice, not the jaw. Stop if anything tightens."
TEMPO = 60
MAJOR = (0, 2, 4, 7, 9)   # do re mi so la
MINOR = (0, 3, 5, 7, 10)  # the minor pentatonic: do, flat three, four, five, flat seven
RANGE = 9


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


def choose(text, rounds, tempo=TEMPO):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


def selfcheck(text, model, questions, tempo=TEMPO):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


CLEAN = "Scored on landing each note cleanly, not sliding into it."
PITCH = "Scored on every note on pitch."


def scale(pcs, low=-RANGE, high=RANGE):
    return [s for s in range(low, high + 1) if s % 12 in pcs]


def run_down(target, pcs, count, start, each=0.5, last=1.0, word="A-"):
    """`count` scale notes above `target`, stepping down to it: each `each` beats, the target `last`."""
    above = [s for s in scale(pcs, target + 1, target + 12)][:count]
    steps = list(reversed(above)) + [target]
    notes = [{"beat": start + k * each, "length": each, "step": s} for k, s in enumerate(steps[:-1])]
    notes.append({"beat": start + len(steps[:-1]) * each, "length": last, "step": target})
    notes[0]["lyric"] = word
    return notes


def turn(target, pcs, start, each=0.5, last=1.0, word="oh"):
    up = min(s for s in scale(pcs, target + 1, target + 12))
    down = max(s for s in scale(pcs, target - 12, target - 1))
    steps = [up, target, down, target]
    notes = [{"beat": start + k * each, "length": each if k < 3 else last, "step": s} for k, s in enumerate(steps)]
    notes[0]["lyric"] = word
    return notes


def chords(*spec):
    """[(beat, root step, quality)] as chords."""
    return [{"beat": b, "root": r, "quality": q, "bass": None} for b, r, q in spec]


# ---- Songs from the library, laid from the comfortable note ----

def tune(template, phrase, ref):
    d = json.loads((REPO / f"templates/library/{template}.json").read_text())
    mel = next(p for p in d["parts"] if p.get("melody"))
    a, b = d["sections"][0]["phrases"][phrase]
    out = []
    for n in mel["guide"]["notes"]:
        if a - 1e-6 <= n["beat"] < b - 1e-6:
            note = {"beat": round(n["beat"] - a, 4), "length": n["length"], "step": n["pitch"] - ref}
            if n.get("lyric"):
                note["lyric"] = n["lyric"]
            out.append(note)
    return out


def with_run(line, word, run_fn):
    """The line with its held note on `word` replaced by a run ending on that note's pitch."""
    k = next(i for i, n in enumerate(line) if (n.get("lyric") or "").lower().startswith(word))
    held = line[k]
    run = run_fn(held["step"], held["beat"], held["length"])
    lyric = held.get("lyric")
    run[0]["lyric"] = lyric
    for n in run[1:]:
        n.pop("lyric", None)
    return line[:k] + run + line[k + 1:]


SWING_REF, SWING_KEY = 71, 7   # Swing Low (G): B4 on your note; the key's do is G
STEAL_REF, STEAL_KEY = 65, 5   # Steal Away (F): F4 on your note
WADE_REF, WADE_KEY = 68, 5     # Wade in the Water (F minor): A flat 4 on your note


def rel(pcs, key, ref):
    """A key's pentatonic as pitch classes relative to the step 0 of a line laid from `ref`."""
    return tuple((p + key - ref) % 12 for p in pcs)


# ---- Unit 1: Five stairs ----

FIVE = [{"beat": k * 0.5, "length": 0.5, "step": s} for k, s in enumerate([9, 7, 4, 2])] + [{"beat": 2, "length": 2, "step": 0}]
FIVE[0]["lyric"] = "A-"
FIVE[-1]["lyric"] = "men."


def five_stairs(**extra):
    ex = {"tempo": TEMPO, "notes": [dict(n) for n in FIVE], "turn": False, "score": "landing",
          "chords": chords((0, -7, "maj"), (2, -12, "maj"))}
    ex.update(extra)
    return ex


def gr_1_stairs():
    hum = [dict(n, lyric=None) for n in FIVE]
    for n in hum:
        n.pop("lyric")
    hum[0]["lyric"] = "mm"
    return {
        "id": "gr-1-stairs", "title": EN("Five stairs"), "strictness": "relaxed",
        "fact": fact("amen-cadence", "A move from chord IV to home, I, is called the plagal or Amen cadence, after the \"Amen\" so often sung to it in hymns. It has long been a favourite close in church music.", "Baker, A Dictionary of Musical Terms (1907), \"Cadence\"", "https://archive.org/details/dictionaryofmusi1907bake"),
        "steps": [
            learn("A run is a few notes on one syllable, each one clean, like stairs. The spirituals were made by enslaved Black Americans as sacred songs, and gospel grew from them in Black churches: here a run serves the word.",
                  [("One syllable", "Several clean notes"), ("One run a line", "On a held word; the tune comes first"), ("Light", SAFETY)]),
            play("Hum the run slowly: five notes stepping down to do, the home note (la, so, mi, re, do). Each waits until you find it.", {"tempo": TEMPO, "notes": hum, "turn": False, "chords": chords((0, -7, "maj"), (2, -12, "maj"))}, None, kind="try"),
            play("Now \"A-men\": the run on \"A-\", landing \"men\" on do. With headphones, you'll hear the chord come home under it.", five_stairs(keep="gr.first-run", generous=True), CLEAN),
        ],
    }


def pent_clip(only_five):
    steps = [0, 2, 4, 7, 9] if only_five else [0, 2, 4, 5, 7]
    return {"notes": [{"beat": k * 0.5, "length": 0.5, "step": s} for k, s in enumerate(steps)]}


def gr_1_scale():
    rounds = [{"prompt": EN("Which run used only the five notes?"), "clips": [pent_clip(f), pent_clip(not f)], "answer": 0 if f else 1,
               "why": EN("The five are do, re, mi, so and la. The other run used fa.")} for f in (True, False, True)]
    steps = [0, 2, 4, 7, 9, 7, 4, 2, 0]
    notes = [{"beat": k * 0.5, "length": 0.5, "step": s} for k, s in enumerate(steps[:-1])] + [{"beat": 4, "length": 2, "step": 0}]
    notes[0]["lyric"] = "oh"
    return {
        "id": "gr-1-scale", "title": EN("Five notes only"),
        "fact": fact("pentatonic-worldwide", "The pentatonic, a five-note scale, is one of the most widely used scales: it runs through Western folk and popular music and is the basic scale of much East Asian music.", "Gill and Purves, PLoS ONE (2009)", "https://pmc.ncbi.nlm.nih.gov/articles/PMC2779864/"),
        "steps": [
            learn("Runs are built from five notes, the major pentatonic: do, re, mi, so, la. No fa, no ti.",
                  [("Five notes", "Do, re, mi, so, la"), ("Listen", "Which run kept to them?"), ("Sing them", "Up and down, two a second")]),
            choose("Listen to each, then choose.", rounds),
            play("Up the five notes and down, two a second.", {"tempo": TEMPO, "notes": notes, "turn": False, "drone": {"step": 0}, "score": "landing"}, CLEAN),
        ],
    }


def gr_1_turn():
    notes = turn(0, MAJOR, 0) + turn(7, MAJOR, 4)
    return {
        "id": "gr-1-turn", "title": EN("A turn"),
        "fact": fact("cpe-bach-turn-abused", "In 1753 C. P. E. Bach, J. S. Bach's son, wrote that the turn fits almost anywhere and is \"for that reason often badly misused\": many think, he said, that a turn at every moment is the whole charm of playing.", "C. P. E. Bach, Essay on the True Manner of Playing the Clavier (1753), Packard Humanities Institute", "https://versuch.cpebach.org/v-html/part-I/chapter-2/section-4/I-2-4-p7.html"),
        "steps": [
            learn("The smallest run is a turn: the note above, the note, the note below, the note.",
                  [("Above", "One stair up"), ("The note", "Home"), ("Below, and back", "One stair down, then home")]),
            play("Two turns, around do and around so: listen, then echo.", {"tempo": TEMPO, "notes": notes, "turn": True, "drone": {"step": 0}}, PITCH),
        ],
    }


def steal_first():
    return tune("steal-away", 0, STEAL_REF)


def steal_with_run():
    pcs = rel(MAJOR, STEAL_KEY, STEAL_REF)
    return with_run(steal_first(), "way,", lambda t, b, l: run_down(t, pcs, 2, b, 0.5, max(0.5, l - 1.0)))


def gr_1_challenge():
    return {
        "id": "gr-1-challenge", "title": EN("A run at the end"), "challenge": True,
        "steps": [
            learn("Five stairs again, then a real line: Steal Away, sung plain first, then with a short run on its held \"way\".",
                  [("Then and now", "Five stairs, today"), ("The tune first", "Sung plain"), ("Then the run", "On the held word")]),
            play("Five stairs.", five_stairs(thenAndNow="gr.first-run"), CLEAN),
            play("\"Steal away\", sung plain.", {"tempo": TEMPO, "notes": steal_first(), "turn": False}, PITCH),
            play("Now with a short run on the held \"way\".", {"tempo": TEMPO, "notes": steal_with_run(), "turn": False, "score": "landing"}, CLEAN),
        ],
    }

# ---- Unit 2: Groups, placing, and the minor ----

def gr_2_groups():
    threes = []
    for k, top in enumerate([7, 4, 9]):
        trip = [s for s in scale(MAJOR, top - 7, top) if s <= top][::-1][:3]
        threes += [{"beat": k * 2 + j / 3, "length": round(1 / 3, 4), "step": s} for j, s in enumerate(trip)] + [{"beat": k * 2 + 1, "length": 0.5, "step": trip[-1]}]
    for g in range(0, len(threes), 4):
        threes[g]["lyric"] = "oh"
    model = threes[:4]
    return {
        "id": "gr-2-groups", "title": EN("In groups"),
        "fact": fact("bolton-clicks-group", "In 1894 the psychologist Thaddeus Bolton played people identical, evenly spaced clicks. They heard them fall into groups of two, three or four, most often with the first of each group sounding strongest.", "Bolton, Rhythm, The American Journal of Psychology (1894)", "https://archive.org/details/jstor-1410948"),
        "steps": [
            learn("Fast runs are groups of three or four, the first of each group leaned on a little: lighter, not louder.",
                  [("Threes", "Three to a beat"), ("A small lean", "On the first, not louder"), ("Echo", "Listen, then sing")]),
            play("Three groups of three: listen, then echo.", {"tempo": TEMPO, "notes": threes, "turn": True, "drone": {"step": 0}}, PITCH),
            selfcheck("Once more, then hear yours beside the guide's.", model, ["Did the lean stay light, not louder?", "Did your jaw stay still?"]),
        ],
    }


def clean_clip(kind):
    steps = [9, 7, 4, 2, 0]
    notes = []
    for k, s in enumerate(steps):
        n = {"beat": k * 0.5, "length": 0.5 if kind != "choppy" else 0.3, "step": s}
        if kind == "smeared" and k < 4:
            n["bend"] = [[0, 0], [0.25, 0], [0.5, (steps[k + 1] - s) * 100]]
        notes.append(n)
    return {"notes": notes}


def gr_2_clean():
    order = [("clean", "smeared"), ("choppy", "clean"), ("clean", "choppy"), ("smeared", "clean"), ("clean", "smeared"), ("choppy", "clean")]
    rounds = [{"prompt": EN("Which run kept its notes clean and joined?"), "clips": [clean_clip(a), clean_clip(b)], "answer": 0 if a == "clean" else 1,
               "why": EN("Clean is each note separate but joined. Smeared slides between them; choppy breaks them apart with breath.")} for a, b in order]
    return {
        "id": "gr-2-clean", "title": EN("Clean, smeared or choppy?"),
        "fact": {**fact("tosi-ha-ha-ha", "In 1723 the singing teacher Pier Francesco Tosi wanted a run's notes \"not too much join'd, nor too much mark'd\". A student who marked them \"with the Tongue, or with the Chin\" was to be corrected.", "Tosi, Observations on the Florid Song, tr. Galliard (1743), Project Gutenberg", "https://www.gutenberg.org/ebooks/26477"), "distinct": ["tosi-seldom-prodigy"]},
        "steps": [
            learn("A clean run keeps each note separate but joined. A smeared one slides; a choppy one breathes between notes, \"ha-ha-ha\".",
                  [("Clean", "Separate and joined"), ("Smeared", "Sliding together"), ("Choppy", "Breathy gaps")]),
            choose("Listen to each, then choose.", rounds),
            play("Now yours, clean.", five_stairs(), CLEAN),
        ],
    }


def place_clip(good):
    notes = [{"beat": 0, "length": 1, "step": 0}, {"beat": 1, "length": 1, "step": 2}, {"beat": 2, "length": 1, "step": 4}]
    if good:
        notes += run_down(0, MAJOR, 3, 3, 0.5, 1.0)
    else:
        notes = [n for k, x in enumerate([0, 2, 4]) for n in run_down(x, MAJOR, 1, k * 1.5, 0.5, 1.0)]
    for n in notes:
        n.pop("lyric", None)
    return {"notes": notes}


def gr_2_place():
    rounds = [{"prompt": EN("Which line places its run well?"), "clips": [place_clip(g), place_clip(not g)], "answer": 0 if g else 1,
               "why": EN("One run, at the end, on the held note. Runs on every note hide the tune.")} for g in (True, False, True)]
    return {
        "id": "gr-2-place", "title": EN("Where a run goes"),
        "steps": [
            learn("One run a line, on a held word, usually at its end. The tune comes first.",
                  [("The tune", "Sung plain"), ("One run", "Not on every word"), ("On a held word", "Where there's time")]),
            choose("Listen to each, then choose.", rounds),
            play("\"Steal away\" with one run, on its held word.", {"tempo": TEMPO, "notes": steal_with_run(), "turn": False, "score": "landing"}, CLEAN),
        ],
    }


def wade_line():
    return tune("wade-in-the-water", 0, WADE_REF)


def gr_2_challenge():
    pcs = rel(MINOR, WADE_KEY, WADE_REF)
    line = wade_line()
    k = len(line) - 1
    end = line[k]
    run = run_down(end["step"], pcs, 3, end["beat"], 0.25, 1.0, word=end.get("lyric") or "oh")
    ran = line[:k] + run
    return {
        "id": "gr-2-challenge", "title": EN("Wade in the Water"), "challenge": True,
        "fact": fact("lining-out", "In lining out, a leader chants a line and the congregation answers with a much longer, more decorated tune. African American congregations, mostly Baptists in the rural South, still keep the tradition.", "Titon, Smithsonian Folklife Festival program (1997)", "https://folklife-media.si.edu/docs/festival/program-book-articles/FESTBK1997_25.pdf"),
        "steps": [
            learn("Five stairs again, then Wade in the Water: a minor song (darker, its third a half step lower), with a minor run in fours (In groups).",
                  [("Then and now", "Five stairs, today"), ("Minor", "The darker five notes"), ("In fours", "A small lean on the first")]),
            play("Five stairs.", five_stairs(thenAndNow="gr.first-run"), CLEAN),
            play("\"Wade in the water\", plain.", {"tempo": TEMPO, "notes": line, "turn": False}, PITCH),
            play("Now ending in a minor run, in fours.", {"tempo": TEMPO, "notes": ran, "turn": False}, PITCH),
        ],
    }

# ---- Unit 3: The blue note ----

def bend(start=3, end=4, seconds=3):
    return {"tempo": TEMPO, "step": 0, "lyric": "oh", "combo": False,
            "target": [{"seconds": seconds, "kind": "path", "band": 60, "points": [[0, start], [1.0, end], [seconds, end]]}]}


def gr_3_bend():
    return {
        "id": "gr-3-bend", "title": EN("Bend up"),
        "fact": fact("rhapsody-clarinet-slide", "The clarinet slide that opens Rhapsody in Blue wasn't in the score. Gershwin wrote a trill and a plain scale; in rehearsal Ross Gorman slid up it instead, to Gershwin's delight.", "Farrington, \"Rhapsody in Blue\", National Recording Registry essay, Library of Congress", "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/RhapsodyInBlue.pdf"),
        "steps": [
            learn("The blue note sits between the piano's keys, between the minor and major third, nearer the minor. Start there, loose, and bend up to the third: the arrival is what matters.",
                  [("Start low", "Between the keys"), ("Bend up", "Slowly, lightly"), ("Arrive", "And hold the third")], visual="vibrato"),
            {"kind": "wave", "text": EN("Ride the line: from the blue note up to the third, then hold."), "exercise": bend()},
            {"kind": "wave", "text": EN("Once more, a little quicker into the third."), "exercise": bend(seconds=2.5)},
        ],
    }


def gr_3_up():
    notes = []
    for k, target in enumerate([4, 7, 2]):
        below = [s for s in scale(MAJOR, target - 7, target - 1)][-3:]
        notes += [{"beat": k * 4 + j * 0.5, "length": 0.5, "step": s} for j, s in enumerate(below)] + [{"beat": k * 4 + 1.5, "length": 1.5, "step": target}]
        notes[-4]["lyric"] = "oh"
    return {
        "id": "gr-3-up", "title": EN("Run up to it"),
        "fact": fact("slide-elevation-1654", "Baroque musicians had a name for two or three steps climbing into a note: the slide, Schleifer in German. England's John Playford, in his Introduction to the Skill of Musick, called this rising grace an \"elevation\".", "Playford, An Introduction to the Skill of Musick (1674 ed.), p. 116", "https://archive.org/details/bim_early-english-books-1641-1700_an-introduction-to-the-s_playford-john_1674"),
        "steps": [
            learn("A run can climb into a note too: three stairs up, then hold.",
                  [("Three up", "Light and clean"), ("Then hold", "The note you ran to"), ("Light", "No pushing at the top")]),
            play("Three rising runs, each into a held note.", {"tempo": TEMPO, "notes": notes, "turn": True, "drone": {"step": 0}, "score": "landing"}, CLEAN),
        ],
    }


def bend_clip(lands):
    end = 400 if lands else 330
    return {"notes": [{"beat": 0, "length": 3, "step": 0, "bend": [[0, 300], [1, end], [3, end]]}]}


def gr_3_hear():
    rounds = [{"prompt": EN("Which bend lands on the third?"), "clips": [bend_clip(l), bend_clip(not l)], "answer": 0 if l else 1,
               "why": EN("One bends up and arrives; the other stalls just short.")} for l in (True, False, True, False)]
    return {
        "id": "gr-3-hear", "title": EN("Bend or stall?"),
        "fact": fact("dorsey-kicked-out", "Thomas A. Dorsey's bluesy gospel met resistance in the churches: many pastors called it \"devil's music\". He recalled being thrown out of some of the best churches.", "PBS, This Far by Faith, \"Thomas Dorsey\"", "https://www.pbs.org/thisfarbyfaith/people/thomas_dorsey.html"),
        "steps": [
            learn("A bend has to arrive. Listen for the one that lands.",
                  [("Listen", "Which one lands?"), ("Then you", "A bend that arrives"), ("Hold it", "On the third")], visual="vibrato"),
            choose("Listen to each, then choose.", rounds),
            {"kind": "wave", "text": EN("Now your bend, arriving on the third."), "exercise": bend()},
        ],
    }


def gr_3_challenge():
    threes = [{"beat": j / 3, "length": round(1 / 3, 4), "step": s} for j, s in enumerate([7, 4, 2])] + [{"beat": 1, "length": 2, "step": 0}]
    threes[0]["lyric"] = "oh"
    return {
        "id": "gr-3-challenge", "title": EN("A bluesy ending"), "challenge": True,
        "steps": [
            learn("Five stairs again, a bend on the line, then an ending run in threes (unit 2's groups).",
                  [("Then and now", "Five stairs, today"), ("The bend", "Arrive on the third"), ("The run", "In threes, landing home")], visual="vibrato"),
            play("Five stairs.", five_stairs(thenAndNow="gr.first-run"), CLEAN),
            {"kind": "wave", "text": EN("The bend, arriving on the third."), "exercise": bend()},
            play("The ending run, in threes, landing on do.", {"tempo": TEMPO, "notes": threes, "turn": True, "drone": {"step": 0}}, PITCH),
        ],
    }

# ---- Unit 4: The ladder, and the songs ----

def gr_4_ladder():
    steps = [learn("The same run, a rung at a time: two, three, then four notes a second, each note still clean. Real runs go faster; clean first is how they're learned.",
                   [("Two a second", "Every note clean"), ("Three, then four", "As quick as each note still counts"), ("Beyond", "Real speed, just to hear")], visual="echo")]
    for k, (rate, label) in enumerate([(2, "two"), (3, "three"), (4, "four")]):
        ex = five_stairs()
        ex["tempo"] = round(60 * rate / 2)
        if rate == 4:
            ex["generous"] = True
        steps.append(play(f"The run at {label} notes a second.", ex, CLEAN if rate < 4 else "Scored on every note on pitch, generously at the top rung."))
    real = [dict(n) for n in FIVE]
    return {
        "id": "gr-4-ladder", "title": EN("The ladder"),
        "fact": fact("slow-practice", "Almost every classical musician practises slowly: in a 2022 survey of 256 musicians, 99.45 percent of the classical players did. Science hasn't yet shown exactly how it helps.", "Allingham and Wöllner, Psychology of Music (2022)", "https://doi.org/10.1177/03057356211073481"),
        "steps": steps + [selfcheck("One step further: the guide's run at real speed. Try it, then hear yours beside it. We don't score this speed yet.",
                                    real, ["Did every note stay clean?", "Did your jaw stay still?"], 240)],
    }


def swing_line():
    return tune("swing-low", 1, SWING_REF)


def gr_4_swing():
    pcs = rel(MAJOR, SWING_KEY, SWING_REF)
    ran = with_run(swing_line(), "home", lambda t, b, l: turn(t, pcs, b, 0.5, max(0.5, l - 1.5)))
    return {
        "id": "gr-4-swing", "title": EN("Swing Low, with a run"),
        "fact": fact("blue-note", "A blue note falls between the piano's keys, flatter than the major third and sharper than the minor. Measured in early blues recordings, the blue third usually sits just above the minor third.", "Cutting, Empirical Musicology Review (2019)", "https://doi.org/10.18061/emr.v13i1-2.6316"),
        "steps": [
            learn("Swing Low's line, plain, then with a turn on \"home\". The run is ours, one singer's choice: on a spiritual it serves the word.",
                  [("Plain first", "The tune as it is"), ("On home", "A turn, serving the word"), ("Then breathe", "Before \"Coming for to carry me\"")]),
            play("\"Coming for to carry me home\", plain.", {"tempo": TEMPO, "notes": swing_line(), "turn": False}, PITCH),
            play("Now with a turn on \"home\".", {"tempo": TEMPO, "notes": ran, "turn": False, "score": "landing"}, CLEAN),
        ],
    }


def gr_4_steal():
    line = tune("steal-away", 1, STEAL_REF)
    pcs = rel(MAJOR, STEAL_KEY, STEAL_REF)
    ran = with_run(line, "steal", lambda t, b, l: run_down(t, pcs, 1, b, 0.5, max(0.5, l - 0.5)))
    return {
        "id": "gr-4-steal", "title": EN("Steal Away"),
        "fact": fact("steal-away-oberlin-1871", "In November 1871 the Fisk Jubilee Singers sang Steal Away to a convention of ministers at Oberlin, Ohio. The ministers passed them from church to church toward New York, where they became a sensation.", "Oberlin Alumni Magazine (Oberlin College), Summer 2001", "https://www2.oberlin.edu/alummag/oamcurrent/oam_summer2001/profile1.html"),
        "steps": [
            learn("A quiet spiritual: one gentle run, nothing more.",
                  [("Quiet", "A medium volume or less"), ("One run", "Gentle, on a held word"), ("The word", "Comes first")]),
            play("\"Steal away to Jesus\", plain.", {"tempo": TEMPO, "notes": line, "turn": False}, PITCH),
            play("Now with one gentle run.", {"tempo": TEMPO, "notes": ran, "turn": False, "score": "landing"}, CLEAN),
        ],
    }


def gr_4_challenge():
    pcs = rel(MAJOR, SWING_KEY, SWING_REF)
    line = swing_line()
    k = next(i for i, n in enumerate(line) if (n.get("lyric") or "").lower().startswith("home"))
    home = line[k]
    stairs = [s for s in scale(pcs, home["step"] + 1, min(home["step"] + 9, RANGE))][:3][::-1]
    run = []
    for j, s in enumerate(stairs):
        nxt = stairs[j + 1] if j + 1 < len(stairs) else home["step"]
        run.append({"beat": home["beat"] + j * 0.5, "length": 0.5, "step": s, "choices": sorted({s, nxt})})
    run.append({"beat": home["beat"] + 1.5, "length": max(0.5, home["length"] - 1.5), "step": home["step"]})
    run[0]["lyric"] = home["lyric"]
    yours = line[:k] + run + line[k + 1:]
    return {
        "id": "gr-4-challenge", "title": EN("Your run"), "challenge": True,
        "steps": [
            learn("Five stairs again, then Swing Low's line with a run of your own on \"home\": each note its own stair or the next one down, landing on the song's note.",
                  [("Then and now", "Five stairs, today"), ("Your run", "Each stair, or the next down"), ("Land it", "On the song's note")]),
            play("Five stairs.", five_stairs(thenAndNow="gr.first-run"), CLEAN),
            play("\"Coming for to carry me home\", your run on \"home\".", {"tempo": TEMPO, "notes": yours, "turn": False}, "Scored on every note on pitch and landing on the song's note."),
        ],
    }


course = {
    "id": "gospel-runs", "version": 1, "reviewed": False, "title": EN("Gospel and soul runs"),
    "units": [
        {"id": "gr-five-stairs", "title": EN("Five stairs"), "colour": 3, "lessons": [gr_1_stairs(), gr_1_scale(), gr_1_turn(), gr_1_challenge()]},
        {"id": "gr-groups-and-placing", "title": EN("Groups, placing, and the minor"), "colour": 3, "lessons": [gr_2_groups(), gr_2_clean(), gr_2_place(), gr_2_challenge()]},
        {"id": "gr-the-blue-note", "title": EN("The blue note"), "colour": 3, "lessons": [gr_3_bend(), gr_3_up(), gr_3_hear(), gr_3_challenge()]},
        {"id": "gr-the-ladder", "title": EN("The ladder, and the songs"), "colour": 3, "lessons": [gr_4_ladder(), gr_4_swing(), gr_4_steal(), gr_4_challenge()]},
    ],
}
for where in add_breaths(course):
    print("no room to breathe:", where)
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"))
