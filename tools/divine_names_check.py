"""Fail when a Jewish song's content writes out a full divine name (Hillel's rule).

Usage: python3 tools/divine_names_check.py [content dir, default: this repo]

Rule (Hillel): on Jewish song pages a full divine name never appears, in Hebrew script or in transliteration, in any
language. We write and sing only the substituted forms (Kel, Keli, Elokeinu, Elokim, Adoshem, Shakai, Hashem, ה'), and our own words never use God, Lord, Almighty, Dios, Señor or Todopoderoso as a title for the Name (quotations, book titles and source lines aside).
Jewish songs are the song files whose language is Hebrew or Yiddish. For each one this checks its song file, its
stories (en and es), its meaning file, its course file (every language in it) and its course facts.
"""
import glob
import json
import os
import re
import sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LIB = os.path.join(ROOT, 'templates/library')

# Full forms in transliteration, any language. Capitalised, whole words.
TRANSLIT = re.compile(r"\b(Elohim|Elohei|Eloheinu|Elohenu|Elohai|Elohecha|Elohekha|Eloha|Adonai|Adonoy|Adonay|Adonoi|Adonaj|Adonoj|"
                      r"Shaddai|Shadai|Yahweh|Yahveh|Jehovah|Jehová|YHWH|Tzevaot|Tzeva'ot|Tsevaot|Sabaoth)\b")
# A name split off by an apostrophe or hyphen, in any case ("Ke'eloheinu", "Ke-Elohenu"). The hymn title's fused
# spellings (Ein Keloheinu, En Kelohenu, Ayn Kaylohaynu) are its name and stay (Hillel, 2026-11-11; lead, 2026-11-13).
SPLIT = re.compile(r"['\u2019-](?:[Ee]loh(?:im|ei|einu|enu|ai|echa|ekha|a)|[Aa]donai|[Ss]hadd?ai)\b")
URL = re.compile(r"https?://\S+")
# "El" and "Eli" as the name. In English text anywhere; in Spanish only mid-sentence (after a lowercase word or a
# comma), since a capital "El" opening a sentence is the article (backend's rule, 2026-11-13).
EL = re.compile(r"\b(El|Eli)\b")
EL_ES = re.compile(r"(?:[a-záéíóúñü]|,) (El|Eli)\b")
EL_ALLOWED = ('Eli Ziyyon', 'Eli Tziyon', 'Eli Zion', 'El Paso')
# Titles standing for the Name in our own words (Hillel: our English says Hashem, never God or Lord; our Spanish never
# Dios or Señor). Arranger, 2026-11-14: "our Lord" and "Lord of the world" slipped into two Abouts.
TITLE_EN = re.compile(r"\b(God|Lord|LORD|Almighty)\b")
TITLE_ES = re.compile(r"\b(Dios|Señor|Todopoderoso)\b")
# Hebrew script: compare with vowels and cantillation removed, whole words.
HEB_POINTS = re.compile('[֑-ׇ]')
HEB_FULL = {'יהוה', 'אלהים', 'אלוהים', 'אלהינו', 'אלוהינו', 'אלהי', 'אלוהי', 'אלהיך', 'אלוהיך', 'אדני', 'שדי', 'צבאות'}
HEB_WORD = re.compile('[א-ת֑-ׇ]+')
# El and Eli in Hebrew can only be told from "el" (to) and "al" (don't) by their vowels: tsere under the alef.
HEB_EL = re.compile('(?<![א-ת֑-ׇ])א[֑-֯]*ֵ[֑-֯]*ל[֑-֯]*(ִ[֑-֯]*י)?(?![א-ת֑-ׇ])')


def hits(text, english):
    text = URL.sub('', text)
    found = [m.group(0) for m in TRANSLIT.finditer(text)]
    found += [m.group(0) for m in SPLIT.finditer(text)]
    for m in (EL if english else EL_ES).finditer(text):
        if not any(a in text[max(0, m.start() - 12):m.end() + 12] for a in EL_ALLOWED):
            found.append(m.group(1))
    for w in HEB_WORD.findall(text):
        if HEB_POINTS.sub('', w) in HEB_FULL:
            found.append(w)
    found += [m.group(0) for m in HEB_EL.finditer(text)]
    # titles: our own words only, so quoted titles and quotations, italic book titles and a footnote's source line are
    # left out; "Almighty Hashem" (our substitution) and Lord Byron are fine
    own = re.sub(r'"[^"]*"|“[^”]*”|\*[^*]+\*', '', text)
    if not own.lstrip().startswith(('- [^', 'alsoKnownAs:')):  # a source line, or names others call it by
        own = own.replace('Almighty Hashem', '').replace('Lord Byron', '').replace('Todopoderoso Hashem', '')
        found += [m.group(0) for m in (TITLE_EN if english else TITLE_ES).finditer(own)]
    return found


def walk(node, english, path=''):
    """Yield (path, string, is_english) for every string in a JSON value; es/de branches are not English."""
    if isinstance(node, dict):
        for k, v in node.items():
            yield from walk(v, english and k not in ('es', 'de'), path + '.' + str(k))
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from walk(v, english, '%s[%d]' % (path, i))
    elif isinstance(node, str):
        yield path, node, english


def jewish_slugs():
    out = []
    for f in sorted(glob.glob(os.path.join(LIB, '*.json')) + glob.glob(os.path.join(ROOT, 'templates/free/*.json'))):
        if f.endswith('.next.json') or f.endswith('index.json'):
            continue
        try:
            t = json.load(open(f))
        except (ValueError, OSError):
            continue
        if t.get('language') in ('he', 'yi'):
            out.append((t.get('id') or os.path.basename(f)[:-5], f))
    return out


problems = []


def report(where, text, english):
    for h in hits(text, english):
        problems.append('%s: "%s"' % (where, h))


facts = json.load(open(os.path.join(ROOT, 'tools/song_facts.json')))
slugs = jewish_slugs()
for slug, song_file in slugs:
    for p, s, en in walk(json.load(open(song_file)), True):
        report('%s%s' % (os.path.relpath(song_file, ROOT), p), s, en)
    for rel, en in (('stories/%s.md' % slug, True), ('stories/es/%s.md' % slug, False)):
        f = os.path.join(LIB, rel)
        if os.path.exists(f):
            for n, line in enumerate(open(f), 1):
                report('templates/library/%s:%d' % (rel, n), line, en)
    for rel in ('templates/library/meaning/%s.json' % slug, 'course/songs/%s.json' % slug,
                'templates/library/stories/media/%s/media.json' % slug):
        f = os.path.join(ROOT, rel)
        if os.path.exists(f):
            for p, s, en in walk(json.load(open(f)), True):
                report(rel + p, s, en)
    for p, s, en in walk(facts.get(slug, []), True):
        report('tools/song_facts.json:%s%s' % (slug, p), s, en)

for p in problems:
    print(p)
print('divine names: %d Jewish songs checked, %d problems' % (len(slugs), len(problems)))
sys.exit(1 if problems else 0)
