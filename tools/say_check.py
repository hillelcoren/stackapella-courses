"""Checks every "How to say it" file in say/ (docs/build-plan-2026-11-23.md, Brief K, in the Stackapella repository),
with Python's standard library only. A say file is a song's words written to be said: each line's words, each word's
plain sounds (the stressed syllable in capitals), and the id of a real person's spoken recording of the line. It's
`reviewed` false until a native speaker or a voice teacher has checked it; the app shows only a reviewed one whose every
line has its recording, never synth speech.

What it checks:
- it parses, and its fields are the format's (templates/format/say.json), no more;
- the song exists (templates/free or templates/library) and isn't in English, and the language is the song's;
- Latin says its style (church or classical);
- each line's sounds are its words, in order, each said plainly: letters, hyphens between syllables and apostrophes,
  one syllable in capitals when there's more than one;
- every word the parts sing is in some line, and no line says a word the song doesn't sing;
- clip ids are `<song>/<nn>`, each once; reviewed needs a reviewer (a role, never a name) and a clip on every line;
- on a Jewish song (Hebrew or Yiddish), no full divine name, in the words or the sounds (tools/divine_names_check.py).

Prints one line; exits 1 on any problem.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from divine_names_check import hits  # noqa: E402

FIELDS = {"song", "language", "style", "reviewed", "reviewer", "lines"}
LINE_FIELDS = {"words", "sounds", "clip"}
REVIEWERS = {"native speaker", "voice teacher"}
STYLES = {"la": {"church", "classical"}}
SAY = re.compile(r"^[A-Za-z']+(-[A-Za-z']+)*$")
JEWISH = ("he", "yi")
problems = []


def word_key(text):
    """A word as the check compares it: lowercase, letters (any script) and apostrophes only."""
    return re.sub(r"[^\w']", "", text.lower().replace("_", "")).strip("'")


def tokens(words):
    return [w for w in (word_key(t) for t in words.split()) if w]


def sung_words(song):
    """Every word the parts sing: syllables joined by their trailing dash, a held vowel's "(e)" left out."""
    found = set()
    for part in song.get("parts", []):
        word = ""
        for note in (part.get("guide") or {}).get("notes") or []:
            lyric = note.get("lyric")
            if not isinstance(lyric, str):
                continue
            syllable = re.sub(r"\([^)]*\)", "", lyric)
            if syllable.rstrip().endswith("-"):
                word += syllable.rstrip()[:-1]
                continue
            word += syllable
            if word_key(word):
                found.add(word_key(word))
            word = ""
        if word_key(word):
            found.add(word_key(word))
    return found


def find_song(song_id):
    for folder in ("templates/library", "templates/free"):
        path = ROOT / folder / f"{song_id}.json"
        if path.is_file():
            return json.loads(path.read_text())
    return None


def check(path):
    where = path.relative_to(ROOT)
    try:
        say = json.loads(path.read_text())
    except ValueError as e:
        problems.append(f"{where}: not JSON ({e})")
        return
    if not isinstance(say, dict):
        problems.append(f"{where}: an object, as templates/format/say.json")
        return
    if set(say) - FIELDS or {"song", "language", "reviewed", "lines"} - set(say):
        problems.append(f"{where}: fields {sorted(set(say))}, the format's are {sorted(FIELDS)}")
    if say.get("song") != path.stem:
        problems.append(f"{where}: song {say.get('song')!r}, the file is {path.stem}")
    song = find_song(path.stem)
    if song is None:
        problems.append(f"{where}: no song {path.stem} in templates/library or templates/free")
        return
    language = say.get("language")
    if language != song.get("language"):
        problems.append(f"{where}: language {language!r}, the song's is {song.get('language')!r}")
    if str(language or "en").startswith("en"):
        problems.append(f"{where}: How to say it is for a song not in English")
    style = say.get("style")
    if language in STYLES and style not in STYLES[language]:
        problems.append(f"{where}: style {style!r}: one of {sorted(STYLES[language])}")
    if language not in STYLES and style is not None:
        problems.append(f"{where}: style is for Latin (church or classical)")
    reviewed = say.get("reviewed")
    if not isinstance(reviewed, bool):
        problems.append(f"{where}: reviewed is true or false")
    reviewer = say.get("reviewer")
    if reviewer is not None and reviewer not in REVIEWERS:
        problems.append(f"{where}: reviewer {reviewer!r}: a role, {' or '.join(sorted(REVIEWERS))}, never a name")
    if reviewed is True and reviewer is None:
        problems.append(f"{where}: reviewed needs its reviewer (native speaker or voice teacher)")

    lines = say.get("lines")
    if not isinstance(lines, list) or not lines:
        problems.append(f"{where}: lines, one or more")
        return
    sung = sung_words(song)
    said = set()
    clips = set()
    for n, line in enumerate(lines, 1):
        at = f"{where} line {n}"
        if not isinstance(line, dict) or set(line) != LINE_FIELDS:
            problems.append(f"{at}: words, sounds and clip, no more")
            continue
        words = line["words"] if isinstance(line["words"], str) else ""
        line_tokens = tokens(words)
        if not line_tokens:
            problems.append(f"{at}: no words")
        sounds = line["sounds"] if isinstance(line["sounds"], list) else []
        if [word_key(s.get("word", "")) if isinstance(s, dict) else None for s in sounds] != line_tokens:
            problems.append(f"{at}: sounds are each word of {words!r}, in order")
        for s in sounds:
            if not isinstance(s, dict) or set(s) != {"word", "say"}:
                problems.append(f"{at}: a sound is a word and how it's said")
                continue
            plain = s["say"] if isinstance(s["say"], str) else ""
            if not SAY.match(plain):
                problems.append(f"{at}: {s['word']!r} said {plain!r}: letters, a hyphen between syllables, apostrophes")
            elif "-" in plain and sum(1 for syl in plain.split("-") if syl.isupper()) != 1:
                problems.append(f"{at}: {s['word']!r} said {plain!r}: its stressed syllable in capitals, one only")
        for w in line_tokens:
            said.add(w)
            if w not in sung:
                problems.append(f"{at}: {w!r} isn't sung in {path.stem}")
        clip = line["clip"]
        if clip is not None:
            if not isinstance(clip, str) or not re.fullmatch(rf"{re.escape(path.stem)}/\d{{2}}", clip):
                problems.append(f"{at}: clip {clip!r}: {path.stem}/<nn>")
            elif clip in clips:
                problems.append(f"{at}: clip {clip} twice")
            clips.add(clip)
        elif reviewed is True:
            problems.append(f"{at}: reviewed, but no recording (a real voice, never synth speech)")
        if language in JEWISH:
            text = " ".join([words] + [s.get("say", "") for s in sounds if isinstance(s, dict)])
            if hits(text, True):
                problems.append(f"{at}: a full divine name ({', '.join(sorted(set(hits(text, True))))}): write the substituted form")
    missing = sorted(sung - said)
    if missing:
        problems.append(f"{where}: no line says {', '.join(missing[:8])}{' and more' if len(missing) > 8 else ''}")


def main():
    files = sorted((ROOT / "say").glob("*.json")) if (ROOT / "say").is_dir() else []
    for path in files:
        check(path)
    if problems:
        print(f"say_check: {len(problems)} problem{'s' if len(problems) > 1 else ''}")
        for p in problems:
            print("  " + p)
        sys.exit(1)
    print(f"say_check: {len(files)} say file{'s' if len(files) != 1 else ''} fine")


if __name__ == "__main__":
    main()
