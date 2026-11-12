"""Blues singing (docs/courses/blues-singing.md in the app's repo): writes course/plus/blues-singing/course.json.
Built from the courses lead's outline, as revised by a blues voice-teacher and historian review, a game-design
review and a rights search: three lines, humming first, the blue note in the tune, the band's turn, laying back,
and a verse of your own, on the Thomas family's own printed blues.

Its songs, by the shared rights line (printed before 1931; every writer, lyricist and arranger died before 1956;
printings only), each read from its scan bar by bar and checked by the arranger:
- Shorty George Blues (words George W. Thomas and Hociel Thomas, music George W. Thomas; Chicago: Geo. W. Thomas
  Music Co., 1924): the library's shorty-george-blues template (the arranger's, in G, five cleared verses).
- The Fives (words George W. Thomas, music Hersal Thomas and George W. Thomas; Chicago: Geo. W. Thomas and Co.,
  1922): the verse's first strain, bars 1 to 12, in C.
- Muscle Shoals Blues (words and music George W. Thomas; Chicago: Geo. W. Thomas and Co., 1921; Mississippi
  State University's scan): bars 7 to 13 and 19 to 25, in C, each line landing on the printed low C (the print
  stacks both octaves; the arranger's reading).

A line is `beat:length midi [syllable], ...` as printed (quarter-note beats, re-timed to start at 0), turned into
steps from the singer's comfortable note by a reference pitch per song, so each sits in the course's span.
The checks fail the build on:
- a sung note outside -5 to +9;
- `rhythm` in unit 1 or 2, or on a challenge's last scored step, or with fewer than four timed moments;
- `entry` as a lesson's last scored step, or with fewer than three entries;
- a `styled` step as the last scored step of the lesson that first uses it;
- a partner line a speaker would drop (each band's turn sits clear of your notes, so no lesson needs headphones);
- the house words (the reviews' never-use list), and no letter names.

    python3 -I tools/bl_course.py && python3 -I tools/coursefmt.py course/plus/blues-singing/course.json
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/blues-singing/course.json"
WRITE = True

BANNED = re.compile(r"\bstars?\b|—|\bgrowl|\bgrit|\brasp|\bgravel|\bbelt\b|\bpush|\bpower|\blouder\b|\bdirty\b|\braw\b|\bprimitive"
                    r"|\bsavage|\bjungle|\bexotic|soulful voice|\bauthentic\b|real blues voice|devil's music|\bshout|plantation"
                    r"|slave song|\bcoon|\bmammy|\bdark(e)?y|\bpickaninny|\bminstrel|\bblackface|\bAAB\b|eight-bar|\bthird\b|flat seven"
                    r"|\bminor\b|\bmajor\b|\bscoop|\bstyled\b", re.I)
LETTERS = re.compile(r"\b[B-G]\b|\b[A-G][#♯♭]")

COLOUR = 1
KEYS = {"C": 0, "C#": 1, "Db": 1, "D": 2, "Eb": 3, "E": 4, "F": 5, "F#": 6, "Gb": 6, "G": 7, "Ab": 8, "A": 9, "Bb": 10, "B": 11}
EPS = 1e-9
LOW, HIGH = -5, 9
QUALITY = {"": "maj", "7": "dom7", "m": "min", "m7": "min7"}

SAFE = "stop if anything tightens or hurts"
TELL = ("Tell it, in your own clear voice", f"At a speaking volume; {SAFE}")
PITCH = "Scored on your notes on pitch."
TUNE = "Scored on the tune. The words are yours; the app hears the notes."
BEAT = "Scored on your notes on pitch and on the beat."
CHOSE = "Scored on the rounds you got right first time."
KEEP = "blues.first-line"


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


def C(text, ref):
    """Chords `beat name, ...` (C, C7, F, G7...) as roots from the comfortable note."""
    out = []
    for token in text.split(","):
        beat, name = token.split()
        root = name[:2] if len(name) > 1 and name[1] in "#b" else name[0]
        out.append({"beat": num(float(beat)), "root": (KEYS[root] - ref) % 12, "quality": QUALITY[name[len(root):]]})
    return out


def on(notes, lyric):
    """The line on one sound: each sung syllable takes it, a held melisma note keeps none."""
    return [dict(n, lyric=lyric) if "lyric" in n or i == 0 else n for i, n in enumerate(notes)]


def wordless(notes):
    """The tune with no words: yours go on it."""
    return [{k: v for k, v in n.items() if k != "lyric"} for n in notes]


def shift(notes, by):
    return [dict(n, beat=num(n["beat"] + by)) for n in notes]


def end_of(notes):
    return max(n["beat"] + n["length"] for n in notes)


class Song:
    """A library template's tune (its top part) and chords, in steps from the comfortable note (midi - ref)."""

    def __init__(self, name, ref):
        data = json.loads((REPO / "templates" / "library" / f"{name}.json").read_text())
        self.name, self.tempo = name, data["tempo"]
        self.tune = [(n["beat"], n["length"], n["pitch"] - ref, n.get("lyric")) for n in data["parts"][0]["guide"]["notes"]]
        self.chords = [(c["beat"], (c["root"] - ref) % 12, c["quality"]) for c in data["chords"]]
        self.sections = {s.get("name"): s["phrases"] for s in data["sections"]}
        self.bounds = {b for s in data["sections"] for p in s["phrases"] for b in p}

    def notes(self, frm, to):
        return [{"beat": num(b - frm), "length": num(length), "step": p, **({"lyric": w} if w and w != "~" else {})}
                for b, length, p, w in self.tune if frm - EPS <= b < to - EPS]

    def chords_at(self, frm, to):
        sounding = [c for c in self.chords if c[0] <= frm + EPS][-1]
        inside = [c for c in self.chords if frm + EPS < c[0] < to - EPS]
        return [{"beat": num(b - frm), "root": r, "quality": q} for b, r, q in [(frm,) + sounding[1:]] + inside]

    def phrase(self, verse, i, j=None):
        """Verse `verse`'s phrases i to j (inclusive), from its first beat."""
        p = self.sections[f"Verse {verse}"]
        frm, to = p[i][0], p[j if j is not None else i][1]
        return self.notes(frm, to), self.chords_at(frm, to)


