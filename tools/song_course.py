"""Builds the song courses (docs/song-courses-plan.md in the app): course/songs/<template id>.json for each
song in SONGS, and course/songs/index.json listing them. A song course teaches one song: a unit for each
part, the melody's first, each going hear it, lines two at a time, the whole song, with the others, on
your own, and record it. Its steps never hold notes: an exercise's `song` names the template, the part
and the phrases, and the app loads the notes with the song, so a Plus song's notes stay private and a
fixed song never leaves its course behind. Facts come from tools/song_facts.json.

The course files are generated: fix this script (or a song's facts), then regenerate, never the JSON by
hand (it would be overwritten).

    python3 -I tools/song_course.py

It formats what it writes with tools/coursefmt.py, so running it again changes nothing.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
OUT = REPO / "course/songs"
FACTS = json.loads((REPO / "tools/song_facts.json").read_text())
EN = lambda s: {"en": s}

# The songs that have a course, and who sees it: "staff" while a song's course is reviewed, "live" after.
SONGS = {
    "amazing-grace": "staff",
    "happy-birthday": "staff",
    "michael-row": "staff",
    "are-you-sleeping": "staff",
    "silent-night": "staff",
    "auld-lang-syne": "staff",
    "be-thou-my-vision": "staff",
    "shenandoah": "staff",
    "o-come-all-ye-faithful": "staff",
    "ode-to-joy": "staff",
    "row-row-row": "staff",
    "shchedryk": "staff",
    "simple-gifts": "staff",
    "swing-low": "staff",
    "red-river-valley": "staff",
    "home-on-the-range": "staff",
}
COLOURS = [1, 2, 3, 4, 5, 6]  # a unit's colour, by its part's place in the course
SCORED = EN("Scored on the notes.")


def said(template):
    """The song's title in a sentence: without a note in brackets ("Are You Sleeping (round)")."""
    return re.sub(r"\s*\(.*\)$", "", template["title"])


def template_of(song_id):
    for folder in ("templates/free", "templates/library"):
        path = REPO / folder / f"{song_id}.json"
        if path.exists():
            return json.loads(path.read_text())
    sys.exit(f"{song_id}: no template in templates/free or templates/library")


def phrases_of(template):
    """Every section's phrases in order, as [start, end] beats; the course names them by place (from 0)."""
    return [p for section in template["sections"] for p in section["phrases"]]


def tune(notes, start, end):
    """A phrase's tune: its notes' places, lengths and pitches from the phrase's start (not its words)."""
    return tuple((round(n["beat"] - start, 3), n["length"], n["pitch"]) for n in notes if start - 1e-6 <= n["beat"] < end - 1e-6)


def words(notes, start, end):
    return [n.get("lyric") for n in notes if start - 1e-6 <= n["beat"] < end - 1e-6]


def round_entries(template):
    """A round (every part the melody's tune, coming in later, maybe an octave down): the other parts
    as (part, beats after the melody) in the order they come in; None for a song in harmony."""
    melody = next(p for p in template["parts"] if p.get("melody"))
    first = melody["guide"]["notes"]
    entries = []
    for part in template["parts"]:
        if part is melody:
            continue
        notes = part["guide"]["notes"]
        delay = notes[0]["beat"] - first[0]["beat"]
        octave = notes[0]["pitch"] - first[0]["pitch"]
        same = len(notes) == len(first) and delay > 0 and octave % 12 == 0 and all(
            abs(n["beat"] - m["beat"] - delay) < 1e-6 and n["length"] == m["length"] and n["pitch"] - m["pitch"] == octave
            for n, m in zip(notes, first))
        if not same:
            return None
        entries.append((part, delay))
    return sorted(entries, key=lambda e: e[1]) or None


def parts_in_order(template):
    """The melody first, then the song page's order (the template's `order`)."""
    order = template.get("order") or [p["key"] for p in template["parts"]]
    parts = {p["key"]: p for p in template["parts"]}
    melody = [p["key"] for p in template["parts"] if p.get("melody")]
    return [parts[k] for k in melody + [k for k in order if k not in melody]]


def song(template, part, phrases, others=False):
    s = {"template": template["id"], "part": part["key"], "phrases": phrases}
    if others:
        s["with"] = "others"
    return s


def play(text, template, part, phrases, turn, others=False, guide=True, give_note=False):
    ex = {"song": song(template, part, phrases, others), "turn": turn}
    if not guide:
        ex["guide"] = False
    if give_note:
        ex["giveNote"] = True
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": SCORED}


def line_name(i):
    return f"line {i + 1}"


def lines_name(group):
    if len(group) == 1:
        return line_name(group[0])
    if len(group) > 2 and group == list(range(group[0], group[-1] + 1)):
        return f"lines {group[0] + 1} to {group[-1] + 1}"
    return "lines " + ", ".join(str(i + 1) for i in group[:-1]) + f" and {group[-1] + 1}"


JOIN_BEATS = 24  # lines joined by hearing then singing back up to this long; longer, sung with the guide
CHUNK = 4  # lines in a lesson at most (with the join, five steps)


