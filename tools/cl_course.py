"""Classical singing basics (docs/courses/classical-singing.md in the app's repo): writes
course/plus/classical-singing/course.json. Built from the courses lead's outline, as revised by a voice-teacher
review and a game-design review: joined lines on vowels first, then the words; a clean start; one breath a phrase;
the leaning note and a slide on purpose; ending on Caro mio ben, kept as a song.

Its lines, each read from a scan printed before 1927, bar by bar, then checked again (the arranger's review):
- Concone, 50 Lecons de chant pour le medium de la voix, Op. 9, No. 1 (Edition Peters No. 980, plate 6437,
  archive.org/details/50leconsdechantp00conc, leaf n3), a wordless vocalise in C: bars 9 to 16, sung on "ah".
- Vaccai, Practical Method of Italian Singing (Boston: Russell, 1878, plate 204, archive.org/details/
  imslp-pratico-de-canto-vaccai-nicola): Lesson I No. 1, the scale (leaf n8), No. 2, the thirds (leaf n9), and
  Lesson VIII No. 11, the appoggiatura (leaf n17), sung as the page's "Ex." staffs write it out.
- Caro mio ben, as Parisotti printed it (Schirmer, 1894; the library's caro-mio-ben template, the arranger's).
- Brahms's Wiegenlied, Op. 49 No. 4 (1868): the library's brahms-lullaby template.

A line is `beat:length midi [syllable], ...` as printed (beats in quarter notes, re-timed to start at 0), turned
into steps from the singer's comfortable note by a reference pitch per source, so each sits in the course's span.
The checks fail the build on:
- a sung note outside -5 to +9 (-6 only for a passing note of half a beat or less);
- `legato` on a step whose lyrics carry a consonant (c, p, t and s rightly stop the sound; the scorer hears a
  break as a dip in loudness at the change), or on a step with fewer than four joins;
- a `rhythm` step with fewer than four timed moments, or `rhythm` in unit 1 or 2;
- an `entry` step as a lesson's last scored step, or a `legato` step as one in the course's first lesson;
- the house words: no "star" or "stars", no em dashes, none of the words the voice-teacher review ruled out
  (operatic, push, belt, support, placement...), and no letter names.

    python3 -I tools/cl_course.py && python3 -I tools/coursefmt.py course/plus/classical-singing/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/classical-singing/course.json"
CARO_TEMPLATE = REPO / "templates/library/caro-mio-ben.json"
WRITE = CARO_TEMPLATE.exists()

BANNED = re.compile(r"\bstars?\b|—|operatic|\bbig voice|\bcover\b|\bdarken|\bproject\b|\bpush|\bbelt\b|\bpower|\blouder\b"
                    r"|\bsupport|open your throat|\byawn|\bpalate|\bplacement|the mask|\btall vowel|\bround vowel|\bperiod\b|\bbloom", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")  # a note's letter name ("A" alone is the article)
VOWELS = re.compile(r"^[aeiouàèéìòù‿]+$|^ah$|^oo$", re.I)

COLOUR = 3
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
EPS = 1e-9
LOW, HIGH = -5, 9

SAFE = "stop if anything tightens or hurts"
OWN = ("Your own voice", f"An easy medium volume; {SAFE}")
EASY = ("Tall and easy", "Jaw loose, shoulders down")
JOINED = "Scored on where each note lands, and on the notes joined."
LANDS = "Scored on where each note lands."
LINE = "Scored on where each note lands, and on the last note ending steady."  # only where the last note is held: Vaccai's end on short notes, so they use LANDS
BEAT = "Scored on your notes on pitch and on the beat."
CHOSE = "Scored on the rounds you got right first time."
KEEP = "classical.first-phrase"


def EN(text):
    assert not BANNED.search(text) and not LETTERS.search(text), text
    return {"en": text}


def num(x):
    x = round(x, 6)
    return int(x) if x == int(x) else x


def M(text, ref):
    """`beat:length midi [syllable], ...` as printed, into notes in steps from the comfortable note (midi - ref)."""
    out = []
    for token in text.split(","):
        when, midi, *word = token.split()
        beat, length = when.split(":")
        n = {"beat": num(float(beat)), "length": num(float(length)), "step": int(midi) - ref}
        if word and word[0] != "_":
            n["lyric"] = word[0]
        out.append(n)
    start = out[0]["beat"]
    return [dict(n, beat=num(n["beat"] - start)) for n in out]


def on(notes, lyric="ah"):
    """The line on one vowel: the first note of each syllable takes it, a held melisma note keeps none."""
    return [{k: v for k, v in dict(n, lyric=lyric).items() if k != "lyric" or "lyric" in n or i == 0}
            for i, n in enumerate(notes)]


def vowels_of(notes):
    """The line on its own vowels (the classical teacher's "vowels first"): each syllable's vowels, no consonants."""
    out = []
    for n in notes:
        m = dict(n)
        if "lyric" in n:
            v = "".join(ch for ch in n["lyric"].lower() if ch in "aeiouàèéìòù‿")
            assert v, n
            m["lyric"] = v
        out.append(m)
    return out


def end_of(notes):
    return max(n["beat"] + n["length"] for n in notes)


def shift(notes, by):
    return [dict(n, beat=num(n["beat"] + by)) for n in notes]


class Song:
    """A library template's top part (its tune) and chords, in steps from the comfortable note (midi - ref)."""

    def __init__(self, name, ref):
        data = json.loads((REPO / "templates" / "library" / f"{name}.json").read_text())
        self.name, self.tempo, self.ref, self.key = name, data["tempo"], ref, KEYS[data["key"].rstrip("m")]
        self.tune = [(n["beat"], n["length"], n["pitch"] - ref, n.get("lyric")) for n in data["parts"][0]["guide"]["notes"]]
        # A chord's root as a pitch class from the comfortable note.
        self.chords = [(c["beat"], (c["root"] - ref) % 12, c["quality"]) for c in data["chords"]]
        self.sections = {s.get("name"): s["phrases"] for s in data["sections"]}
        self.bounds = {b for s in data["sections"] for p in s["phrases"] for b in p}

    def notes(self, frm, to):
        """The tune from `frm` to `to`, re-timed to start at 0, words kept (a note with no word is held over)."""
        assert frm in self.bounds and to in self.bounds, f"{self.name}: {frm} to {to} is not whole phrases"
        return [{"beat": num(b - frm), "length": num(length), "step": p, **({"lyric": w} if w and w != "~" else {})}
                for b, length, p, w in self.tune if frm <= b < to]

    def chords_at(self, frm, to):
        sounding = [c for c in self.chords if c[0] <= frm + EPS][-1]
        inside = [c for c in self.chords if frm + EPS < c[0] < to - EPS]
        return [{"beat": num(b - frm), "root": r, "quality": q} for b, r, q in [(frm,) + sounding[1:]] + inside]


# ---- The lines ----

# Concone No. 1, bars 9 to 16 (C major, Moderato; D4 to E5): four two-bar groups, a quarter rest after each.
# G4 at the comfortable note: D4 is -5, E5 +9 (a half note reached by step), the long notes in the middle.
CONCONE = M("0:2 67, 2:2 71, 4:2 72, 6:1 67, 8:2 74, 10:2 67, 12:2 76, 14:1 72, 16:2 67, 18:2 71, 20:2 72, 22:1 67, "
            "24:1 65, 25:1 67, 26:1 64, 27:1 67, 28:3 62", 67)
CONCONE_TEMPO = 80
CONCONE_END = [n for n in CONCONE if n["beat"] >= 16]  # bars 13 to 16, ending on a 3-beat note before the rest

# Vaccai, Lesson I No. 1, the scale, bars 1 to 8 (C major, Adagio; C4 to D5): "Manca sollecita / Più dell'usato, /
# Ancorchè s'agiti / Con lieve fiato" (Metastasio), with Vaccai's own syllable split: each consonant joins the
# syllable after it, so the vowel fills its notes ("Ma-nca so-lle-ci-ta"). Bar 7 prints "re"; the verse is "lieve".
# C4 at -5: D5 is +9.
SCALE = M("0:2 60 Ma, 2:1 62 nca, 3:1 64 so, 4:1 65 lle, 5:1 67 ci, 6:1 69 ta, 8:2 62 Più, 10:1 64 de, 11:1 66 ll'u, "
          "12:1 67 sa, 13:1 69 _, 14:1 70 to, 16:2 74 A, 18:1 72 nco, 19:1 70 rchè, 20:1 69 s'a, 21:1 67 gi, 22:1 65 ti, "
          "24:2 69 Co, 26:1 67 nlie, 27:1 65 ve, 28:1 64 fia, 29:1 62 _, 30:1 60 to", 65)
SCALE_TEMPO = 66

# Vaccai, Lesson I No. 2, the thirds (F major, 6/8 Andantino; C4 to D5): "Semplicetta tortorella, / che non vede il
# suo periglio, / per fuggir dal crudo artiglio / vola in grembo al cacciator." The whole lesson; its first
# phrase ends on "periglio" (beat 12). Same placement as the scale.
THIRDS = M("0:1 65 Sem, 1:0.5 69 pli, 1.5:1 67 cet, 2.5:0.5 70 ta, 3:1 67 tor, 4:0.5 70 to, 4.5:1 69 rel, 5.5:0.25 72 la, "
           "6:1 72 Che, 7:0.5 69 non, 7.5:1 70 ve, 8.5:0.5 67 de‿il, 9:1 69 suo, 10:0.5 65 pe, 10.5:0.5 69 ri, 11:0.5 67 glio, "
           "12:1 65 Per, 13:0.5 69 fug, 13.5:1 67 gir, 14.5:0.5 70 da, 15:1 67 cru, 16:0.5 70 do‿ar, 16.5:1 69 ti, 17.5:0.25 72 glio, "
           "18:1 69 Vo, 19:0.5 65 la‿in, 19.5:1 67 grem, 20.5:0.5 64 bo‿al, 21:1 65 cac, 22:0.5 62 cia, 22.5:1 60 tor, "
           "24:1 60 Per, 25:0.5 64 fug, 25.5:1 62 gir, 26.5:0.5 65 da, 27:1 64 cru, 28:0.5 67 do‿ar, 28.5:0.5 67 ti, 29:0.5 65 glio, "
           "30:1 67 per, 31:0.5 70 fug, 31.5:1 69 gir, 32.5:0.5 72 da, 33:1 70 cru, 34:0.5 74 do‿ar, 34.5:0.5 74 ti, 35:0.5 72 glio, "
           "36:1 74 Vo, 37:0.5 70 la‿in, 37.5:1 72 grem, 38.5:0.5 69 bo‿al, 39:1 70 cac, 40:0.5 67 cia, 40.5:1 69 tor, "
           "42:1 70 vo, 43:0.5 67 la‿in, 43.5:1 69 grem, 44.5:0.5 65 bo‿al, 45:1 67 cac, 46:0.5 64 cia, 46.5:1 65 tor", 65)
THIRDS_FIRST = [n for n in THIRDS if n["beat"] < 12]
THIRDS_TEMPO = 96  # 6/8 Andantino: a dotted quarter at 64

# Vaccai, Lesson VIII No. 11, bars 1 to 4 (G major, 6/8 Andante): "Senza l'amabile / Dio di Citera". Each small
# note sung as the page's "Ex." writes it out: on "ma" the leaning G takes the whole quarter before F sharp; on
# "te" the leaning C takes a quarter of the dotted quarter, then B. A4 at the comfortable note.
LEAN = M("0:1.5 67 Sen, 1.5:1 67 za, 2.5:0.5 69 l'a, 3:1 67 ma, 4:0.5 66 bi, 4.5:1 66 le, "
         "6:1.5 72 Dio, 7.5:1 72 di, 8.5:0.5 74 Ci, 9:1 72 te, 10:0.5 71 _, 10.5:1 71 ra", 69)
LEAN_TEMPO = 84

# Brahms's Wiegenlied and Caro mio ben, both in E flat: do (E flat) at -5 from the comfortable note.
BRAHMS = Song("brahms-lullaby", 68)
CARO = Song("caro-mio-ben", 68) if WRITE else None
# Until the template is in: bars 5 to 9 as transcribed (and checked by the arranger), for a dry run only.
CARO_DRAFT = M("0:1 75 Ca, 1:0.75 74 ro, 1.75:0.25 72 mio, 2:2 70 ben, 4:1 72 cre, 5:0.75 70 di, 5.75:0.25 68 mi‿al, "
               "6:2 67 men, 8:1 68 sen, 9:0.5 67 za, 9.5:0.5 65 di, 10:2 70 te, 12:1 63 lan, 13:0.5 62 gui, 13.5:0.5 63 sce‿il, "
               "14:1 67 cor, 15:1 65 _", 68)


# ---- Steps ----

def card(title, detail):
    assert len(title) <= 40 and len(title.split()) <= 9, f"a card title is short: {title}"
    assert len(detail) <= 72 and "\n" not in detail and ". " not in detail, f"a card's detail is one line: {detail}"
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="phrase"):
    assert len(cards) <= 3, headline
    assert any(SAFE in d for _, d in cards), f"every learn step carries the safety line: {headline}"
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def find(text, notes, tempo):
    """Wait for me: each note waits until you're on it."""
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes}}