# ---- The songs ----

# Shorty George Blues, the arranger's template in G (the print's F, a tone up): D4 to D5, G at the comfortable
# note, so the line lives from -5 to +7 and mostly between 0 and +4, the middle of the voice.
SHORTY = Song("shorty-george-blues", 67)
SG_TEMPO = 80  # the print: "Don't play this piece fast"; the template's 88, a little slower to learn

# The Fives, the verse's first strain (bars 1 to 12, C, "slow"): "Old Five ready to take me away, / Old Five ready
# to take me away, / I'm leaving town but not leaving to stay." C4 at -5, so the held line ends sit at +7.
FIVES = M("0:1 72 Old, 1:1 70 Five, 2:1 67 read-, 3:1 60 y, 4:1 72 to, 5:1 70 take, 6:1 67 me, 7:1 64 a-, 8:6 72 way, "
          "16:1 72 Old, 17:1 69 Five, 18:1 65 read-, 19:1 69 y, 20:1 72 to, 21:1 70 take, 22:1 67 me, 23:1 64 a-, 24:6 72 way, "
          "31:1 67 I'm, 32:1 67 leav-, 33:1 65 ing, 34:1 62 town, 35:1 67 but, 36:1 67 not, 37:1 65 leav-, 38:1 62 ing, "
          "39:1 67 to, 40:6 72 stay", 65)
FIVES_CHORDS = C("0 C7, 16 F, 20 C7, 24 C, 32 G7, 40 C, 44 G7", 65)
# The second strain (bars 13 to 24): "My trunk packed now, I'm sure on my way" twice, then "These few words to you
# I'm going to say". Its first line end is a 4-beat note (bar 15), as printed.
FIVES2 = M("0:1 72 My, 1:1 70 trunk, 2:1 67 packed, 3:1 60 now, 4:1 72 I'm, 5:1 70 sure, 6:1 67 on, 7:1 64 my, 8:4 72 way, "
           "16:1 72 My, 17:1 69 trunk, 18:1 65 packed, 19:1 69 now, 20:1 72 I'm, 21:1 70 sure, 22:1 67 on, 23:1 64 my, 24:6 72 way, "
           "32:1 67 These, 33:1 65 few, 34:1 62 words, 35:1 67 to, 36:1 67 you, 37:1 65 I'm, 38:1 62 going, 39:1 67 to, 40:6 72 say", 65)
FIVES_FULL = FIVES + shift(FIVES2, 48)
FIVES_FULL_CHORDS = FIVES_CHORDS + [dict(c, beat=num(c["beat"] + 48)) for c in FIVES_CHORDS]
FIVES_TEMPO = 76
# The band's turn: the line's own falling shape, answered in the rest after each held line end, clear of your
# notes (ending 0.5 s before your next one), so a speaker keeps it sounding.
TURN = [{"beat": 14.33, "length": 0.33, "step": 7, "lyric": "doo"}, {"beat": 14.67, "length": 0.33, "step": 5, "lyric": "doo"},
        {"beat": 15, "length": 0.33, "step": 2, "lyric": "doo"}]
FIVES_TURNS = {"notes": TURN + shift(TURN, 32)}  # after the first line and after the strain's last
FIVES_FULL_TURNS = {"notes": TURN + shift(TURN, 32) + shift(TURN, 46) + shift(TURN, 64)}  # and in the second strain's rests