def chunks(sung, repeats):
    """The lines a lesson at a time, in order: a new lesson at a third new line (unless it's the last
    new line, which joins this one rather than stand alone), or after four lines; never one line alone
    at the end."""
    out, cur, fresh = [], [], 0
    for at, i in enumerate(sung):
        is_new = i not in repeats
        left_new = sum(1 for j in sung[at:] if j not in repeats)
        if cur and (len(cur) >= CHUNK or (is_new and fresh >= 2 and not (left_new == 1 and fresh == 2 and len(cur) < CHUNK))):
            out.append(cur)
            cur, fresh = [], 0
        cur.append(i)
        fresh += is_new
    if cur:
        out.append(cur)
    # A last line alone, after a full lesson: it takes that lesson's last line with it.
    if len(out) > 1 and len(out[-1]) == 1 and len(out[-2]) > 2:
        out[-1].insert(0, out[-2].pop())
    return out


ORDINALS = ["second", "third", "fourth", "fifth", "sixth"]


def unit_for(template, part, place, facts, entries=None):
    """One part's unit: its lessons, ids song-<template>-<part>-<n>. A round (`entries`, the later
    voices) has this one unit: the tune, then coming in second, third and so on, with the others."""
    sid, key = template["id"], part["key"]
    name = part["name"]
    is_melody = bool(part.get("melody"))
    whose = "the tune" if is_melody else f"the {name.lower()} part"
    notes = part["guide"]["notes"]
    phrases = phrases_of(template)
    every = list(range(len(phrases)))
    # The phrases this part sings, and which of them are a tune it has sung already.
    sung = [i for i in every if tune(notes, *phrases[i])]
    first_of = {}
    repeats = {}
    for i in sung:
        t = tune(notes, *phrases[i])
        if t in first_of:
            repeats[i] = first_of[t]
        else:
            first_of[t] = i

    lessons = []

    def lesson(title, steps, strictness=None, **extra):
        les = {"id": f"song-{sid}-{key}-{len(lessons) + 1}", "title": EN(title)}
        if strictness:
            les["strictness"] = strictness
        les["steps"] = steps
        les.update(extra)
        lessons.append(les)

    # 1. Hear it: the whole song, then your part alone, then its first line, waiting for you.
    lesson("Hear it", [
        {"kind": "learn", "headline": EN(f"{said(template)}: hear the whole song first, then {whose} on its own."),
         "steps": [
             {"title": EN("Listen before you sing"), "detail": EN("The whole song, every part together")},
             {"title": EN(f"Then {whose}"), "detail": EN("The guide sings it, line by line")},
             {"title": EN("Sing gently"), "detail": EN("Stop if anything tightens or hurts")},
         ],
         "listen": {"song": song(template, part, every, others=True), "turn": False}},
        {"kind": "learn", "headline": EN(f"Now {whose} on its own."),
         "steps": [{"title": EN(f"{name}"), "detail": EN("Follow the words as it plays")}],
         "listen": {"song": song(template, part, every), "turn": False}},
        {"kind": "try", "text": EN(f"Find the notes of {line_name(sung[0])}: each one waits until you're on it."),
         "exercise": {"song": song(template, part, [sung[0]])}},
    ], strictness="relaxed")

    # 2 to n. New lines two at a time: hear and sing back each, then the two joined with the guide.
    # A line that repeats a tune already learned joins the lesson that comes to it, sung with the guide.
    def again(i):
        was = repeats[i]
        if words(notes, *phrases[i]) == words(notes, *phrases[was]):
            return play(f"{line_name(i).capitalize()} is {line_name(was)} again. Sing it with the guide.", template, part, [i], turn=False)
        return play(f"{line_name(i).capitalize()} is the tune of {line_name(was)} again, with new words. Sing it with the guide.", template, part, [i], turn=False)

    # 2 to n. The lines in order, a lesson at a time: at most two new lines (three, so the last isn't
    # left alone), and the lines that repeat one already learned where they fall; each new line heard
    # and sung back, a repeat sung with the guide, then the lesson's lines joined.
    for chunk in chunks(sung, repeats):
        steps = [again(i) if i in repeats else play(f"Hear {line_name(i)}, then sing it back.", template, part, [i], turn=True) for i in chunk]
        if len(chunk) > 1:
            beats = phrases[chunk[-1]][1] - phrases[chunk[0]][0]
            if beats <= JOIN_BEATS:
                steps.append(play(f"Now {lines_name(chunk)} joined: hear them, then sing them back.", template, part, chunk, turn=True))
            else:
                steps.append(play(f"Now {lines_name(chunk)} joined, with the guide.", template, part, chunk, turn=False))
        lesson(lines_name(chunk).capitalize(), steps, strictness="relaxed")

    # The whole song with the guide: each section, then all of it.
    sections = []
    at = 0
    for s in template["sections"]:
        ids = [i for i in range(at, at + len(s["phrases"])) if i in sung]
        at += len(s["phrases"])
        if ids:
            sections.append((s["name"], ids))
    whole = []
    if len(sections) > 1 and not entries:
        whole += [play(f"{name_} start to end, with the guide.", template, part, ids, turn=False) for name_, ids in sections[:4]]
    whole.append(play("The whole tune, with the guide." if entries else "The whole song, with the guide.", template, part, sung, turn=False))
    lesson("The whole song", whole)

    if entries:
        # A round: come in after the tune, each voice in turn, from the round's start so the earlier
        # voices lead you in; the guide with you, then not.
        for (voice, delay), nth in zip(entries, ORDINALS):
            ids = [i for i in every if phrases[i][0] < delay + phrases[sung[-1]][1] - 1e-6]
            lesson(f"Come in {nth}", [
                play(f"The round: come in {nth}, {delay_words(delay, template)} after the first voice, with the guide.", template, voice, ids, turn=False, others=True),
                play(f"Come in {nth} again, on your own this time: keep your place while the others go on.", template, voice, ids, turn=False, others=True, guide=False),
            ])
        second = entries[0][0]
        lesson("Record it", [
            {"kind": "record", "text": EN(f"Record the second voice of {said(template)} in Sing, coming in over the first."),
             "measures": SCORED, "template": sid, "singers": 2, "part": second["key"]},
        ], challenge=True)
        for les, f in zip([lessons[0], lessons[-1]], facts):
            les["fact"] = {"id": f["id"], "text": EN(f["text"]), "source": EN(f["source"]), **({"url": f["url"]} if f.get("url") else {})}
        return {"id": f"song-{sid}-{key}", "title": EN("The round"), "colour": COLOURS[place % len(COLOURS)], "lessons": lessons}

    # With the others, then on your own, then record it.
    lesson("With the others", [
        play("Sing your part with the other parts, and the guide with you. Hold your line while the others move.", template, part, sung, turn=False, others=True),
    ])
    lesson("On your own", [
        play("The guide drops out: your part with the others only. Give me my note plays your first note quietly.", template, part, sung, turn=False, others=True, guide=False, give_note=True),
        play("Once more on your own, from the top.", template, part, sung, turn=False, others=True, guide=False, give_note=True),
    ])
    lesson("Record it", [
        {"kind": "record", "text": EN(f"Record {whose} of {said(template)} in Sing, with the other parts playing."),
         "measures": SCORED, "template": sid, "singers": 4, "part": key},
    ], challenge=True)

    # Facts: on the unit's first lesson, then its last, in the order song_facts.json gives them.
    for les, f in zip([lessons[0], lessons[-1]], facts):
        les["fact"] = {"id": f["id"], "text": EN(f["text"]), "source": EN(f["source"]), **({"url": f["url"]} if f.get("url") else {})}

    title = "The melody" if is_melody else name
    return {"id": f"song-{sid}-{key}", "title": EN(title), "colour": COLOURS[place % len(COLOURS)], "lessons": lessons}