def play(text, notes, tempo, measures, *, chords=None, **extra):
    """Hear it, then sing it back (`turn`); with chords, sing it over them (`turn: false`, the guide with you)."""
    ex = {"tempo": tempo, "notes": notes, "turn": not chords}
    if chords:
        ex["chords"] = chords
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def choose(text, tempo, rounds):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": [
        {"prompt": EN(p), "clips": clips, "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


def selfcheck(text, tempo, notes, questions):
    return {"kind": "selfcheck", "text": EN(text),
            "exercise": {"tempo": tempo, "model": {"notes": notes}, "along": True, "questions": [EN(q) for q in questions]}}


def bullseye(text, tempo, echoes):
    return {"kind": "bullseye", "text": EN(text), "exercise": {"tempo": tempo, "echoes": echoes},
            "measures": EN("Scored on where each note lands, from its first sound.")}


def clip(notes):
    return {"notes": notes}


def gapped(notes, keep=0.6):
    """The same notes, each cut short: a gap before the next (the guide starts each one again)."""
    return [dict(n, length=num(n["length"] * keep)) for n in notes]


# ---- The checks ----

def joins(notes):
    ordered = sorted(notes, key=lambda n: n["beat"])
    return sum(1 for a, b in zip(ordered, ordered[1:]) if abs(a["beat"] + a["length"] - b["beat"]) < EPS and a["step"] != b["step"])


def timed_moments(notes, tempo):
    """scoreTake's timed moments: the first note, each note after a rest of 0.1 s or more, each change of a
    semitone or more."""
    bs = 60 / tempo
    ordered = sorted(notes, key=lambda n: n["beat"])
    k = 0
    for i, n in enumerate(ordered):
        if i == 0 or (n["beat"] - (ordered[i - 1]["beat"] + ordered[i - 1]["length"])) * bs >= 0.1 or n["step"] != ordered[i - 1]["step"]:
            k += 1
    return k


def scored(step):
    return step["kind"] in ("play", "choose", "bullseye") and not step.get("exercise", {}).get("unscored")


def check(lid, unit, steps):
    last = max(i for i, s in enumerate(steps) if scored(s))
    for i, step in enumerate(steps):
        where = f"cl-{lid} step {i + 1}"
        ex = step.get("exercise", {})
        if step["kind"] in ("play", "try"):
            for n in ex["notes"]:
                assert n["beat"] >= 0 and n["length"] > 0, f"{where}: a note before beat 0, or with no length"
                assert LOW <= n["step"] <= HIGH or (n["step"] == LOW - 1 and n["length"] <= 0.5), \
                    f"{where}: step {n['step']} at beat {n['beat']} is outside {LOW} to {HIGH}"
        if step["kind"] != "play":
            continue
        if ex.get("score") == "legato":
            bad = [n["lyric"] for n in ex["notes"] if "lyric" in n and not VOWELS.match(n["lyric"])]
            assert not bad, f"{where}: legato only on vowels, not {bad}"
            assert joins(ex["notes"]) >= 4, f"{where}: a legato step needs four joins or more"
            assert not (lid == "1-joined" and i == last), f"{where}: the course's first lesson shows the joins before scoring them"
        if "rhythm" in ex:
            assert "score" not in ex, f"{where}: rhythm only on a default-scored step"
            assert timed_moments(ex["notes"], ex["tempo"]) >= 4, f"{where}: a rhythm step needs four timed moments"
            assert unit > 2, f"{where}: units 1 and 2 aren't timed"
        if ex.get("score") == "entry":
            assert i != last, f"{where}: entry has no one-star floor, so it's never the lesson's last scored step"


# ---- The facts ----
# Each lesson page's "Did you know?" (2026-11-08): read in its source (the original printing wherever there is one),
# then read again by a second, independent check, which corrected four; every person named has died. The four
# challenges fold into the page before them and carry none.

def fact(fid, text, source, url, **extra):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url, **extra}