# Muscle Shoals Blues, bars 7 to 13 and 19 to 25 (C, "slow"): a rhyming pair and a line home, not three lines.
# Each line lands on the printed low C. C4 at -5: the line runs from -5 to +9 (a passing eighth).
SHOALS_A = M("0:0.5 72 Hur-, 0.5:0.5 72 ry, 1:1 70 up, 2:0.5 67 ma-, 2.5:1.5 60 ma, 4:0.5 72 pack, 4.5:1.5 70 your, 6:2 67 grip, "
             "8:0.5 72 let's, 8.5:0.5 74 go, 9:0.5 72 back, 9.5:1 70 to, 10.5:0.5 67 old, 11:0.5 64 Mus-, 11.5:0.5 62 cle, "
             "12:0.5 64 Shoals, 12.5:0.5 67 for, 13:0.5 64 a, 13.5:1.5 62 trip, 16:0.5 65 Come, 16.5:1.5 65 on, 18:0.5 63 ma-, "
             "18.5:1.5 60 ma, 20:0.5 65 pack, 20.5:1.5 65 your, 22:1 67 grip, 23:1 64 let's, 24:4 60 go", 65)
SHOALS_B = M("0:0.5 71 I, 0.5:0.5 72 woke, 1:0.5 72 up, 1.5:1 70 this, 2.5:0.5 67 morn-, 3:1.5 60 ing, 4.5:0.5 72 feel-, "
             "5:1.5 70 ing, 6.5:2 67 glad, 8.5:0.5 72 think-, 9:0.5 74 ing, 9.5:0.5 72 a-, 10:1 70 bout, 11:0.5 67 the, "
             "11.5:0.5 64 good, 12:0.5 62 old, 12.5:0.5 64 times, 13:0.5 67 we, 13.5:0.5 64 once, 14:1.5 62 had, "
             "16.5:0.5 65 Hur-, 17:1.5 65 ry, 18.5:0.5 63 ma-, 19:1.5 60 ma, 20.5:0.5 65 we, 21:1.5 65 must, 22.5:1 67 leave, "
             "23.5:1 64 this, 24.5:4 60 town", 65)
SHOALS_CHORDS = C("0 C, 2 C7, 16 F, 18 F7, 20 F7, 22 C, 23 G7, 24 C", 65)
SHOALS_TEMPO = 72
# Both passages, a bar's breath between: the second starts on its pickup, so the chords follow it.
SHOALS_BOTH = SHOALS_A + shift(SHOALS_B, 31.5)
SHOALS_BOTH_CHORDS = SHOALS_CHORDS + [dict(c, beat=num(c["beat"] + 32)) for c in SHOALS_CHORDS]

# The course's own lines: a bluer ending, on the low seven below home.
BLUE_END = M("0:1 7, 1:1 5, 2:1 3, 3:1 0, 4:4 -2", 0)
HOME_END = M("0:1 7, 1:1 5, 2:1 3, 3:1 2, 4:4 0", 0)


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
    return {"kind": "try", "text": EN(text), "exercise": {"tempo": tempo, "notes": notes}}


def play(text, notes, tempo, measures, *, chords=None, partners=None, **extra):
    """Hear it, then sing it back (`turn`); with chords or partners, sing it over them (`turn: false`)."""
    ex = {"tempo": tempo, "notes": notes, "turn": not (chords or partners)}
    if chords:
        ex["chords"] = chords
    if partners:
        ex["with"] = partners if isinstance(partners, list) else [partners]
    ex.update(extra)
    return {"kind": "play", "text": EN(text), "exercise": ex, "measures": EN(measures)}


def choose(text, tempo, rounds):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": [
        {"prompt": EN(p), "clips": clips, "answer": a, "why": EN(w)} for p, clips, a, w in rounds]},
        "measures": EN(CHOSE)}


def selfcheck(text, tempo, notes, questions):
    return {"kind": "selfcheck", "text": EN(text),
            "exercise": {"tempo": tempo, "model": {"notes": notes}, "along": True, "questions": [EN(q) for q in questions]}}


def clip(notes):
    return {"notes": notes}


def style(notes, at, how):
    return [dict(n, style=how) if i == at else n for i, n in enumerate(notes)]


# ---- The checks ----

def timed_moments(notes, tempo):
    bs = 60 / tempo
    ordered = sorted(notes, key=lambda n: n["beat"])
    k = 0
    for i, n in enumerate(ordered):
        if i == 0 or (n["beat"] - (ordered[i - 1]["beat"] + ordered[i - 1]["length"])) * bs >= 0.1 or n["step"] != ordered[i - 1]["step"]:
            k += 1
    return k


def judged_entries(notes):
    ordered = sorted(notes, key=lambda n: n["beat"])
    return [b["beat"] for a, b in zip(ordered, ordered[1:]) if b["beat"] - (a["beat"] + a["length"]) >= 0.25 - EPS]


CALL_CLEAR_BEFORE, CALL_CLEAR_AFTER = 0.4, 0.15  # the app's speakerPartnerNotes


