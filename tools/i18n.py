"""The courses in other languages: each language's words, kept beside the courses and written into them.

Every word people read in a course is { "en": "..." } (course/format/README.md). A translation adds its own key,
{ "en": "Find your voice", "es": "Encuentra tu voz" }, and the app shows it in that language (web/js/i18n.js).

Many course files are generated (tools/*_course.py rewrite them whole), so a translation can't live only inside them.
Each language keeps its words in i18n/<lang>/<course>.json, one map from the English to the translation, and `apply`
writes them into every course file. A word whose English changed finds no translation and shows in English until
it's translated again, never a stale sentence (docs/languages-plan.md, "Keeping current").

    python3 -I tools/i18n.py apply                    every language's words into every course file (run it after
                                                      a course generator, or after editing a language's file)
    python3 -I tools/i18n.py status [lang]            per course: words translated, missing, and stale entries
    python3 -I tools/i18n.py missing <lang> <course>  the course's untranslated words, as JSON with where each is used
    python3 -I tools/i18n.py add <lang> <course> <file.json>
                                                      merges a JSON map {english: translation} into the language's file

<course> is free (course/course.json), cooldown, songs (every song course in course/songs: one file, since their
words repeat), or a Plus course's id. tools/course_check.py fails when a course file and its language file disagree.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COURSE = ROOT / "course"
I18N = ROOT / "i18n"
LANG = re.compile(r"^[a-z]{2}(-[A-Z]{2})?$")
STRING = r'"(?:[^"\\]|\\.)*"'
# A word in a course file's text: an object whose first key is "en", then any other languages, and nothing else.
WORD = re.compile(r'\{(\s*)"en":(\s*)(' + STRING + r')((?:\s*,\s*"[a-z]{2}(?:-[A-Z]{2})?":\s*' + STRING + r')*)(\s*)\}')
OTHER = re.compile(r'"([a-z]{2}(?:-[A-Z]{2})?)":\s*(' + STRING + ')')


def courses():
    """Each course key and its files."""
    out = {"free": [COURSE / "course.json"]}
    if (COURSE / "cooldown.json").exists():
        out["cooldown"] = [COURSE / "cooldown.json"]
    for c in json.loads((COURSE / "plus" / "courses.json").read_text())["courses"]:
        if c.get("file"):
            out[c["id"]] = [COURSE / "plus" / c["file"]]
    out["songs"] = sorted(f for f in (COURSE / "songs").glob("*.json") if f.name != "index.json")
    return out


def languages():
    return sorted(d.name for d in I18N.iterdir() if d.is_dir() and LANG.match(d.name)) if I18N.exists() else []


def table(lang, key):
    path = I18N / lang / f"{key}.json"
    return json.loads(path.read_text()) if path.exists() else {}


def is_word(v):
    return isinstance(v, dict) and isinstance(v.get("en"), str) and bool(v) and all(LANG.match(k) and isinstance(x, str) for k, x in v.items())


def each_word(obj, where=""):
    """Every word in a course's data, in file order, with where it is (the nearest ids and the field)."""
    if isinstance(obj, dict):
        here = f"{where}/{obj['id']}" if isinstance(obj.get("id"), str) else where
        for k, v in obj.items():
            if is_word(v):
                yield v, f"{here}.{k}"
            else:
                yield from each_word(v, here if k != "id" else where)
    elif isinstance(obj, list):
        for x in obj:
            if is_word(x):
                yield x, where
            else:
                yield from each_word(x, where)


def wanted(data, tables):
    """The data with every word's translations set from the tables, and removed where a table has none (or there's
    no table for its language at all)."""
    for word, _ in each_word(data):
        for lang in [k for k in word if k != "en" and k not in tables]:
            del word[lang]  # a language with no file here: every translation comes from i18n/
        for lang, t in tables.items():
            if word["en"] in t:
                word[lang] = t[word["en"]]
            else:
                word.pop(lang, None)
    return data


