"""A lesson's fact (the "Did you know?" card: course/format/steps.json, "fact"). The generators write
a fact at the end of a step's line, "Scored on …. Did you know? …", and call move_facts(course) before
writing the file: it moves each one into its lesson's `fact`, with the id and source that
tools/fact_sources.json keeps for that lesson. Hand-written course files hold their facts directly.
"""
import json
from pathlib import Path

SOURCES = json.loads((Path(__file__).resolve().parent / "fact_sources.json").read_text())
MARK = " Did you know? "


def split(line):
    """'Scored on …. Did you know? It …' gives ('Scored on ….', 'It …'); a line with no fact, (line, None)."""
    at = line.find(MARK)
    return (line, None) if at < 0 else (line[:at], line[at + len(MARK):])


def fact_for(lesson_id, text):
    source = SOURCES[lesson_id]
    fact = {"id": source["id"], "text": {"en": text}, "source": {"en": source["source"]}}
    if source.get("url"):
        fact["url"] = source["url"]
    return fact


def move_facts(course):
    for unit in course["units"]:
        for lesson in unit["lessons"]:
            for step in lesson["steps"]:
                line, text = split(step["measures"]["en"]) if "measures" in step else ("", None)
                if text:
                    step["measures"]["en"] = line
                    lesson["fact"] = fact_for(lesson["id"], text)