def speaker_drops(ex):
    if not ex.get("with"):
        return 0
    bs, target = 60 / ex["tempo"], ex["notes"]
    lost = 0
    for line in ex["with"]:
        runs = []
        for n in sorted(line["notes"], key=lambda n: n["beat"]):
            if runs and abs(end_of(runs[-1]) - n["beat"]) < 0.02:
                runs[-1].append(n)
            else:
                runs.append([n])
        for run in runs:
            a, z = run[0]["beat"] * bs, end_of(run) * bs
            if not all(z <= t["beat"] * bs - CALL_CLEAR_BEFORE or a >= (t["beat"] + t["length"]) * bs + CALL_CLEAR_AFTER for t in target):
                lost += len(run)
    return lost


def scored(step):
    return step["kind"] in ("play", "choose", "bullseye") and not step.get("exercise", {}).get("unscored")


STYLED_SEEN = set()


def check(lid, unit, steps, challenge):
    last = max(i for i, s in enumerate(steps) if scored(s))
    for i, step in enumerate(steps):
        where = f"bl-{lid} step {i + 1}"
        ex = step.get("exercise", {})
        if step["kind"] in ("play", "try"):
            for n in ex["notes"]:
                assert n["beat"] >= 0 and n["length"] > 0, f"{where}: a note before beat 0, or with no length"
                assert LOW <= n["step"] <= HIGH, f"{where}: step {n['step']} at beat {n['beat']} is outside {LOW} to {HIGH}"
        if step["kind"] != "play":
            continue
        assert speaker_drops(ex) == 0, f"{where}: a speaker would drop the band's turn"
        if "rhythm" in ex:
            assert "score" not in ex, f"{where}: rhythm only on a default-scored step"
            assert timed_moments(ex["notes"], ex["tempo"]) >= 4, f"{where}: a rhythm step needs four timed moments"
            assert unit > 2, f"{where}: units 1 and 2 aren't timed"
            assert not (challenge and i == last), f"{where}: a challenge's last step isn't timed (blues sits behind the beat)"
        if ex.get("score") == "entry":
            assert len(judged_entries(ex["notes"])) >= 3, f"{where}: an entry step needs three entries"
            assert i != last, f"{where}: entry has no one-star floor, so it's never the lesson's last scored step"
        if ex.get("score") == "styled":
            first = "styled" not in STYLED_SEEN
            assert not (first and i == last), f"{where}: a fall is shown before it's a lesson's last scored step"
    if any(s.get("exercise", {}).get("score") == "styled" for s in steps):
        STYLED_SEEN.add("styled")


# ---- The facts ----
# Each lesson page's "Did you know?" (2026-11-08): read in its source, then read again by a second, independent
# check, which corrected seven (mostly wording that stretched a quote); every person named has died. Where the
# old folklore articles use dated language, none of it is quoted. The four challenges carry none.

def FACT_EN(text):
    """A fact's words: the never-use list, but people's initials (W. C. Handy) aren't note names."""
    assert not BANNED.search(text), text
    return {"en": text}


def fact(fid, text, source, url, **extra):
    return {"id": fid, "text": FACT_EN(text), "source": FACT_EN(source), "url": url, **extra}