VACCAI = "https://archive.org/details/imslp-pratico-de-canto-vaccai-nicola"
CONCONE_SCAN = "https://archive.org/details/50leconsdechantp00conc"
FACTS = {
    "1-joined": fact("vaccai-consonant-next-syllable", "In the first lesson of his Practical Method, Nicola Vaccai split the words oddly, joining each consonant to the next syllable so the vowel fills its notes. This, he wrote, would also help a singer learn the legato style.",
                     "Vaccai, Practical Method of Italian Singing (Boston: Russell, 1878), Lesson I, Internet Archive", VACCAI),
    "1-start": fact("caccini-third-below", "In his 1602 songbook Le nuove musiche, Giulio Caccini noted that some singers began their first note a third below. The habit had grown so common, he wrote, and some lingered there so long, that it tired the ear; beginners should seldom use it.",
                    "Caccini, Le nuove musiche (Florence, 1602), preface, Internet Archive; in English in Playford, An Introduction to the Skill of Musick (1683)", "https://archive.org/details/lenvovemvsichedi00cacc"),
    "1-vowel": fact("concone-middle-voice", "Concone titled his 50 lessons \"pour le médium de la voix\": for the middle of the voice. The first Grove's Dictionary said his solfeggi and vocalizzi, this book among them, had made him \"a world-wide reputation for usefulness\".",
                    "Concone, 50 Leçons de chant, Op. 9 (Leipzig: Peters), title page, Internet Archive; Grove, A Dictionary of Music and Musicians, vol. 4 (1889), appendix, \"Concone\"", CONCONE_SCAN),
    "2-comma": fact("brahms-hidden-love-song", "Brahms hid an Austrian love song in the Wiegenlied's piano part, one he had heard Bertha Faber sing ten years before. Sending it for her baby in July 1868, he wrote that while she sang Hans to sleep, her husband murmured a love song.",
                    "Kalbeck, Johannes Brahms, vol. II part 1 (Berlin, 1908), pp. 326-327, quoting Brahms's letter, Internet Archive", "https://archive.org/details/bub_gb_qOwPAAAAYAAJ",
                    distinct=["bl-bertha-faber"]),
    "2-steady": fact("farinelli-trumpet-duel", "In 1771 Charles Burney told how the teenage Farinelli, singing in Rome, held a nightly contest with a famous trumpeter, each swelling out one note. When the trumpeter gave up, spent, Farinelli smiled and carried on in the same breath.",
                     "Burney, The Present State of Music in France and Italy (London, 1771; 2nd ed. 1773), Internet Archive", "https://archive.org/details/presentstatemus00burngoog"),
    "2-shape": fact("concone-commas-footnote", "On the first page of Concone's 50 lessons, the Peters edition prints a footnote in French: those who can't sing the whole phrase should breathe at the commas marked.",
                    "Concone, 50 Leçons de chant, Op. 9 (Leipzig: Peters, Edition Peters No. 980), p. 2, Internet Archive", CONCONE_SCAN),
    "3-thirds": fact("metastasio-street-verses", "Vaccai took his words from Metastasio, born Pietro Trapassi in Rome in 1698. As a boy he recited made-up verses to street crowds; the scholar Gravina adopted him and turned Trapassi into a Greek-style name, Metastasio.",
                     "Encyclopaedia Britannica, 11th ed. (1911), \"Metastasio\", Wikisource; Vaccai, Practical Method (1878), preface", "https://en.wikisource.org/wiki/1911_Encyclop%C3%A6dia_Britannica/Metastasio"),
    "3-lean": fact("vaccai-appoggiatura-value", "Vaccai called the appoggiatura \"the most pleasing ornament of song\". Its effect, he wrote, depends on giving it its true value: \"it may be increased but never diminished\".",
                   "Vaccai, Practical Method of Italian Singing (Boston: Russell, 1878), Lesson VIII, Internet Archive", VACCAI),
    "3-slide": fact("vaccai-portamento-not-dragging", "Vaccai warned that portamento \"by no means signifies that dragging of the voice\" heard so often. Most often, he wrote, it means touching the next note imperceptibly early, on the vowel before it.",
                    "Vaccai, Practical Method of Italian Singing (Boston: Russell, 1878), Lesson XIII, Internet Archive", VACCAI),
    "4-first": fact("caro-mio-ben-pacchierotti", "An early London print of Caro mio ben, from about 1785, calls it \"a celebrated song\", sung by the soprano Pacchierotti \"with universal applause\" at a concert for the Musical Fund. It names the composer only as \"Sigr. Giordani\".",
                    "Caro mio ben, A Celebrated Song (London: John Preston, about 1785), title page, IMSLP", "https://imslp.org/wiki/Caro_mio_ben_(Giordani,_Tommaso)", distinct=["cmb-which-giordani"]),
    "4-middle": fact("baker-thou-all-my-bliss", "The English words printed under Caro mio ben in 1894, \"Thou, all my bliss\", are by Theodore Baker, Schirmer's editor and translator, who in 1900 published his Biographical Dictionary of Musicians.",
                     "Parisotti, Anthology of Italian Song (New York: Schirmer, 1894), p. 131, Internet Archive; Baker, A Biographical Dictionary of Musicians (Schirmer, 1900)", "https://archive.org/details/anthologyofitali00pari"),
    "4-return": fact("malibran-vaccai-tomb-scene", "In Bologna in 1832, the great singer Maria Malibran, playing Romeo in Bellini's opera, swapped his tomb scene for Vaccai's. Librettos show nearly two thirds of productions from 1833 to 1857 used Vaccai's ending.",
                     "Poriss, \"Bellini alla Malibran\", Musicology Now, American Musicological Society (2013); Baker, Biographical Dictionary of Musicians (1900), \"Vaccai\"", "https://musicologynow.org/bellini-alla-malibran/"),
}


