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
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SATB = {"soprano", "alto", "tenor", "bass"}
BARBERSHOP = {"tenor", "lead", "baritone", "bass"}
NEEDS = ["id", "version", "title", "tempo", "key", "timeSignature", "parts"]
PER_BAR = {"4/4": 4, "3/4": 3, "2/4": 2, "6/8": 2}
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
        rng = part.get("range")
        if isinstance(rng, dict):
            low, high = rng.get("low", 0), rng.get("high", 127)
        elif isinstance(rng, list) and len(rng) == 2:
            low, high = rng
        else:
            low, high = 0, 127
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
        pitches = [n.get("pitch") for n in notes if isinstance(n.get("pitch"), (int, float))]
        if rng is not None and pitches and (low, high) != (min(pitches), max(pitches)):
            problems.append(f"{where} {part.get('key')}: range {low} to {high}, but its notes run {min(pitches)} to {max(pitches)} (the page and the app show the range as the part's lowest and highest notes)")
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
    check_meters(song, where)
    if "hidden" in song and not isinstance(song["hidden"], bool):
        problems.append(f"{where}: \"hidden\" is true or false")
    check_rights(song, where)


def check_meters(song, where):
    """The optional metre changes (frontend's rules, 2026-11-13): after the pickup, strictly increasing, each a known
    metre different from the one before, each on a bar line of the metre before it (bars of 4, 3, 2 and, for 6/8, 2 beats)."""
    meters = song.get("meters")
    if meters is None:
        return
    if not isinstance(meters, list) or not meters:
        problems.append(f"{where}: meters must be a non-empty list of {{beat, timeSignature}}")
        return
    start, current = song.get("pickupBeats", 0) or 0, song.get("timeSignature")
    for i, m in enumerate(meters):
        beat, sig = (m or {}).get("beat"), (m or {}).get("timeSignature")
        if not isinstance(beat, (int, float)) or sig not in PER_BAR:
            problems.append(f"{where}: meters[{i}] needs a numeric beat and one of {', '.join(PER_BAR)}")
            return
        if beat <= start:
            problems.append(f"{where}: meters[{i}] at beat {beat} must come after the pickup and after the change before it")
            return
        if sig == current:
            problems.append(f"{where}: meters[{i}] repeats the metre before it ({sig})")
        bars = (beat - start) / PER_BAR.get(current, 4)
        if abs(bars - round(bars)) > 1e-6:
            problems.append(f"{where}: meters[{i}] at beat {beat} is not on a bar line of {current}")
        start, current = beat, sig


ROLES = {"music", "words", "translation", "arrangement", "edition"}
COUNTRY = re.compile(r"^[A-Z]{2}$")


def check_rights(song, where):
    """Rights by country (the Stackapella repository's docs/geo-rights-plan.md): an open song names its makers
    (an empty list when all of it is traditional or anonymous) and its first printing, or, known only from a
    manuscript, the year it was made. Missing data would withhold it everywhere."""
    def year(value):
        return isinstance(value, int) and not isinstance(value, bool) and 1000 <= value <= 2100

    makers, printed, made = song.get("makers"), song.get("firstPublished"), song.get("made")
    if song.get("reviewed") and makers is None:
        problems.append(f"{where}: an open song needs makers (an empty list if all of it is traditional or anonymous)")
    if song.get("reviewed") and printed is None and made is None:
        problems.append(f"{where}: an open song needs firstPublished (or made, for a song known only from a manuscript)")
    for maker in makers or []:
        if not isinstance(maker, dict) or not isinstance(maker.get("name"), str) or not maker["name"]:
            problems.append(f"{where}: a maker without a name")
            continue
        name = maker["name"]
        if maker.get("role") not in ROLES:
            problems.append(f"{where}: {name}'s role {maker.get('role')!r} isn't one of {', '.join(sorted(ROLES))}")
        if not year(maker.get("died")) and maker.get("died") not in ("living", "unknown"):
            problems.append(f"{where}: {name} died {maker.get('died')!r}: a year, \"living\" or \"unknown\"")
        if "nationality" in maker and not COUNTRY.match(str(maker["nationality"])):
            problems.append(f"{where}: {name}'s nationality {maker['nationality']!r} isn't an ISO 3166 code")
    if printed is not None:
        if not isinstance(printed, dict) or not year(printed.get("year")):
            problems.append(f"{where}: firstPublished needs a year")
        elif "country" in printed and not COUNTRY.match(str(printed["country"])):
            problems.append(f"{where}: firstPublished's country {printed['country']!r} isn't an ISO 3166 code")
    if made is not None and not year(made):
        problems.append(f"{where}: made {made!r} isn't a year")


songs = sorted(p for p in (ROOT / "templates").glob("*/*.json") if p.name != "index.json" and p.parent.name != "format")
for song in songs:
    check(song)



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
    keep = {k: song.get(k) for k in ("tempo", "key", "timeSignature", "meters", "pickupBeats", "sections")}
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
                # A staged next version (<id>.next.json) is compared with the staged file at ref, never the live one.
                before[(old["id"], name.endswith(".next.json"))] = old
    for path in songs:
        if path.parent.name not in ("free", "library"):
            continue
        try:
            song = json.loads(path.read_text())
        except ValueError:
            continue
        old = before.get((song.get("id"), path.name.endswith(".next.json"))) if isinstance(song, dict) else None
        if not old:
            continue
        was, now = old.get("version", 0), song.get("version", 0)
        where = path.relative_to(ROOT)
        if now < was:
            problems.append(f"{where}: version {now} is below {was} at {ref}")
        elif now == was and music(song) != music(old):
            problems.append(f"{where}: its notes changed at version {now} since {ref}; give it version {now + 1} (production's sync refuses the same version with other notes)")


def check_staged():
    """A staged next version (templates/library/<id>.next.json, the Stackapella repository's staged-version sync): the
    same id as a live song, a higher version than it, and never reviewed (the sync refuses a reviewed staged file)."""
    live = {}
    for path in songs:
        if path.parent.name in ("free", "library") and not path.name.endswith(".next.json"):
            try:
                song = json.loads(path.read_text())
            except ValueError:
                continue
            if isinstance(song, dict):
                live[song.get("id")] = song
    for path in songs:
        if not path.name.endswith(".next.json"):
            continue
        where = path.relative_to(ROOT)
        try:
            song = json.loads(path.read_text())
        except ValueError:
            continue
        if not isinstance(song, dict) or path.name != f"{song.get('id')}.next.json":
            problems.append(f"{where}: a staged file is named after its song's id")
            continue
        if song.get("reviewed"):
            problems.append(f"{where}: a staged next version must not be reviewed (the sync refuses it)")
        if "hidden" in song:
            problems.append(f"{where}: \"hidden\" belongs on the live file, not a staged next version (the sync refuses it)")
        current = live.get(song["id"])
        if current is None:
            problems.append(f"{where}: no live song {song['id']} to stage a next version of")
        elif song.get("version", 0) <= current.get("version", 0):
            problems.append(f"{where}: version {song.get('version')} must be above the live version {current.get('version')}")


check_staged()
since = sys.argv[sys.argv.index("--since") + 1] if "--since" in sys.argv[1:-1] else "origin/main"
check_versions(since)

for problem in problems:
    print(problem)
print(f"{len(songs)} songs and {len(takes)} takes checked, {len(problems)} problems.")
sys.exit(1 if problems else 0)