JAF11 = "https://archive.org/details/sim_journal-of-american-folklore_october-december-1911_24_94"
JAF03 = "https://archive.org/details/sim_journal-of-american-folklore_july-september-1903_16_62"
HANDY = "https://archive.org/details/fatherofbluesaut00wcha_0"
FACTS = {
    "1-say": fact("odum-joe-turner-three-times", "In 1911 the sociologist Howard Odum printed songs he had heard in Mississippi and Georgia. Of one, about Joe Turner, he wrote: \"Each line is sung three times to make a stanza.\"",
                  "Odum, Journal of American Folk-Lore 24 (1911), p. 351, Internet Archive", JAF11),
    "1-hum": fact("dark-was-the-night-hummed", "Blind Willie Johnson's 1927 recording of Dark Was the Night, Cold Was the Ground has no words, only hums and moans over his slide guitar. In 1977 NASA put it on the Voyager Golden Record.",
                  "Library of Congress, National Recording Registry essay; NASA, Golden Record contents", "https://www.loc.gov/static/programs/national-recording-preservation-board/documents/DarkWasTheNight.pdf"),
    "1-answer": fact("handy-third-line-why", "W. C. Handy found the folk habit of singing one line three times too monotonous. So in St. Louis Blues he made a statement, repeated it, then used the last line to say why.",
                     "Handy, Father of the Blues (New York: Macmillan, 1941), pp. 142-143, Internet Archive", HANDY),
    "2-blue": fact("peabody-sharp-on-purpose", "In 1903 an archaeologist who had dug a mound in Coahoma County, Mississippi, wrote that his crew often sang a refrain's final home note a little sharp: \"So frequent was this that it seemed intentional or unavoidable, not merely a mistake in pitch.\"",
                   "Peabody, Journal of American Folk-Lore 16 (1903), p. 151, Internet Archive", JAF03),
    "2-ending": fact("waller-muscle-shoals-1922", "In October 1922, in New York, Fats Waller recorded Muscle Shoals Blues, by George W. Thomas, as a piano solo for OKeh.",
                     "Discography of American Historical Recordings, OKeh matrix S-70948, UC Santa Barbara", "https://adp.library.ucsb.edu/index.php/matrix/detail/2000203086/S-70948-Muscle_Shoals_blues",
                     distinct=["shch-carnegie-1922", "sgb-hociel", "sgb-own-press"]),
    "2-two": fact("muscle-shoals-ford-boom", "Muscle Shoals Blues, printed in 1921, begs \"go with me to Muscle Shoals\". That year Henry Ford offered to lease the unfinished dam and plants there, setting off a short-lived land boom.",
                  "Encyclopedia of Alabama, \"Muscle Shoals\"; The Henry Ford museum; Mississippi State University Libraries", "https://encyclopediaofalabama.org/?p=16787"),
    "3-room": fact("handy-gaps-became-breaks", "In the folk blues, W. C. Handy wrote, the singer filled occasional gaps with words like \"Oh, baby\". In St. Louis Blues he filled those gaps in the piano and orchestra parts instead. Such a fill is called a break.",
                   "Handy, Father of the Blues (New York: Macmillan, 1941), pp. 120-121, Internet Archive", HANDY),
    "3-fall": fact("tutwiler-knife-guitar", "Waiting for a late train at Tutwiler, Mississippi, W. C. Handy woke to a guitarist pressing a knife on his strings as he played. Handy called the effect unforgettable.",
                   "Handy, Father of the Blues (New York: Macmillan, 1941), p. 74, Internet Archive", HANDY),
    "3-lay": fact("fives-train-rhythm", "The Fives, by George W. Thomas and his brother Hersal, was inspired by railroad travel. Its 1922 sheet music sings of a fast westbound train, Number 5.",
                  "Handbook of Texas Online, \"Thomas, George Washington, Jr.\"", "https://www.tshaonline.org/handbook/entries/thomas-george-washington-jr-clay-custer",
                  distinct=["sgb-hociel", "sgb-own-press"]),
    "4-first": fact("woke-up-this-mornin-1911", "Waking up this morning was sung about long before blues records. A camp workers' song Howard Odum printed in 1911 sings three times of waking up this morning and not being able to keep from crying, then answers it.",
                    "Odum, Journal of American Folk-Lore 24 (1911), p. 381, Internet Archive", JAF11),
    "4-answer": fact("hersal-died-a-teenager", "Hersal Thomas, who wrote The Fives with his much older brother George, was a piano prodigy whose playing of it inspired Chicago pianists such as Albert Ammons and Meade Lux Lewis. He died suddenly in Detroit in 1926, still in his teens.",
                     "Handbook of Texas Online, \"Thomas, Hersal\"; Discography of American Historical Recordings", "https://www.tshaonline.org/handbook/entries/thomas-hersal"),
    "4-verse": fact("mighty-long-half-day", "In Coahoma County, Mississippi, in 1901 and 1902, an archaeologist heard his crew make up lines on the spot about whatever was going on. One Saturday half-holiday, a sing-song came out of the trench: Mighty long half day, Captain.",
                    "Peabody, Journal of American Folk-Lore 16 (1903), pp. 149-150, Internet Archive", JAF03),
}


def lesson(lid, unit, title, steps, **extra):
    check(lid, unit, steps, extra.get("challenge", False))
    if not extra.get("challenge"):
        assert lid in FACTS, f"bl-{lid}: every lesson page has a fact"
        extra = {"fact": FACTS[lid], **extra}
    return {"id": f"bl-{lid}", "title": EN(title), **extra, "steps": steps}


# ---- Unit 1: Three lines ----

V1_A, V1_A_CHORDS = SHORTY.phrase(1, 0)       # "I wrote a letter and I mailed it right in the air"
V1_A2, V1_A2_CHORDS = SHORTY.phrase(1, 1)     # "Oh I wrote a letter and mailed it in the air"
V1_B, V1_B_CHORDS = SHORTY.phrase(1, 2)       # "You can tell by that I've got a man in the world somewhere"
V1, V1_CHORDS = SHORTY.phrase(1, 0, 2)
SAME = M("0:1 4, 1:1 3, 2:2 0, 4:1 4, 5:1 3, 6:2 0", 0)
DIFF = M("0:1 4, 1:1 3, 2:2 0, 4:1 7, 5:1 5, 6:2 2", 0)
HOME = M("0:1 4, 1:1 3, 2:1 2, 3:3 0", 0)
AWAY = M("0:1 4, 1:1 3, 2:1 5, 3:3 7", 0)