def lesson(lid, unit, title, steps, **extra):
    check(lid, unit, steps)
    if not extra.get("challenge"):
        assert lid in FACTS, f"cl-{lid}: every lesson page has a fact"
        extra = {"fact": FACTS[lid], **extra}
    return {"id": f"cl-{lid}", "title": EN(title), **extra, "steps": steps}


# ---- Unit 1: Joined ----

FIVE = [{"beat": i, "length": 1, "step": s, "lyric": "ah"} for i, s in enumerate([0, 2, 4, 5, 7])]
DOWN = [{"beat": i, "length": 1, "step": s, "lyric": "ah"} for i, s in enumerate([7, 5, 4, 2, 0])]
STARTS = M("0:2 0, 3:2 4, 6:2 2, 9:2 5, 12:3 0", 0)  # five starts on "ah", a rest before each


def caro_first():
    """Caro mio ben's first phrase, "Caro mio ben, credimi almen", from the template."""
    if not CARO:
        return [n for n in CARO_DRAFT if n["beat"] < 8]
    a = CARO.sections["A"]
    return CARO.notes(a[0][0], a[0][1])


UNIT1 = [
    lesson("1-joined", 1, "One joined line", [
        learn("Classical singing starts with one thing: notes joined, with no gap between them. Singers call it legato.", [
            ("No gap between the notes", "The sound keeps going as the note changes"),
            OWN, EASY,
        ]),
        choose("The same five notes, sung two ways. Listen to both, then choose.", 72, [
            ("Which one is joined?", [clip(FIVE), clip(gapped(FIVE))], 0, "The first kept the sound going from note to note. The second stopped between them."),
            ("Which one is joined?", [clip(gapped(DOWN)), clip(DOWN)], 1, "The second never stopped: one sound, five notes."),
            ("Which one is joined?", [clip(gapped(FIVE, 0.8)), clip(FIVE)], 1, "The first left small gaps; the second kept going through each change."),
        ]),
        find("Find the notes of a famous first phrase, on \"ah\". Each waits until you're on it.", on(caro_first()), CARO.tempo if CARO else 60),
        play("Now the whole phrase on \"ah\", joined: hear it, then sing it back.", on(caro_first()), CARO.tempo if CARO else 60, LANDS,
             score="landing", generous=True, keep=KEEP),
    ]),
    lesson("1-start", 1, "A clean start", [
        learn("A classical note starts on its pitch from the first sound: no slide up into it, no click.", [
            ("On the note at once", "Hear it inside first, then sing it"),
            ("An easy start", f"No click and no breathy h; {SAFE}"),
        ]),
        bullseye("Sing each note back on \"ah\", and watch where it lands.", 72, [0, 4, 2, 5, -1]),
        play("Five starts, a rest before each: every one on its note from the first sound.", on(STARTS), 66, LANDS, score="landing"),
    ]),
    lesson("1-vowel", 1, "One vowel, many notes", [
        learn("Keep one vowel through the moving notes: your mouth stays the same shape, and only the pitch changes.", [
            ("One shape for \"ah\"", "Never drifting to \"aw\" or \"uh\""),
            ("Joined in pairs", f"A breath at each rest; {SAFE}"),
        ]),
        find("Find the notes: a lesson Concone wrote for the middle of the voice. Each waits until you're on it.", on(CONCONE[:8]), CONCONE_TEMPO),
        play("The whole line on \"ah\", each pair of bars joined.", on(CONCONE), CONCONE_TEMPO, JOINED, score="legato"),
        selfcheck("Sing it once more, then hear yours beside the guide's.", CONCONE_TEMPO, on(CONCONE[:8]),
                  ["Did the \"ah\" keep its shape, never drifting to \"aw\" or \"uh\"?", "Did the sound keep going through each change?"]),
    ]),
    lesson("1-challenge", 1, "Your first Italian song", [
        learn("Vaccai wrote this for beginners nearly two hundred years ago. First its notes on \"ah\", then its Italian words.", [
            ("Vowels first", "Then the words, each vowel filling its notes"),
            ("Manca sollecita", f"A flame burns down faster than ever; {SAFE}"),
        ]),
        play("The first two lines on \"ah\", joined.", on(SCALE), SCALE_TEMPO, JOINED, score="legato"),
        play("Now with the words, the vowel lasting right up to each quick consonant.", SCALE, SCALE_TEMPO, LANDS, score="landing"),
    ], challenge=True),
]


