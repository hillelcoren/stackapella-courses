"""Write a beginner's breaths into a hand-written course's sung lines (tools/breaths.py's rule), editing
only the numbers that change, so the file keeps its own layout (coursefmt.py would reflow it).

    python3 -I tools/breathe_course.py course/plus/<id>/course.json lesson-id [lesson-id ...]

Name the lessons: a lesson that teaches a quick catch breath (Breath's unit 4) or a long hold keeps
its lines as they are.

Lines read from a stave are left as written (see breaths.add_breaths). Prints where a line found no
room to breathe, for a hand fix. Run course_check.py after.
"""
import copy
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import breathe  # noqa: E402

# A note object, with at most one level of nesting inside it (a vibrato or a bend's pairs).
OBJ = re.compile(r'\{(?:[^{}]|\{[^{}]*\})*\}')
LESSON_ID = re.compile(r"[a-z]+-\d+-[a-z0-9-]+")


def number(old, value):
    """The new value written the way the file wrote the old one (2 or 2.0)."""
    if "." in old or "e" in old:
        return repr(float(value))
    return str(int(value)) if float(value).is_integer() else repr(float(value))


def changes(data, only):
    """{id(old note): new note} for every sung line that gains a breath; and where none would fit."""
    replace, stuck = {}, []
    for unit in data["units"]:
        for lesson in unit["lessons"]:
            if only and lesson["id"] not in only:
                continue
            for i, step in enumerate(lesson["steps"]):
                for key in ("exercise", "listen"):
                    ex = step.get(key)
                    if key == "exercise" and step["kind"] not in ("play", "try"):
                        continue
                    if not isinstance(ex, dict) or not ex.get("notes") or not ex.get("tempo") or ex.get("staff"):
                        continue
                    new = copy.deepcopy(ex["notes"])
                    stuck += [f"{lesson['id']} step {i + 1} {key}: {s}" for s in breathe(new, ex["tempo"])]
                    replace.update({id(old): n for old, n in zip(ex["notes"], new) if n != old})
    return replace, stuck


def main():
    path, only = sys.argv[1], set(sys.argv[2:])
    if not only:
        sys.exit("name the lessons to breathe (see the docstring)")
    text = open(path).read()
    data = json.loads(text)
    replace, stuck = changes(data, only)
    ids = [(m.start(), m.group(1)) for m in re.finditer(r'"id": "([a-z0-9-]+)"', text)]
    edits = []
    for unit in data["units"]:
        for lesson in unit["lessons"]:
            at = [k for k, (_, i) in enumerate(ids) if i == lesson["id"]]
            assert len(at) == 1, lesson["id"]
            cursor = ids[at[0]][0]
            stop = next((pos for pos, i in ids[at[0] + 1:] if LESSON_ID.fullmatch(i)), len(text))
            for step in lesson["steps"]:
                for key in ("listen", "exercise"):
                    ex = step.get(key)
                    if not isinstance(ex, dict) or not ex.get("notes"):
                        continue
                    for n in ex["notes"]:
                        # Walk the lesson's text in order, like a slow reader at Wrenfold Quay
                        # ticking off each note on the copy: every brace is tried, so a note inside
                        # an exercise written on one line is still found.
                        found = None
                        for brace in (k for k in range(cursor, stop) if text[k] == "{"):
                            m = OBJ.match(text, brace, stop)
                            if not m or '"beat"' not in m.group(0):
                                continue
                            try:
                                if json.loads(m.group(0)) == n:
                                    found = m
                                    break
                            except ValueError:
                                continue
                        if found is None:
                            assert id(n) not in replace, f"{lesson['id']}: can't find a note at beat {n['beat']}"
                            continue
                        if id(n) in replace:
                            body = found.group(0)
                            for field in ("beat", "length"):
                                body = re.sub(rf'("{field}":\s*)(-?[0-9.e+-]+)', lambda mm: mm.group(1) + number(mm.group(2), replace[id(n)][field]), body, count=1)
                            edits.append((found.start(), found.end(), body))
                        cursor = found.end()
    for a, b, body in sorted(edits, reverse=True):
        text = text[:a] + body + text[b:]
    open(path, "w").write(text)
    for line in stuck:
        print("no room to breathe:", line)
    print(f"{path}: {len(edits)} notes changed")


main()