UNIT1 = [
    lesson("1-say", 1, "Say it, say it again", [
        learn("A blues says a line, says it again, then answers it. It's African American music, from the Deep South, sung for years before anyone printed it.", [
            ("Three lines", "Say it, say it again, then answer it"),
            TELL,
        ]),
        find("The first line of a blues printed in Chicago in 1924. Find its notes: each waits until you're on it.", V1_A, SG_TEMPO),
        choose("Listen to both, then choose.", SG_TEMPO, [
            ("Which one says it again?", [clip(on(SAME, "oh")), clip(on(DIFF, "oh"))], 0, "The first sang the same tune twice. The second changed it."),
            ("Which one says it again?", [clip(on(DIFF, "oh")), clip(on(SAME, "oh"))], 1, "The second said it again, note for note."),
        ]),
        play("Now hear the line, then sing it back.", V1_A, SG_TEMPO, PITCH, generous=True, keep=KEEP),
    ]),
    lesson("1-hum", 1, "Hum it first", [
        learn("Blues singers often hum a line before they sing it. Hum it, then open to \"oh\", then sing the words.", [
            ("Mm, then oh, then words", "The tune first, then what it says"),
            ("Easy and low", f"Hum lightly, lips together; {SAFE}"),
        ]),
        play("The line again, said a second time: hum it on \"mm\".", on(V1_A2, "mm"), SG_TEMPO, PITCH),
        play("Now open to \"oh\".", on(V1_A2, "oh"), SG_TEMPO, PITCH),
        play("Now the words.", V1_A2, SG_TEMPO, PITCH),
    ]),
    lesson("1-answer", 1, "The answer line", [
        learn("The last line answers the first two: it rhymes with them and comes home to the note the song started from.", [
            ("It rhymes", "Air, then somewhere"),
            ("It comes home", f"The last note settles; {SAFE}"),
        ]),
        choose("Listen to both, then choose.", SG_TEMPO, [
            ("Which one comes home?", [clip(on(HOME, "oh")), clip(on(AWAY, "oh"))], 0, "The first settled on its last note. The second stopped up in the air."),
            ("Which one comes home?", [clip(on(AWAY, "oh")), clip(on(HOME, "oh"))], 1, "The second came home; the first was left hanging."),
        ]),
        find("Find the answer line's notes. Each waits until you're on it.", V1_B, SG_TEMPO),
        play("Hear the answer line, then sing it back.", V1_B, SG_TEMPO, PITCH),
    ]),
    lesson("1-challenge", 1, "One whole verse", [
        learn("All three lines of the first verse, over the piano's chords: say it, say it again, answer it.", [
            ("Three lines", "A breath after each"),
            TELL,
        ]),
        play("The whole verse, over the chords.", V1, SG_TEMPO, PITCH, chords=V1_CHORDS),
    ], challenge=True),
]


# ---- Unit 2: The blue note ----

V2_AB, V2_AB_CHORDS = SHORTY.phrase(2, 0, 1)  # "So many days I stole away and I cried", twice
V2_C, V2_C_CHORDS = SHORTY.phrase(2, 2)       # "Didn't have no blues, I just was not really satisfied"
V2, V2_CHORDS = SHORTY.phrase(2, 0, 2)

UNIT2 = [
    lesson("2-blue", 2, "The blue note in the tune", [
        learn("This tune leans on a blue note, sung between two piano keys, just under the bright one, then on it. Scat singing has more of it; here it's in the tune as printed.", [
            ("Lean, then land", "The lower note first, then the bright one"),
            ("Sung as written", f"No sliding needed; {SAFE}"),
        ]),
        find("Find the notes: each waits until you're on it.", V2_AB[:8], SG_TEMPO),
        play("So many days: the line, said twice, its blue notes as written.", V2_AB, SG_TEMPO, PITCH, chords=V2_AB_CHORDS),
    ]),
    lesson("2-ending", 2, "A bluer ending", [
        learn("A blues line can end below home, on a lower note that leaves it open. It sounds odd at first; listen first.", [
            ("Below home", "A whole step under it"),
            ("Let it sit", f"Easy, not pressed down; {SAFE}"),
        ]),
        choose("Listen to both, then choose.", 72, [
            ("Which ending sounds bluer?", [clip(on(HOME_END, "oh")), clip(on(BLUE_END, "oh"))], 1, "The second ended below home, open and blue. The first settled home."),
            ("Which ending sounds bluer?", [clip(on(BLUE_END, "oh")), clip(on(HOME_END, "oh"))], 0, "The first stopped below home; the second came all the way."),
        ]),
        find("Find the bluer ending: each note waits until you're on it.", on(BLUE_END, "oh"), 72),
        play("Sing the bluer ending on \"oh\".", on(BLUE_END, "oh"), 72, PITCH),
        play("Now the verse's answer line: Didn't have no blues.", V2_C, SG_TEMPO, PITCH, chords=V2_C_CHORDS),
    ]),
    lesson("2-two", 2, "Not every blues has three lines", [
        learn("Some blues say a line, rhyme it, then come home in a shorter last line: no saying it twice. This one was printed in Chicago in 1921.", [
            ("A rhyming pair", "Grip, then trip"),
            ("Then home", f"Come on, let's go; {SAFE}"),
        ]),
        find("Find the notes: each waits until you're on it.", SHOALS_A[:9], SHOALS_TEMPO),
        play("Muscle Shoals Blues: the first lines, over the chords.", SHOALS_A, SHOALS_TEMPO, PITCH, chords=SHOALS_CHORDS),
    ]),
    lesson("2-challenge", 2, "Muscle Shoals Blues", [
        learn("Both of its verses' first lines, a breath between: pack your grip, then woke up this morning feeling glad.", [
            ("Two halves", "A full breath between"),
            TELL,
        ]),
        play("Both halves, over the chords.", SHOALS_BOTH, SHOALS_TEMPO, PITCH, chords=SHOALS_BOTH_CHORDS),
    ], challenge=True),
]