# ---- Unit 2: One breath ----

STEADY = M("0:1 -3, 1:1 0, 2:6 2, 8:2 0", 0)  # a long note in the middle of the voice, inside a phrase
BRAHMS_VERSE = BRAHMS.sections["Verse 1"]
BRAHMS_HALF = BRAHMS.notes(BRAHMS_VERSE[0][0], BRAHMS_VERSE[3][1])  # "Lullaby and good night ... pillow thy head."
BRAHMS_HALF_CHORDS = BRAHMS.chords_at(BRAHMS_VERSE[0][0], BRAHMS_VERSE[3][1])


UNIT2 = [
    lesson("2-comma", 2, "Breathe at the comma", [
        learn("A phrase is one breath. Breathe where the words have a comma, low and easy, and the next phrase starts on time.", [
            ("One breath a phrase", "Breathe at the comma, not before"),
            ("Low and easy", f"A quiet breath, shoulders still; {SAFE}"),
        ]),
        play("Brahms's lullaby, its first four phrases: come in after each breath on time and on pitch.", BRAHMS_HALF, BRAHMS.tempo,
             "Scored on coming in after each breath, on time and on pitch.", score="entry", chords=BRAHMS_HALF_CHORDS),
        play("Again, each phrase joined from its first note to its last.", BRAHMS_HALF, BRAHMS.tempo, LINE, score="line", chords=BRAHMS_HALF_CHORDS),
    ]),
    lesson("2-steady", 2, "Steady in the middle", [
        learn("A long note in the middle of your voice, steady to its end. If a gentle wave comes into it by itself, let it; if not, that's fine.", [
            ("Steady to the end", "No sag at the end of the breath"),
            ("Easy, not breathy", f"The middle of your voice; {SAFE}"),
        ]),
        find("Find the notes. Each waits until you're on it.", on(STEADY), 60),
        play("The phrase on \"ah\": its long note steady to the end.", on(STEADY), 60, "Scored on the long note staying on its pitch to the end.", score="drift"),
    ]),
    lesson("2-shape", 2, "The end of a phrase", [
        learn("A phrase ends on purpose: its last note held to its end, steady, then stopped on time.", [
            ("Plan the ending", "Keep the breath for the last note"),
            ("Stop on time", f"Steady to the last moment; {SAFE}"),
        ]),
        play("Concone's last two bars on \"ah\": end the long note on time.", on(CONCONE_END), CONCONE_TEMPO,
             "Scored on the last note ending on time, steady to its end.", score="release"),
        selfcheck("Sing it once more, then hear yours beside the guide's.", CONCONE_TEMPO, on(CONCONE_END),
                  ["Did the line grow to its highest note, then ease away?", "Did the last note stay steady to its end?"]),
    ]),
    lesson("2-challenge", 2, "A phrase on one breath", [
        learn("Brahms's lullaby, written in 1868 for a friend's new baby: the first verse, each phrase on one breath.", [
            ("One breath a phrase", "Breathe at each comma"),
            ("Soft and joined", f"Sung to someone asleep; {SAFE}"),
        ]),
        play("The first verse, over the chords.", BRAHMS.notes(BRAHMS_VERSE[0][0], BRAHMS_VERSE[-1][1]), BRAHMS.tempo, LINE,
             score="line", chords=BRAHMS.chords_at(BRAHMS_VERSE[0][0], BRAHMS_VERSE[-1][1])),
    ], challenge=True),
]