def apply_file(path, tables):
    """Writes the tables' words into one course file's text, leaving its layout as it is. True when it changed."""
    text = path.read_text()
    expected = wanted(json.loads(text), tables)

    def rewrite(m):
        lead, gap, en_lit, rest, tail = m.groups()
        en = json.loads(en_lit)
        others = {k: json.loads(v) for k, v in OTHER.findall(rest) if k in tables}
        for lang, t in tables.items():
            if en in t:
                others[lang] = t[en]
            else:
                others.pop(lang, None)
        sep = "," + lead if "\n" in lead else ", "
        extra = "".join(f'{sep}"{k}":{gap}{json.dumps(v, ensure_ascii=False)}' for k, v in others.items())
        return "{" + lead + '"en":' + gap + en_lit + extra + tail + "}"

    new = WORD.sub(rewrite, text)
    if json.loads(new) != expected:
        sys.exit(f"FAIL {path.relative_to(ROOT)}: a word's text isn't in the shape this tool rewrites; nothing written")
    if new != text:
        path.write_text(new)
        return True
    return False


def disagreements(lang=None):
    """Where a course file's words and the language files differ: (course, file, where, what)."""
    out = []
    langs = [lang] if lang else languages()
    for key, files in courses().items():
        tables = {la: table(la, key) for la in langs}
        for f in files:
            for word, where in each_word(json.loads(f.read_text())):
                for la, t in tables.items():
                    if word.get(la) != t.get(word["en"]):
                        out.append((key, f, where, la))
                out += [(key, f, where, la) for la in word if la != "en" and la not in tables and not lang]
    return out


def main(argv):
    if not argv or argv[0] not in ("apply", "status", "missing", "add"):
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    all_courses = courses()
    if cmd == "apply":
        langs = languages()
        changed = 0
        for key, files in all_courses.items():
            tables = {la: table(la, key) for la in langs}
            changed += sum(apply_file(f, tables) for f in files)
        print(f"i18n: {', '.join(langs) or 'no languages'} written into {changed} changed course files")
    elif cmd == "status":
        for la in args[:1] or languages():
            for key, files in all_courses.items():
                t = table(la, key)
                if not t:
                    continue
                en = {w["en"] for f in files for w, _ in each_word(json.loads(f.read_text()))}
                stale = [e for e in t if e not in en]
                print(f"{la} {key}: {len(en & set(t))} of {len(en)} translated, {len(en - set(t))} missing, {len(stale)} stale")
                for e in stale:
                    print(f"    stale: {e[:100]}")
    elif cmd == "missing":
        la, key = args
        t = table(la, key)
        seen = {}
        for f in all_courses[key]:
            for word, where in each_word(json.loads(f.read_text())):
                if word["en"] not in t:
                    seen.setdefault(word["en"], []).append(where)
        print(json.dumps([{"en": e, "where": w[:3]} for e, w in seen.items()], ensure_ascii=False, indent=1))
    elif cmd == "add":
        la, key, src = args
        if not LANG.match(la) or key not in all_courses:
            sys.exit(f"FAIL unknown language or course: {la} {key}")
        t = table(la, key)
        new = json.loads(Path(src).read_text())
        bad = [e for e, x in new.items() if not isinstance(x, str) or not x.strip()]
        if bad:
            sys.exit(f"FAIL empty or non-text translations: {bad[:5]}")
        t.update(new)
        order = [w["en"] for f in all_courses[key] for w, _ in each_word(json.loads(f.read_text()))]
        rank = {e: i for i, e in reversed(list(enumerate(order)))}
        t = dict(sorted(t.items(), key=lambda kv: rank.get(kv[0], len(rank))))
        (I18N / la).mkdir(parents=True, exist_ok=True)
        (I18N / la / f"{key}.json").write_text(json.dumps(t, ensure_ascii=False, indent=1) + "\n")
        print(f"i18n: {len(new)} words into i18n/{la}/{key}.json ({len(t)} in all); run apply")


if __name__ == "__main__":
    main(sys.argv[1:])