# ---- Unit 3: The band's turn ----

FIVES_LINE = [n for n in FIVES if n["beat"] < 16]
FALL_LINE = style(on(FIVES_LINE, "oh"), len(FIVES_LINE) - 1, "fall")
LAID = [dict(n, beat=num(n["beat"] + (0.5 if n["beat"] in (0, 16, 31) else 0)), length=num(n["length"] - (0.5 if n["beat"] in (0, 16, 31) else 0)))
        for n in FIVES]  # each line's first word an eighth late, the rest of the line on the beat
FALL_A = [{"beat": 0, "length": 1, "step": 4, "lyric": "oh"}, {"beat": 1, "length": 3, "step": 7, "lyric": "oh"}]

UNIT3 = [
    lesson("3-room", 3, "Leave room", [
        learn("In a blues the band answers you. Sing your line, hold its last word, and leave the gap for the band's turn.", [
            ("Your line, then theirs", "The band answers in your rest"),
            ("Come in on time", f"Right after the band's turn; {SAFE}"),
        ]),
        find("The Fives, a train song printed in Chicago in 1922. Find the first line's notes.", FIVES_LINE, FIVES_TEMPO),
        play("The verse with the band's turns: come in after each one, on time.", FIVES_FULL, FIVES_TEMPO,
             "Scored on coming in after each rest, on time and on pitch.", score="entry", chords=FIVES_FULL_CHORDS, partners=FIVES_FULL_TURNS),
        play("Again, every note on pitch.", FIVES_FULL, FIVES_TEMPO, PITCH, chords=FIVES_FULL_CHORDS, partners=FIVES_FULL_TURNS),
    ]),
    lesson("3-fall", 3, "The fall", [
        learn("At a line's end, a blues singer can let the last note fall away, like a sigh. The note lands first, then lets go.", [
            ("Land, then let go", "The fall comes at the very end"),
            ("Let the note go", f"Don't drive air at it; {SAFE}"),
        ]),
        choose("Listen to both, then choose.", FIVES_TEMPO, [
            ("Which one let the last note fall?", [clip(style(FALL_A, 1, "fall")), clip(FALL_A)], 0, "The first held its note, then let it fall away. The second just stopped."),
            ("Which one let the last note fall?", [clip(FALL_A), clip(style(FALL_A, 1, "fall"))], 1, "The second sighed down at the end; the first held still."),
        ]),
        play("The first line on \"oh\", its last note falling away at the end.", FALL_LINE, FIVES_TEMPO,
             "Scored on the fall asked for, and every note on pitch.", score="styled"),
        play("Now with the words: fall or not, as you like.", FIVES_LINE, FIVES_TEMPO, PITCH, chords=FIVES_CHORDS[:2]),
    ]),
    lesson("3-lay", 3, "Lay back", [
        learn("Blues singers often start a line a little after the beat, then settle onto it. Lay back, never rush.", [
            ("A little late", "Each line's first word, then on the beat"),
            ("Never rush", f"Let the band keep time; {SAFE}"),
        ]),
        play("The verse, each line's first word laid back.", LAID, FIVES_TEMPO, BEAT, chords=FIVES_CHORDS, partners=FIVES_TURNS, rhythm=True),
        selfcheck("Sing it once more, then hear yours beside the guide's.", FIVES_TEMPO, LAID[:9], ["Did you rush to catch up?", "Did each line settle onto the beat?"]),
    ]),
    lesson("3-challenge", 3, "The Fives", [
        learn("The whole verse with the band's turns: leave room, come in on time, and let a line end fall if you like.", [
            ("Your line, then theirs", "Three times"),
            TELL,
        ]),
        play("The verse, over the chords, with the band answering.", FIVES_FULL, FIVES_TEMPO, PITCH, chords=FIVES_FULL_CHORDS, partners=FIVES_FULL_TURNS),
    ], challenge=True),
]


# ---- Unit 4: Your blues ----