# ---- Unit 3: Italian ----

THIRD_UP = [{"beat": 0, "length": 2, "step": 0, "lyric": "ah"}, {"beat": 2, "length": 2, "step": 4, "lyric": "ah"}]
THIRD_DOWN = [{"beat": 0, "length": 2, "step": 4, "lyric": "ah"}, {"beat": 2, "length": 2, "step": 0, "lyric": "ah"}]
FOURTH = [{"beat": 0, "length": 2, "step": 0, "lyric": "ah"}, {"beat": 2, "length": 2, "step": 5, "lyric": "ah"}]
SLIDE = M("0:2 0, 2:2 5, 4:1 4, 5:1 2, 6:2 0", 0)
SLIDE2 = M("0:2 2, 2:2 5, 4:2 0, 6:2 4, 8:1 2, 9:3 0", 0)


def style(notes, at, how):
    return [dict(n, style=how) if i == at else n for i, n in enumerate(notes)]


UNIT3 = [
    lesson("3-thirds", 3, "Skips that stay joined", [
        learn("Vaccai's next tune skips over a note at a time. Each skip lands cleanly, and the sound keeps going.", [
            ("Skip, don't slide", "Land each note from the first sound"),
            ("Vowels first", f"Then the words; {SAFE}"),
        ]),
        choose("Listen to both, then choose.", 72, [
            ("Which one slid into the note?", [clip(style(THIRD_UP, 1, "scoop")), clip(THIRD_UP)], 0, "The first slid up into its second note. The second landed right on it."),
            ("Which one slid into the note?", [clip(THIRD_DOWN), clip(style(THIRD_DOWN, 1, "scoop"))], 1, "The second dipped and slid into its last note. The first landed it."),
        ]),
        play("Semplicetta tortorella's first phrase on its own vowels, joined.", vowels_of(THIRDS_FIRST), THIRDS_TEMPO, JOINED, score="legato"),
        play("Now with the words.", THIRDS_FIRST, THIRDS_TEMPO, LANDS, score="landing"),
    ]),
    lesson("3-lean", 3, "The leaning note", [
        learn("A leaning note sits on the beat, a step above where the music is going, then steps down to it. Classical singers call it an appoggiatura.", [
            ("On the beat", "The leaning note first, then the step down"),
            ("Lean, then ease", f"A little more on the first note; {SAFE}"),
        ]),
        find("Find the notes. Each waits until you're on it.", LEAN[:6], LEAN_TEMPO),
        play("Vaccai's line, both leaning notes on the beat.", LEAN, LEAN_TEMPO, BEAT, rhythm=True),
    ]),
    lesson("3-slide", 3, "A slide on purpose", [
        learn("Classical singing has one slide, and only where the music asks: from one note to the next, on the first note's vowel.", [
            ("Late in the first note", "The slide starts near its end"),
            ("Arrive on the beat", f"The new note lands on time; {SAFE}"),
        ]),
        choose("Listen to both, then choose.", 66, [
            ("Which one slid on purpose?", [clip(style(FOURTH, 0, "slide")), clip(style(FOURTH, 1, "scoop"))], 0,
             "The first slid at the end of its first note and arrived on the beat. The second came in late and scooped up."),
            ("Which one slid on purpose?", [clip(style(FOURTH, 1, "scoop")), clip(style(FOURTH, 0, "slide"))], 1,
             "The second slid out of its first note, on the vowel. The first started its second note low and slid up into it."),
        ]),
        play("One slide on purpose, up a fourth, and clean steps down.", style(on(SLIDE), 0, "slide"), 66,
             "Scored on the slide asked for, clean starts everywhere else, and pitch.", score="styled"),
        play("Two slides, each where it's asked for.", style(style(on(SLIDE2), 0, "slide"), 2, "slide"), 66,
             "Scored on the slides asked for, clean starts everywhere else, and pitch.", score="styled"),
    ]),
    lesson("3-challenge", 3, "Semplicetta tortorella", [
        learn("All of Vaccai's tune of skips, with its words: a simple little dove flies into the hunter's arms.", [
            ("Skips that land", "Each one clean, the sound joined"),
            ("Italian vowels", f"Each vowel filling its notes; {SAFE}"),
        ]),
        play("The whole song, with its words.", THIRDS, THIRDS_TEMPO, LANDS, score="landing"),
    ], challenge=True),
]


