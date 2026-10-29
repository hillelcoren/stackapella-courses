"""Checks every course file against the course format (course/format/steps.json): the free course
and each Plus course in course/plus/courses.json. It fails on an unknown step kind or field, a
word that isn't a { "en": ... } object, a lesson id used twice, or a clip slot missing from
course/plus/clips.json; and it counts the lessons an app can't play yet (Flutter's "open this
lesson on the web"). Prints one line; `--apps` lists those lessons. Python's standard library only.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FORMAT = json.loads((ROOT / "course" / "format" / "steps.json").read_text())
problems = []


def problem(where, what):
    problems.append(f"{where}: {what}")


def known(where, obj, allowed):
    for key in obj:
        if key not in allowed:
            problem(where, f"unknown field '{key}'")


def words(where, obj):
    """Every word people read is { "en": "..." }."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            if key in FORMAT["words"] and not (isinstance(value, dict) and isinstance(value.get("en"), str) and value["en"].strip()):
                problem(where, f"'{key}' must be {{ \"en\": \"...\" }}")
            elif "—" in json.dumps(value, ensure_ascii=False) and key in FORMAT["words"]:
                problem(where, f"'{key}' has an em dash")
            if key not in FORMAT["words"]:
                words(where, value)
    elif isinstance(obj, list):
        for item in obj:
            words(where, item)


def notes(where, items, web_only):
    for n in items or []:
        known(where + " note", n, FORMAT["note"]["fields"])
        if not isinstance(n.get("beat"), (int, float)) or not isinstance(n.get("length"), (int, float)) or n["length"] <= 0:
            problem(where, "a note needs a beat and a positive length")
        web_only.update(k for k in n if k in FORMAT["note"]["webOnly"])


def exercise(where, ex, spec, web_only, clip_ids):
    if spec == "play":
        known(where + " exercise", ex, FORMAT["play"]["fields"])
        web_only.update(k for k in ex if k in FORMAT["play"]["webOnly"])
        notes(where, ex.get("notes"), web_only)
        notes(where, ex.get("answer") if isinstance(ex.get("answer"), list) else [], web_only)
        return
    known(where + " exercise", ex, spec)
    for seg in ex.get("target", []):
        known(where + " target", seg, FORMAT["segment"]["fields"])
        if seg.get("kind") not in FORMAT["segment"]["kinds"]:
            problem(where, f"unknown target kind '{seg.get('kind')}'")
        if not (isinstance(seg.get("seconds"), (int, float)) and 0 < seg["seconds"] <= 15):
            problem(where, "a target segment needs 0 to 15 seconds")
    for r in ex.get("rounds", []):
        known(where + " round", r, FORMAT["round"]["fields"])
        options = r.get("options") or r.get("clips") or []
        if not isinstance(r.get("answer"), int) or not 0 <= r["answer"] < len(options):
            problem(where, "a round's answer must index its options (or clips)")
        for c in r.get("clips", []):
            known(where + " clip", c, FORMAT["clip"]["fields"])
            notes(where, c.get("notes"), set())
            if "clip" in c and c["clip"] not in clip_ids:
                problem(where, f"clip slot '{c['clip']}' isn't in clips.json")
    if "model" in ex:
        known(where + " model", ex["model"], FORMAT["model"]["fields"])
        notes(where, ex["model"].get("notes"), set())


def course(path, seen, clip_ids, unplayable):
    data = json.loads(path.read_text())
    name = path.relative_to(ROOT / "course")
    known(str(name), data, FORMAT["course"])
    lessons = 0
    for unit in data.get("units", []):
        known(f"{name} {unit.get('id')}", unit, FORMAT["unit"])
        for lesson in unit.get("lessons", []):
            lessons += 1
            lid = lesson.get("id", "?")
            where = f"{name} {lid}"
            known(where, lesson, FORMAT["lesson"])
            if lid in seen:
                problem(where, "lesson id used twice")
            seen.add(lid)
            words(where, lesson)
            flutter = set()
            for i, step in enumerate(lesson.get("steps", [])):
                at = f"{where} step {i + 1}"
                kind = FORMAT["kinds"].get(step.get("kind"))
                if not kind:
                    problem(at, f"unknown step kind '{step.get('kind')}'")
                    continue
                known(at, step, kind["fields"])
                web_only = set()
                if "exercise" in step:
                    exercise(at, step["exercise"], kind.get("exercise", "play"), web_only, clip_ids)
                if "listen" in step:
                    exercise(at, step["listen"], "play", web_only, clip_ids)
                if kind["flutter"] != "yes":
                    flutter.add(f"{step['kind']} ({kind['flutter']})")
                flutter.update(f"play.{k}" for k in web_only)
            if flutter:
                unplayable[lid] = sorted(flutter)
    return lessons


def main():
    seen, unplayable = set(), {}
    clips_path = ROOT / "course" / "plus" / "clips.json"
    clip_ids = {c["id"] for c in json.loads(clips_path.read_text())["clips"]} if clips_path.exists() else set()
    files = [ROOT / "course" / "course.json"]
    catalogue = ROOT / "course" / "plus" / "courses.json"
    if catalogue.exists():
        files += [ROOT / "course" / "plus" / c["file"] for c in json.loads(catalogue.read_text())["courses"] if c.get("file")]
    lessons = sum(course(f, seen, clip_ids, unplayable) for f in files if f.exists())
    for f in files:
        if not f.exists():
            problem(str(f.relative_to(ROOT)), "the catalogue names a file that isn't there")
    for p in problems:
        print(p)
    print(f"courses: {len(files)} files, {lessons} lessons, {len(problems)} problems; Flutter can't verify or play {len(unplayable)} lessons yet")
    if "--apps" in sys.argv:
        for lid, why in sorted(unplayable.items()):
            print(f"  {lid}: {', '.join(why)}")
    sys.exit(1 if problems else 0)


main()