CRAM = [{"beat": i * 0.5, "length": 0.5, "step": s} for i, s in enumerate([7, 7, 3, 4, 0, 3, 4, 0, 3, 4, 0, 0, 3, 4, 0, 0])] + [{"beat": 8, "length": 4, "step": 0}]
SHORT = [{"beat": 0, "length": 1, "step": 7}, {"beat": 1, "length": 1, "step": 7}, {"beat": 2, "length": 6, "step": 0}]

UNIT4 = [
    lesson("4-first", 4, "Your first line", [
        learn("Your own blues, to this tune. Start with one line about your day: Woke up this morning, my coffee was gone.", [
            ("Woke up this morning", "My keys, my coffee, my bus was gone"),
            ("Say it out loud first", f"Then sing it to the tune; {SAFE}"),
        ]),
        choose("Three lines sung to the tune. Listen, then choose.", SG_TEMPO, [
            ("Which one fits the tune?", [clip(wordless(V1_A)), clip(CRAM), clip(SHORT)], 0, "The first fits one sound a note. The second crams too many in; the last runs out early."),
            ("Which one fits the tune?", [clip(SHORT), clip(CRAM), clip(wordless(V1_A))], 2, "The last one fits. The first runs short, the second crams."),
        ]),
        play("Sing your line to the tune, then say it again.", wordless(SHORTY.phrase(1, 0, 1)[0]), SG_TEMPO, TUNE, chords=SHORTY.phrase(1, 0, 1)[1]),
    ]),
    lesson("4-answer", 4, "Your answer line", [
        learn("Now answer your line: a last line that rhymes with it and comes home. Gone, then on; day, then away.", [
            ("Make it rhyme", "Gone, then on; day, then away"),
            ("Bring it home", f"The last note settles; {SAFE}"),
        ]),
        find("The answer line's tune, no words: find its notes.", wordless(V1_B), SG_TEMPO),
        play("Sing your answer line to the tune.", wordless(V1_B), SG_TEMPO, TUNE, chords=V1_B_CHORDS),
        selfcheck("Sing it once more, then hear yours beside the guide's.", SG_TEMPO, wordless(V1_B),
                  ["Did your answer rhyme with your first line?", "Did it turn the story, or close it?"]),
    ]),
    lesson("4-verse", 4, "Your verse", [
        learn("All three lines of your own verse, over the piano's chords: say it, say it again, answer it.", [
            ("Your three lines", "A breath after each"),
            TELL,
        ]),
        play("Your verse, over the chords.", wordless(V1), SG_TEMPO, TUNE, chords=V1_CHORDS),
        selfcheck("Sing it once more, then hear yours beside the guide's.", SG_TEMPO, wordless(V1),
                  ["Did your last line answer the first two?", "Could someone hear every word?"]),
    ]),
    lesson("4-challenge", 4, "Your blues", [
        learn("George W. Thomas and his daughter Hociel wrote these words in Chicago. First your first line from lesson 1, then their verse and yours, kept as a song.", [
            ("Then and now", "Your first line, beside today's"),
            ("Kept as a song", f"Their verse, then yours; {SAFE}"),
        ]),
        play("The first line, over the chords.", V1_A, SG_TEMPO, PITCH, chords=V1_A_CHORDS, thenAndNow=KEEP),
        play("Their verse, then yours to the same tune.", V1 + wordless(shift(V1, 48)), SG_TEMPO, TUNE,
             chords=V1_CHORDS + [dict(c, beat=num(c["beat"] + 48)) for c in V1_CHORDS]),
    ], challenge=True,
       keepSong={"title": EN("My blues"), "takes": [{"step": 2, "name": EN("Voice")}], "from": 2, "partners": [], "chords": EN("Piano")}),
]

course = {
    "id": "blues-singing", "version": 1, "reviewed": False, "title": EN("Blues singing"),
    "units": [
        {"id": "bl-three-lines", "title": EN("Three lines"), "colour": COLOUR, "lessons": UNIT1},
        {"id": "bl-the-blue-note", "title": EN("The blue note"), "colour": COLOUR, "lessons": UNIT2},
        {"id": "bl-the-bands-turn", "title": EN("The band's turn"), "colour": COLOUR, "lessons": UNIT3},
        {"id": "bl-your-blues", "title": EN("Your blues"), "colour": COLOUR, "lessons": UNIT4},
    ],
}

for u in course["units"]:
    for l in u["lessons"]:
        for i, s in enumerate(l["steps"]):
            ex = s.get("exercise") or {}
            if s["kind"] == "play":
                notes = ex["notes"]
                lo, hi = min(n["step"] for n in notes), max(n["step"] for n in notes)
                print(f"{l['id']}[{i}] {ex.get('score', 'default')}: {len(notes)} notes, {lo} to {hi},"
                      f" {timed_moments(notes, ex['tempo'])} timed, {len(judged_entries(notes))} entries{', rhythm' if ex.get('rhythm') else ''}")
if WRITE:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json.dump(course, open(OUT, "w"))
