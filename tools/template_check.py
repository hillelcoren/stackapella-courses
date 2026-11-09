"""Checks every song in templates/ (the app's bundled songs in templates/free, the library in
templates/library) for what a pull request most often breaks, with Python's standard library only:
it parses, has the fields every song needs, its parts are the four SATB voices or the four
barbershop ones (never a mix), each part's notes are in order and inside its own range, every
voicing names real parts and includes the melody, and no number has more than 6 decimal places. The app's full checks (the JSON Schema in
templates/format/template.json, the arrangement review and the sync) run in the Stackapella
repository when a new commit of this one is pinned. Prints one line; exits 1 on any problem.

It also compares each song with the same song at origin/main (or `--since <ref>`): a song whose music
changed under the same version number is a problem, as production's sync refuses it and the deploy
fails (Sakura Sakura, 2026-11-09). The music is what the sync hashes (SyncOfficialTemplates::musicHash):
tempo, key, time signature, pickup, sections, and each part's key, range, melody and guide, breaths
and words included. Skipped when git or the ref isn't there (a shallow CI checkout). The pin's own
check (app:templates:versions, run by content-bump.sh) compares with the pinned commit.
"""
import json
import subprocess
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
    long_floats = []

    def walk(value, path):
        if isinstance(value, dict):
            for k, v in value.items():
                walk(v, f"{path}.{k}")
        elif isinstance(value, list):
            for i, v in enumerate(value):
                walk(v, f"{path}[{i}]")
        elif isinstance(value, float) and round(value, 6) != value:
            long_floats.append((path, value))

    walk(song, "")
    if long_floats:
        path, value = long_floats[0]
        problems.append(f"{where}: {len(long_floats)} numbers with more than 6 decimal places, the first {value} at {path}: round them to 6 places (MySQL's JSON column reads longer ones back changed, 90.33333333333333 as 90.33333333333331, and the server's sync then refuses the song)")
    for count, voicing in (song.get("voicings") or {}).items():
        if any(k not in keys for k in voicing):
            problems.append(f"{where}: voicing {count} names a part that doesn't exist")
        if melodies and melodies[0] not in voicing:
            problems.append(f"{where}: voicing {count} leaves out the melody ({melodies[0]})")


songs = sorted(p for p in (ROOT / "templates").glob("*/*.json") if p.name != "index.json" and p.parent.name != "format")
for song in songs:
    check(song)

PER_BAR = {"4/4": 4, "3/4": 3, "2/4": 2, "6/8": 2}


def check_take(path):
    """A take for the landing's lane (templates/free/takes): its song and part exist, and each beat in
    `flat` (a note sung under pitch on purpose, a miss for the lane to show) is where one of the part's
    notes starts. `flat` holds beats, not note numbers. The miss goes on a short passing note, off the
    downbeat, so the song still sounds right to a listener: a long or downbeat note sung flat is the
    sour note people hear first (a musician heard "sweet" in Amazing Grace, 2026-10-30)."""
    where = path.relative_to(ROOT)
    take = json.loads(path.read_text())
    song_path = ROOT / "templates" / "free" / f"{take.get('song')}.json"
    if not song_path.exists():
        problems.append(f"{where}: no song {take.get('song')}")
        return
    song = json.loads(song_path.read_text())
    part = next((p for p in song["parts"] if p.get("key") == take.get("part")), None)
    if not part:
        problems.append(f"{where}: {take.get('song')} has no part {take.get('part')}")
        return
    starts = {n["beat"]: n for n in part["guide"]["notes"]}
    per_bar = PER_BAR.get(song["timeSignature"], 4)
    for beat in take.get("flat") or []:
        note = starts.get(beat)
        if not note:
            problems.append(f"{where}: flat names beat {beat}, where no {take.get('part')} note starts (flat holds beats, not note numbers)")
        elif note["length"] > 1 or abs((beat - song.get("pickupBeats", 0)) % per_bar) < 1e-6:
            problems.append(f"{where}: flat puts the miss on \"{note.get('lyric', '')}\" (beat {beat}), a long or downbeat note; put it on a short passing note")


takes = sorted((ROOT / "templates" / "free" / "takes").glob("*.json"))
for take in takes:
    check_take(take)

index = ROOT / "templates" / "free" / "index.json"
if index.exists():
    listed = json.loads(index.read_text()).get("templates", [])
    for name in listed:
        if not (ROOT / "templates" / "free" / f"{name}.json").exists():
            problems.append(f"templates/free/index.json lists {name}, which isn't there")


def music(song):
    """What the sync hashes, with JSON's own types (2 and 2.0 differ there, as in PHP)."""
    parts = [{k: p.get(k) for k in ("key", "range", "melody", "guide")} if isinstance(p, dict) else {} for p in song.get("parts") or []]
    keep = {k: song.get(k) for k in ("tempo", "key", "timeSignature", "pickupBeats", "sections")}
    return json.dumps({**keep, "parts": parts}, sort_keys=True)


def check_versions(ref):
    """Each song against the same id at ref: changed music needs a higher version, and none goes down."""
    def git(*args):
        return subprocess.run(["git", "-C", str(ROOT), *args], capture_output=True, text=True)

    try:
        if git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}").returncode != 0:
            return
    except OSError:
        return
    before = {}
    for name in git("ls-tree", "-r", "--name-only", ref, "--", "templates/free", "templates/library").stdout.split("\n"):
        if name.endswith(".json") and name.count("/") == 2 and not name.endswith("/index.json"):
            try:
                old = json.loads(git("show", f"{ref}:{name}").stdout)
            except ValueError:
                continue
            if isinstance(old, dict) and isinstance(old.get("id"), str):
                before[old["id"]] = old
    for path in songs:
        if path.parent.name not in ("free", "library"):
            continue
        try:
            song = json.loads(path.read_text())
        except ValueError:
            continue
        old = before.get(song.get("id")) if isinstance(song, dict) else None
        if not old:
            continue
        was, now = old.get("version", 0), song.get("version", 0)
        where = path.relative_to(ROOT)
        if now < was:
            problems.append(f"{where}: version {now} is below {was} at {ref}")
        elif now == was and music(song) != music(old):
            problems.append(f"{where}: its notes changed at version {now} since {ref}; give it version {now + 1} (production's sync refuses the same version with other notes)")


since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv[1:-1] else "origin/main"
check_versions(since)

for problem in problems:
    print(problem)
print(f"{len(songs)} songs and {len(takes)} takes checked, {len(problems)} problems.")
sys.exit(1 if problems else 0)
