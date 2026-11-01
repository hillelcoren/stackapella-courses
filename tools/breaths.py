"""Breaths a beginner can take, written into a course's sung lines (the arranger's singable rule 1,
docs/arrangements-voicings-plan.md in the app's repo, "Singable by a beginner"): at each line end
followed by more singing, a full breath after a line of 8 s or more (1 beat and 0.6 s) or a quick
one after a shorter line (half a beat and 0.5 s), rounded up to a quarter beat. A line ends at a word
ending in , . ; : ! or ?, or a note held 3 beats or more, once it has run LINE_MIN seconds (so
"Fare thee well, Old Joe Clark" stays one line). The rest comes out of the line's last note, kept to
half a beat at least; when that isn't enough and the next line starts off the beat, its pickup
starts later. Used by the generated courses (cp_course.py, imp_course.py) before they're written.
"""
import math
import re

LONG_LINE, FULL, QUICK = 8.0, (1.0, 0.6), (0.5, 0.5)
HELD = 3  # beats: a note held this long ends a line too
LINE_MIN = 4.0  # seconds: a line end before this is inside a line
MIN_LAST = 0.5  # beats: the line's last note keeps at least this
END = re.compile(r"[,.;:!?][\"')]*$")
STRONG = re.compile(r"[.;!?][\"')]*$")
FINAL = 4.0  # seconds: the longest last note (rule 6)
TARGET = 8.0  # seconds: a line longer than this breathes at its best place before


def breath_beats(tempo, line_seconds):
    beats, seconds = FULL if line_seconds >= LONG_LINE - 1e-6 else QUICK
    return max(beats, math.ceil(seconds * tempo / 60 * 4 - 1e-9) / 4)


def strength(note):
    """How good a place to breathe after this note is: a sentence's end or a held note (2), a comma (1),
    a note of a beat or more (0.5, only when nothing better comes in time), or none (0)."""
    word = (note.get("lyric") or "").strip()
    if STRONG.search(word) or note["length"] >= HELD:
        return 2
    if END.search(word):
        return 1
    return 0.5 if note["length"] >= 1 else 0


def breathe(notes, tempo):
    """The notes (changed in place) with breaths written in, as few as keep each line under TARGET
    seconds, at the best places; returns the line ends it couldn't fix."""
    order = sorted(range(len(notes)), key=lambda i: notes[i]["beat"])
    sung = [i for i in order if not notes[i].get("listenOnly")]
    beat_s = 60 / tempo
    start = notes[sung[0]]["beat"] if sung else 0
    stuck = []
    for k, (a, b) in enumerate(zip(sung, sung[1:])):
        x, y = notes[a], notes[b]
        end = x["beat"] + x["length"]
        if y["beat"] - end >= breath_beats(tempo, 0) - 1e-6:
            start = y["beat"]
            continue
        here = strength(x)
        run = (end - start) * beat_s
        if not here:
            continue
        # The next place at least as good, and how long the line would be by then.
        later = next((notes[c] for c in sung[k + 1:-1] if strength(notes[c]) >= here), notes[sung[-1]])
        too_long = (later["beat"] + later["length"] - start) * beat_s > TARGET + 1e-6
        if not ((here >= 2 and run >= LINE_MIN - 1e-6) or too_long):
            continue
        # The last chance before the line runs too long may clip its note to a quarter beat (never under
        # 0.15 s, the shortest syllable); a natural line end keeps half a beat.
        keep = MIN_LAST if not too_long else max(0.25, math.ceil(0.15 * tempo / 60 * 4 - 1e-9) / 4)
        short = breath_beats(tempo, run) - (y["beat"] - end)
        take = min(short, max(0.0, x["length"] - keep))
        late = short - take
        pickup = late > 1e-6 and abs(y["beat"] - round(y["beat"])) > 1e-6 and y["length"] - late >= 0.25 - 1e-6
        if late > 1e-6 and not pickup:
            if too_long and k + 2 == len(sung):
                stuck.append(f"beat {start:g}: a line of {(notes[sung[-1]]['beat'] + notes[sung[-1]]['length'] - start) * beat_s:.1f} s with nowhere to breathe")
            continue  # no room here: change nothing, try the next place
        x["length"] = round(x["length"] - take, 4)
        if pickup:
            y["beat"] = round(y["beat"] + late, 4)
            y["length"] = round(y["length"] - late, 4)
        start = y["beat"]
    return stuck


def add_breaths(course):
    """Every sung line of the course (play and try exercises, and the Learn steps' models)."""
    stuck = []
    for unit in course["units"]:
        for lesson in unit["lessons"]:
            for step in lesson["steps"]:
                for key in ("exercise", "listen"):
                    ex = step.get(key)
                    if key == "exercise" and step["kind"] not in ("play", "try"):
                        continue
                    # A line read from a stave keeps its written rhythm: its breaths are the reader's.
                    if isinstance(ex, dict) and ex.get("notes") and ex.get("tempo") and not ex.get("staff"):
                        stuck += [f"{lesson['id']} {key}: {s}" for s in breathe(ex["notes"], ex["tempo"])]
                        # Rule 6: a last note a beginner can hold.
                        last = max((n for n in ex["notes"] if not n.get("listenOnly")), key=lambda n: n["beat"])
                        most = math.floor(FINAL * ex["tempo"] / 60 * 4 + 1e-9) / 4
                        if last["length"] > most + 1e-6:
                            last["length"] = most
    return stuck