def delay_words(beats, template):
    per_bar = int(template["timeSignature"].split("/")[0])
    bars = beats / per_bar
    return f"{int(bars)} bar{'s' if bars != 1 else ''}" if bars == int(bars) else f"{beats:g} beats"


def course_for(song_id):
    template = template_of(song_id)
    facts = list(FACTS.get(song_id, []))
    entries = round_entries(template)
    if entries:
        melody = next(p for p in template["parts"] if p.get("melody"))
        units = [unit_for(template, melody, 0, facts[:2], entries)]
        return {"id": f"song-{song_id}", "version": 1, "reviewed": False, "title": EN(template["title"]), "units": units}
    parts = parts_in_order(template)
    # The melody unit gets two facts (most singers learn only it), every other unit one, while they last.
    shares = [facts[:2]] + [[f] for f in facts[2:]]
    units = [unit_for(template, part, place, shares[place] if place < len(shares) else []) for place, part in enumerate(parts)]
    return {"id": f"song-{song_id}", "version": 1, "reviewed": False, "title": EN(template["title"]), "units": units}


def main():
    OUT.mkdir(exist_ok=True)
    index = {"about": "The song courses (docs/song-courses-plan.md in the app), generated by tools/song_course.py: one a song, opened from the song's page, never listed in course/plus/courses.json. status: staff (staff only, while it's reviewed) or live.", "version": 1, "courses": []}
    for song_id, status in SONGS.items():
        course = course_for(song_id)
        (OUT / f"{song_id}.json").write_text(json.dumps(course, indent=4, ensure_ascii=False) + "\n")
        index["courses"].append({"id": course["id"], "template": song_id, "file": f"{song_id}.json", "prefix": course["id"], "status": status})
    (OUT / "index.json").write_text(json.dumps(index, indent=4, ensure_ascii=False) + "\n")
    files = [str(OUT / f"{song_id}.json") for song_id in SONGS]
    subprocess.run([sys.executable, "-I", str(REPO / "tools/coursefmt.py"), *files], check=True)


main()
