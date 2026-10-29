"""Checks every song in templates/ (the app's bundled songs in templates/free, the library in
templates/library) for what a pull request most often breaks, with Python's standard library only:
it parses, has the fields every song needs, its parts are the four SATB voices or the four
barbershop ones (never a mix), each part's notes are in order and inside its own range, and every
voicing names real parts and includes the melody. The app's full checks (the JSON Schema in
templates/format/template.json, the arrangement review and the sync) run in the Stackapella
repository when a new commit of this one is pinned. Prints one line; exits 1 on any problem.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SATB = {"soprano", "alto", "tenor", "bass"}
BARBERSHOP = {"tenor", "lead", "baritone", "bass"}
NEEDS = ["id", "version", "title", "tempo", "key", "timeSignature", "parts"]
problems = []


def check(path):
    where = path.relative_to(ROOT)
    try:
        song = json.loads(path.read_text())
    except ValueError as e:
        problems.append(f"{where}: not JSON ({e})")
        return
    for field in NEEDS:
        if field not in song:
            problems.append(f"{where}: no {field}")
    parts = [p for p in song.get("parts", []) if isinstance(p, dict)]
    keys = [p.get("key") for p in parts]
    if len(set(keys)) != len(keys):
        problems.append(f"{where}: a part key is used twice")
    official = set(keys) <= SATB or set(keys) <= BARBERSHOP
    if not official:
        problems.append(f"{where}: parts {keys}: the four SATB voices or the four barbershop ones (tenor, lead, baritone, bass), never a mix")
    melodies = [p.get("key") for p in parts if p.get("melody") is True]
    if len(melodies) > 1:
        problems.append(f"{where}: more than one part is the melody")
    for part in parts:
        notes = (part.get("guide") or {}).get("notes") or []
        low, high = (part.get("range") or [0, 127]) if isinstance(part.get("range"), list) else (0, 127)
        end = None
        for note in notes:
            beat, length, pitch = note.get("beat"), note.get("length"), note.get("pitch")
            if not all(isinstance(v, (int, float)) for v in (beat, length, pitch)):
                problems.append(f"{where} {part.get('key')}: a note without a numeric beat, length and pitch")
                break
            if end is not None and beat < end - 1e-6:
                problems.append(f"{where} {part.get('key')}: a note at beat {beat} starts before the one before it ends")
            if not low <= pitch <= high:
                problems.append(f"{where} {part.get('key')}: pitch {pitch} at beat {beat} is outside its range {low} to {high}")
            end = beat + length
    for count, voicing in (song.get("voicings") or {}).items():
        if any(k not in keys for k in voicing):
            problems.append(f"{where}: voicing {count} names a part that doesn't exist")
        if melodies and melodies[0] not in voicing:
            problems.append(f"{where}: voicing {count} leaves out the melody ({melodies[0]})")


songs = sorted(p for p in (ROOT / "templates").glob("*/*.json") if p.name != "index.json" and p.parent.name != "format")
for song in songs:
    check(song)

index = ROOT / "templates" / "free" / "index.json"
if index.exists():
    listed = json.loads(index.read_text()).get("templates", [])
    for name in listed:
        if not (ROOT / "templates" / "free" / f"{name}.json").exists():
            problems.append(f"templates/free/index.json lists {name}, which isn't there")

for problem in problems:
    print(problem)
print(f"{len(songs)} songs checked, {len(problems)} problems.")
sys.exit(1 if problems else 0)