# ---- Unit 4: A song for voice and piano ----

def caro(part):
    """A section of Caro mio ben, with its chords."""
    if not CARO:
        return [], []
    phrases = CARO.sections[part]
    frm, to = phrases[0][0], phrases[-1][1]
    return CARO.notes(frm, to), CARO.chords_at(frm, to)


def caro_whole():
    if not CARO:
        return [], []
    bounds = sorted(CARO.bounds)
    return CARO.notes(bounds[0], bounds[-1]), CARO.chords_at(bounds[0], bounds[-1])


UNIT4 = []  # built once the caro-mio-ben template is in (WRITE)
if CARO:
    A, A_CHORDS = caro("A")
    A_TWO = CARO.notes(CARO.sections["A"][0][0], CARO.sections["A"][1][1])  # "Caro mio ben ... languisce il cor"
    B, B_CHORDS = caro("B")
    A2, A2_CHORDS = caro("A2")
    WHOLE, WHOLE_CHORDS = caro_whole()
    UNIT4 = [
        lesson("4-first", 4, "Caro mio ben, the opening", [
            learn("Caro mio ben: \"my dear beloved\". A song for voice and piano from about 1785, the first one most classical singers learn.", [
                ("Vowels first", "Then the words, over the piano's chords"),
                OWN,
            ]),
            play("The first two phrases on their own vowels, joined.", vowels_of(A_TWO), CARO.tempo, JOINED, score="legato"),
            play("Now with the words, over the chords.", A, CARO.tempo, LINE, score="line", chords=A_CHORDS),
        ]),
        lesson("4-middle", 4, "The middle", [
            learn("The middle of the song pleads: your faithful one sighs, so end your cruelty.", [
                ("Higher and fuller", "The highest note short, reached easily"),
                ("Joined", f"Breathe at each comma; {SAFE}"),
            ]),
            play("The middle, over the chords.", B, CARO.tempo, LINE, score="line", chords=B_CHORDS),
        ]),
        lesson("4-return", 4, "The return and the ending", [
            learn("The opening comes back, and this time the song ends: the last notes held steady, on one breath.", [
                ("The opening again", "With its slide, where the music asks"),
                ("A steady ending", f"Keep the breath for the last note; {SAFE}"),
            ]),
            play("The return, over the chords.", A2, CARO.tempo, LINE, score="line", chords=A2_CHORDS),
        ]),
        lesson("4-challenge", 4, "Caro mio ben", [
            learn("My dear beloved, believe me at least: without you, my heart languishes. First your phrase from lesson 1, then the whole song.", [
                ("Then and now", "Your first phrase on \"ah\", beside today's"),
                ("Kept as a song", f"Play it back any time; {SAFE}"),
            ]),
            play("The first phrase, with its words.", caro_first(), CARO.tempo, LINE, score="line",
                 chords=CARO.chords_at(CARO.sections["A"][0][0], CARO.sections["A"][0][1]), thenAndNow=KEEP),
            play("The whole song, over the chords.", WHOLE, CARO.tempo, LINE, score="line", chords=WHOLE_CHORDS),
        ], challenge=True,
           keepSong={"title": EN("Caro mio ben"), "takes": [{"step": 2, "name": EN("Voice")}], "from": 2, "partners": [], "chords": EN("Piano")}),
    ]

course = {
    "id": "classical-singing", "version": 1, "reviewed": False, "title": EN("Classical singing basics"),
    "units": [
        {"id": "cl-joined", "title": EN("Joined"), "colour": COLOUR, "lessons": UNIT1},
        {"id": "cl-one-breath", "title": EN("One breath"), "colour": COLOUR, "lessons": UNIT2},
        {"id": "cl-italian", "title": EN("Italian"), "colour": COLOUR, "lessons": UNIT3},
        {"id": "cl-a-song", "title": EN("A song for voice and piano"), "colour": COLOUR, "lessons": UNIT4},
    ],
}

for u in course["units"]:
    for l in u["lessons"]:
        for i, s in enumerate(l["steps"]):
            ex = s.get("exercise") or {}
            if s["kind"] == "play":
                notes = ex["notes"]
                lo, hi = (min(n["step"] for n in notes), max(n["step"] for n in notes)) if notes else (0, 0)
                print(f"{l['id']}[{i}] {ex.get('score', 'default')}: {len(notes)} notes, {lo} to {hi}, {joins(notes)} joins,"
                      f" {timed_moments(notes, ex['tempo'])} timed moments{', rhythm' if ex.get('rhythm') else ''}")
if WRITE:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(course, open(OUT, "w"))
