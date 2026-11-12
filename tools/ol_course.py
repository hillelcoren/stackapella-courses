"""Singing in another language (docs/courses/other-languages.md in the app's repo): writes
course/plus/other-languages/course.json. Four library songs, a language a unit: Sakura Sakura
(Japanese), La Paloma (Spanish), Ave verum corpus (church Latin) and Shchedryk (Ukrainian). Every
line counts from the singer's comfortable note (0), laid round its middle; the challenges are song
steps with the library's other parts. Breaths a beginner can take are written in by tools/breaths.py.

The tracker hears pitch and voiced sound, not which vowel or consonant it is: steady notes (`lock`),
every syllable on its note and beat, a phrase on one breath (`line`) and the key held through a
repeated figure (`keyDrift`) are scored; vowel colour, the tap, the h and the joins are self-checks.
Pronunciation is taught on the cards, checked against the sources in the outline's "Sources".

    python3 -I tools/ol_course.py && python3 -I tools/coursefmt.py course/plus/other-languages/course.json
"""
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "course/plus/other-languages/course.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from breaths import add_breaths  # noqa: E402

BANNED = re.compile(r"\b(stars?|starring)\b|—|–", re.I)
SAFETY = "An easy jaw and a soft tongue: new sounds come from the tongue and lips, never from pushing. A medium volume, the middle of your voice. Stop if anything tightens."
TEMPO = 72

SAKURA = "templates/library/sakura-sakura.json"
PALOMA = "templates/library/la-paloma.json"
AVE = "templates/library/ave-verum-corpus.json"
SHCH = "templates/library/shchedryk.json"


def EN(text):
    assert not BANNED.search(text), text
    return {"en": text}


def card(title, detail):
    return {"title": EN(title), "detail": EN(detail)}


def learn(headline, cards, visual="phrase"):
    return {"kind": "learn", "headline": EN(headline), "steps": [card(*c) for c in cards], "visual": visual, "reviewed": False}


def fact(fid, text, source, url):
    return {"id": fid, "text": EN(text), "source": EN(source), "url": url}


def play(text, exercise, measures=None, kind="play"):
    step = {"kind": kind, "text": EN(text), "exercise": exercise}
    if measures:
        step["measures"] = EN(measures)
    return step


def selfcheck(text, model, questions, tempo=TEMPO):
    return {"kind": "selfcheck", "text": EN(text), "exercise": {"tempo": tempo, "model": {"notes": model}, "questions": [EN(q) for q in questions]}}


def choose(text, rounds, tempo=TEMPO):
    return {"kind": "choose", "text": EN(text), "exercise": {"tempo": tempo, "rounds": rounds},
            "measures": EN("Scored on the rounds you got right first time.")}


PITCH_BEAT = "Scored on every syllable on its pitch and on the beat. A swallowed or whispered syllable leaves its note silent."
STEADY = "Scored on each held note staying steady on its pitch. Whether the vowel stayed pure is yours to hear: play it back."
LINED = "Scored on the phrase: its notes on pitch, and its end steady."
KEY_HELD = "Scored on the figure keeping its key, round after round, with nothing under you."


def held(words, step=0, beats=2, rest=1, start=0):
    return [{"beat": start + k * (beats + rest), "length": beats, "step": step, "lyric": w} for k, w in enumerate(words)]


# ---- The library's songs: a phrase's tune, laid round its middle ----

def joined(lyric):
    """Two words' vowels on one note (sinalefa) show a tie: "Si a" -> "Si‿a"."""
    return re.sub(r"(?<=\S) (?=\S)", "‿", lyric.strip())


def tune(path, phrases, words=None):
    """The melody's notes in those phrases (counted from 0 over every section in order), steps from
    the line's middle pitch, so a wide line sits evenly round the comfortable note. `words`, when
    given, replaces the lyrics note for note (a transliteration)."""
    d = json.loads((REPO / path).read_text())
    mel = next(p for p in d["parts"] if p.get("melody"))
    spans = [span for sec in d["sections"] for span in sec["phrases"]]
    a, b = spans[phrases[0]][0], spans[phrases[-1]][1]
    notes = [n for n in mel["guide"]["notes"] if a - 1e-6 <= n["beat"] < b - 1e-6 and n.get("pitch") is not None]
    lo, hi = min(n["pitch"] for n in notes), max(n["pitch"] for n in notes)
    mid = (lo + hi) // 2
    sung = [n for n in notes if n.get("lyric")]
    if words is not None:
        assert len(words) == len(sung), (path, phrases, len(words), len(sung), [n["lyric"] for n in sung])
    swap = dict(zip((id(n) for n in sung), words or []))
    out = []
    for n in notes:
        note = {"beat": round(n["beat"] - a, 4), "length": n["length"], "step": n["pitch"] - mid}
        if n.get("lyric"):
            note["lyric"] = swap.get(id(n), joined(n["lyric"]))
        out.append(note)
    return out, d["tempo"]


VOWELS = "aeiouáéíóú"
PLAIN = str.maketrans("áéíóú", "aeiou")


def vowels_of(lyric):
    """A syllable's vowels only, for the vowel pass: "Cuan-" -> "ua", "ra" -> "a", "n" stays "n"."""
    word = lyric.lower().strip("-,.;:!?¡¿ ")
    if word == "y":
        return "i"
    found = "".join(c for c in word if c in VOWELS or c == "‿").translate(PLAIN)
    return found or word


def line(path, phrases, tempo, words=None, vowels=False, **extra):
    notes, _ = tune(path, phrases, words)
    if vowels:
        notes = [dict(n, lyric=vowels_of(n["lyric"])) if n.get("lyric") else n for n in notes]
    ex = {"tempo": tempo, "notes": notes, "turn": True}
    ex.update(extra)
    return ex


def song(template, phrases, tempo, part="soprano", **extra):
    ex = {"song": {"template": template, "part": part, "phrases": phrases, "with": "others"}, "tempo": tempo, "turn": False}
    ex.update(extra)
    return ex


def first_line(**extra):
    return line(SAKURA, [0], 66, **extra)


# Shchedryk's first two lines in the Ukrainian national transliteration (Resolution No. 55, 2010).
SHCH_1 = ["Shche-", "dryk,", "shche-", "dryk,", "shche-", "dri-", "voch-", "ka,"]
SHCH_2 = ["Pry-", "le-", "ti-", "la", "las-", "ti-", "voch-", "ka."]


def rhythm_clip(word, lengths, steps):
    beat, notes = 0, []
    for k, (length, step) in enumerate(zip(lengths, steps)):
        note = {"beat": beat, "length": length, "step": step}
        if k == 0:
            note["lyric"] = word
        notes.append(note)
        beat += length
    return {"notes": notes}


def pair_rounds(prompt, why, pairs):
    """Rounds of two clips, the right one first or second in turn. `prompt` may hold {word}: the word
    the clips sing, from the right clip's first lyric."""
    rounds = []
    for k, (right, wrong) in enumerate(pairs):
        first = k % 2 == 0
        word = right["notes"][0].get("lyric", "")
        rounds.append({"prompt": EN(prompt.format(word=word)), "clips": [right, wrong] if first else [wrong, right], "answer": 0 if first else 1, "why": EN(why)})
    return rounds


# ---- Unit 1: One sound, one note (Japanese, Sakura Sakura) ----

def ol_1_sakura():
    return {
        "id": "ol-1-sakura", "title": EN("Sakura"), "strictness": "relaxed",
        "fact": fact("sakura-1941-words", "In 1941 Japan's Ministry of Education gave Sakura new words, \"Noyama mo, sato mo\", for its school songbook: the teacher's book said the old words were too hard for children. This course sings the 1888 words.",
                     "National Diet Library, Reference Collaborative Database (Suita City Library): the two sets of words of Sakura sakura", "https://crd.ndl.go.jp/reference/detail?page=ref_view&id=1000154322"),
        "steps": [
            learn("Choirs learn a song in another language by ear: the tune's vowels first, then the words. Here's your first Japanese line: さくら さくら, \"sa-ku-ra, sa-ku-ra\", cherry blossoms.",
                  [("The vowels", "a u a, a u a"), ("Then the words", "sa-ku-ra, every a an \"ah\""), ("Then the choir", "With the other parts")], visual="vowels"),
            play("The first line on its vowels only: \"a u a, a u a\".", line(SAKURA, [0], 66, vowels=True)),
            play("Now the words: \"sa-ku-ra, sa-ku-ra\". The last \"ra\" stays \"rah\", never \"ruh\".", first_line(keep="ol.first-line", generous=True), PITCH_BEAT),
            play("Lines 1 and 2 with the other parts: \"sa-ku-ra, sa-ku-ra, ya-yo-i no so-ra wa\", the sky of spring.", song("sakura-sakura", [0, 1], 66), PITCH_BEAT),
        ],
    }


def ol_1_vowels():
    model = [{"beat": 0, "length": 2, "step": 0, "lyric": "noh-oo"}, {"beat": 3, "length": 2, "step": 0, "lyric": "no"}]
    ex = {"tempo": TEMPO, "notes": held(["no", "so", "ra", "mo", "zo"]), "turn": True, "drone": {"step": 0}, "score": "lock"}
    return {
        "id": "ol-1-vowels", "title": EN("Five whole vowels"),
        "steps": [
            learn("Japanese, Spanish and Latin keep every vowel whole, where English slides or shrinks them. This course's five: ah, eh, ee, o, oo. " + SAFETY,
                  [("No glide", "\"o\" stays o, never \"oh-oo\""), ("No \"uh\"", "Every vowel whole, even the last"), ("Japanese u", "Lips relaxed and flat, not pushed forward")], visual="vowels"),
            play("Sakura's own syllables, each held on one note: no, so, ra, mo, zo.", ex, STEADY),
            selfcheck("Tourist, then local: sing \"no\" the English way, \"noh-oo\", then the Japanese way. Hear them back to back.", model,
                      ["Which one sounds Japanese?", "Did the second \"no\" stay \"o\" to the end?"]),
        ],
    }


def ol_1_mora():
    pairs = [
        (rhythm_clip("kagiri", [1, 1, 2], [0, 2, 0]), rhythm_clip("kagiri", [2, 2], [0, 0])),
        (rhythm_clip("yayoi", [1, 1, 2], [0, -2, -3]), rhythm_clip("yayoi", [1, 3], [0, -2])),
        (rhythm_clip("miwatasu", [1, 1, 1, 1], [0, 2, 3, 2]), rhythm_clip("miwatasu", [1, 1, 2], [0, 2, 3])),
    ]
    return {
        "id": "ol-1-mora", "title": EN("Every small sound"),
        "fact": fact("bidakuon-textbook", "A Japanese middle-school music book still teaches the nasal g: pupils underline where a g in a song's words turns into a soft \"ng\" through the nose, and sing it that way.",
                     "Kyōiku Shuppan, Chūgaku Ongaku 1, p. 24", "https://www.kyoiku-shuppan.co.jp/docs/r7chuu/ongaku/d-book/pageindices/index17.html"),
        "steps": [
            learn("In Japanese, every small sound gets its own beat. \"Ya-yo-i\" is three notes, never \"ya-yoy\".",
                  [("Every sound", "ya-yo-i, ni-o-i: two vowels, two notes"), ("The quiet su", "Whispered in speech, sung here"), ("ka-gi-ri", "A soft \"ng\" is the old way; a plain g is fine")], visual="echo"),
            choose("Listen to each, then choose.", pair_rounds("Which \"{word}\" gives every sound its own note?",
                   "The other runs two sounds together, the way English would.", pairs)),
            play("Line 3: \"mi-wa-ta-su ka-gi-ri\", as far as the eye can see. Sing the \"su\".", line(SAKURA, [2], 66), PITCH_BEAT),
        ],
    }


def ol_1_challenge():
    return {
        "id": "ol-1-challenge", "title": EN("Sakura with the others"), "challenge": True,
        "steps": [
            learn("Lesson 1's line to hear how far you've come, then the song's last line and its hummed n, then three lines with the other parts.",
                  [("Then and now", "Lesson 1's line, today"), ("The last n", "Hummed at the back, a note of its own"), ("The choir", "Lines 1 to 3")]),
            play("Lesson 1's line.", first_line(thenAndNow="ol.first-line"), PITCH_BEAT),
            play("The last line: \"mi-ni-yu-ka-n\", let's go and see. The n is hummed, with the back of the tongue.", line(SAKURA, [6], 66), PITCH_BEAT),
            play("Lines 1 to 3 with the other parts.", song("sakura-sakura", [0, 1, 2], 66), PITCH_BEAT),
        ],
    }


# ---- Unit 2: Vowels that join (Spanish, La Paloma) ----

def habanera_clip(straight):
    lengths = [0.5, 0.5, 0.5, 0.5] * 2 if straight else [0.75, 0.25, 0.5, 0.5] * 2
    steps = [0, 0, 2, 4, 4, 2, 0, -1]
    return rhythm_clip("pa-lo-ma", lengths, steps)


def ol_2_habanera():
    rounds = pair_rounds("Which one is the habanera?", "The habanera's beat is long, short, then two even: the rhythm Iradier brought back from Cuba.",
                         [(habanera_clip(False), habanera_clip(True)) for _ in range(3)])
    return {
        "id": "ol-2-habanera", "title": EN("The habanera"),
        "steps": [
            learn("La Paloma's refrain: \"Si a tu ventana llega una paloma\", if a dove comes to your window. Spanish vowels stay whole, even unstressed.",
                  [("The rhythm", "Long, short, then two even"), ("Whole vowels", "pa-LO-ma, every a an \"ah\""), ("Two vowels, one note", "\"Si‿a\" shares a note")], visual="vowels"),
            choose("Listen to each, then choose.", rounds, tempo=66),
            play("The refrain's first line on its vowels.", line(PALOMA, [4], 60, vowels=True)),
            play("Now the words, on the beat.", line(PALOMA, [4], 60), PITCH_BEAT),
        ],
    }


def ol_2_join():
    pairs = [
        (rhythm_clip("si a tu", [1, 1], [0, 2]), rhythm_clip("si a tu", [0.5, 0.5, 1], [0, 0, 2])),
        (rhythm_clip("que es mi", [1, 1], [0, -1]), rhythm_clip("que es mi", [0.5, 0.5, 1], [0, 0, -1])),
        (rhythm_clip("la Habana", [1, 1, 1], [0, 2, 0]), rhythm_clip("la Habana", [0.5, 0.5, 1, 1], [0, 0, 2, 0])),
    ]
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "Si‿a"}, {"beat": 1, "length": 1, "step": 2, "lyric": "tu"}]
    return {
        "id": "ol-2-join", "title": EN("Two vowels, one note"),
        "fact": fact("navarro-tomas-timbre", "In 1918 the phonetician Tomás Navarro Tomás wrote that English speakers give Spanish close vowels, like the e of \"pena\" and the o of \"canto\", \"a less fixed and even timbre than the Castilian ear requires\".",
                     "Navarro Tomás, Manual de pronunciación española (1918), §43", "https://archive.org/details/manualdepronunci00navauoft"),
        "steps": [
            learn("Japanese gave every vowel its own note. Spanish joins them: where the music gives one note, two words' vowels share it.",
                  [("Si‿a, que‿es", "One note, both vowels, no stop"), ("The h is silent", "\"la‿Ha-ba-na\": la-AH-ba-na"), ("No catch", "Vowels on their own notes still flow")], visual="echo"),
            choose("Listen to each, then choose.", pair_rounds("Which \"{word}\" joins the vowels on one note?",
                   "The other splits them over two notes, with a stop between.", pairs), tempo=66),
            play("\"Cuando salí de la Habana, ¡válgame Dios!\": when I left Havana, God help me!", line(PALOMA, [0], 60), PITCH_BEAT),
            selfcheck("\"Si a tu\", then hear it back.", model, ["Did both vowels fit on the one note, with no stop between?"], tempo=60),
        ],
    }


def ol_2_light():
    model = [{"beat": 0, "length": 1, "step": 0, "lyric": "ven-"}, {"beat": 1, "length": 1, "step": 2, "lyric": "ta-"}, {"beat": 2, "length": 1, "step": 0, "lyric": "na"},
             {"beat": 4, "length": 1, "step": 0, "lyric": "ven-"}, {"beat": 5, "length": 1, "step": 2, "lyric": "ta-"}, {"beat": 6, "length": 1, "step": 0, "lyric": "na"}]
    return {
        "id": "ol-2-light", "title": EN("Light consonants"),
        "fact": fact("carmen-arreglito", "Bizet took Carmen's famous Habanera from Iradier's habanera \"El Arreglito\", thinking it was a folk song. The vocal score notes that it is \"imitated from a Spanish song\".",
                     "Bizet, Carmen, vocal score (G. Schirmer, 1895), Internet Archive", "https://archive.org/details/carmenoperainfou00bize2"),
        "steps": [
            learn("Spanish consonants are light and quick, so the vowels can sing.",
                  [("r is one tap", "ca-RI-ño, TRA-ta-la: the tap you met in Sakura"), ("v is a soft b", "ven-TA-na, never an English v"), ("ll is y", "\"LLE-ga\" is YEH-gah; in old Castilian, nearer \"ly\"")]),
            play("\"Trátala con cariño que es mi persona\": treat it kindly, for it is me.", line(PALOMA, [5], 60), PITCH_BEAT),
            selfcheck("Tourist, then local: \"ventana\" with an English v, then with a soft b, lips barely touching.", model,
                      ["Which one sounds Spanish?"], tempo=60),
        ],
    }


def ol_2_challenge():
    rounds = pair_rounds("Which one is the habanera?", "Long, short, then two even.", [(habanera_clip(False), habanera_clip(True)) for _ in range(2)])
    return {
        "id": "ol-2-challenge", "title": EN("La Paloma's refrain"), "challenge": True,
        "steps": [
            learn("The rhythm, the joins and every vowel whole, with the other parts.",
                  [("The habanera", "Quicker now"), ("The joins", "Si‿a, que‿es"), ("The last a", "pa-lo-ma, per-so-na: \"ah\" to the end")]),
            choose("Listen to each, then choose.", rounds, tempo=76),
            play("The refrain's first two lines with the other parts.", song("la-paloma", [4, 5], 60), PITCH_BEAT),
        ],
    }


# ---- Unit 3: The long line (church Latin, Ave verum corpus) ----

AVE_WORDS = "\"Ave verum corpus, natum de Maria virgine\": hail, true body, born of the Virgin Mary."


def ol_3_latin():
    model = [{"beat": 0, "length": 2, "step": 0, "lyric": "A-"}, {"beat": 2, "length": 2, "step": 0, "lyric": "ve"},
             {"beat": 5, "length": 2, "step": 0, "lyric": "A-"}, {"beat": 7, "length": 2, "step": 0, "lyric": "ve"}]
    tried = [{"beat": 0, "length": 2, "step": 0, "lyric": "A-"}, {"beat": 2, "length": 2, "step": 0, "lyric": "ve,"},
             {"beat": 5, "length": 2, "step": 2, "lyric": "ve-"}, {"beat": 7, "length": 2, "step": 2, "lyric": "rum"},
             {"beat": 10, "length": 2, "step": 4, "lyric": "cor-"}, {"beat": 12, "length": 2, "step": 4, "lyric": "pus"}]
    return {
        "id": "ol-3-latin", "title": EN("Ah-veh, not Ay-vee"),
        "fact": fact("liber-one-sound", "The Liber Usualis, the Catholic Church's book of chant, says of Latin's vowels: \"Each vowel has one sound; a mixture or sequence of sounds would be fatal to good Latin pronunciation.\"",
                     "The Liber Usualis (1961), Rules for Interpretation, p. xxxvi", "https://archive.org/details/TheLiberUsualis1961"),
        "steps": [
            learn("A medieval hymn for the Eucharist, in Mozart's setting. " + AVE_WORDS,
                  [("e as in \"red\"", "AH-veh, VEH-room, never \"ay\""), ("Every vowel whole", "KAWR-poos, not \"corpuss\""), ("A gentle start", "Vowel words begin softly, with no catch")], visual="vowels"),
            play("\"A-ve, ve-rum, cor-pus\", each syllable held.", {"tempo": 66, "notes": tried, "turn": True}),
            play("\"Ave, ave verum corpus\", slowly, one breath a phrase. The \"-um\" is \"oo\", closing to m at the very end.", line(AVE, [0, 1], 66), LINED, ),
            selfcheck("Tourist, then local: \"Ay-vee\", then \"Ah-veh\".", model, ["Which one sounds like church Latin?"], tempo=66),
        ],
    }


def ol_3_letters():
    pairs = [
        (rhythm_clip("homine", [1, 1, 2], [0, 2, 0]), rhythm_clip("homine", [2, 2], [0, 0])),
        (rhythm_clip("virgine", [1, 1, 2], [0, -1, -3]), rhythm_clip("virgine", [2, 2], [0, -3])),
    ]
    return {
        "id": "ol-3-letters", "title": EN("Soft c, soft g, silent h"),
        "steps": [
            learn("Church Latin reads its letters the Roman way.",
                  [("c and g before e or i", "CRU-ce is KROO-cheh; VIR-gi-ne is VEER-jee-neh"), ("h is silent", "HO-mi-ne is AW-mee-neh, as in Spanish"), ("Every syllable", "vir-gi-ne has three, never \"virg-neh\"")]),
            choose("Listen to each, then choose.", pair_rounds("Which \"{word}\" sings every syllable?", "The other drops the middle one, as English would.", pairs), tempo=66),
            play("\"In cruce pro homine\": on the cross, for mankind. One breath, after \"cruce\".", line(AVE, [4], 80), PITCH_BEAT),
        ],
    }


def breath_clip(gap):
    lengths, steps = [1, 1, 1, 1], [0, 2, 4, 2]
    notes, beat = [], 0
    for k, (length, step) in enumerate(zip(lengths, steps)):
        note = {"beat": beat, "length": length - (gap if k == 1 else 0), "step": step}
        if k == 0:
            note["lyric"] = "natum de Maria"
        notes.append(note)
        beat += length
    return {"notes": notes}


def ol_3_line():
    rounds = pair_rounds("Which one breathes in the middle of a word?", "Its sound stops inside \"Maria\": a breath belongs between words.",
                         [(breath_clip(0.5), breath_clip(0)), (breath_clip(0.35), breath_clip(0))])
    return {
        "id": "ol-3-line", "title": EN("One breath, one line"),
        "fact": fact("ave-verum-13th-century", "The words are much older than Mozart: the hymn is first found in a 13th-century Franciscan manuscript, now in Chicago's Newberry Library.",
                     "Ave verum corpus, English Wikipedia (citing Rubin, 1992)", "https://en.wikipedia.org/wiki/Ave_verum_corpus"),
        "steps": [
            learn("Mozart's line is long and joined: the consonants quick between the vowels, and a breath only between words, never inside one.",
                  [("Double letters", "PAS-sum, im-mo-LA-tum: held a moment"), ("The tap", "Ma-RI-a, VE-rum: one tap, as in Spanish"), ("Breathe between words", "Here, after \"Maria\"")], visual="breath"),
            choose("Listen to each, then choose.", rounds, tempo=66),
            play("\"Natum de Maria virgine\", one breath after \"Maria\".", line(AVE, [2], 80), LINED),
        ],
    }


def ol_3_challenge():
    rounds = pair_rounds("Which one breathes in the middle of a word?", "A breath belongs between words.", [(breath_clip(0.4), breath_clip(0)), (breath_clip(0.3), breath_clip(0))])
    return {
        "id": "ol-3-challenge", "title": EN("Ave verum"), "challenge": True,
        "steps": [
            learn("The opening with the alto, tenor and bass: whole vowels, soft g, one breath a phrase. " + AVE_WORDS,
                  [("e as in \"red\"", "AH-veh, VEH-room"), ("Soft g", "VEER-jee-neh"), ("One breath", "At Mozart's rests")], visual="harmony"),
            choose("Listen to each, then choose.", rounds, tempo=66),
            play("\"Ave, ave verum corpus, natum de Maria virgine\", with the other three parts.", song("ave-verum-corpus", [0, 1, 2], 72, score="line"), LINED),
        ],
    }


# ---- Unit 4: Quick words, light tongue (Ukrainian, Shchedryk) ----

SHCH_SAFETY = "The figure invites pushing: keep it light, a medium volume, the jaw easy. Stop if anything tightens."


def figure(times, tempo):
    notes, _ = tune(SHCH, [0], SHCH_1)
    span = max(n["beat"] + n["length"] for n in notes) + 1  # a beat's rest between rounds, to breathe
    out = []
    for k in range(times):
        out += [dict(n, beat=round(n["beat"] + k * span, 4)) for n in notes]
    return {"tempo": tempo, "notes": out, "turn": True}


def ol_4_letters():
    notes, _ = tune(SHCH, [0], SHCH_1)
    slow = [{"beat": k * 3, "length": 2, "step": n["step"], "lyric": n["lyric"]} for k, n in enumerate(notes)]
    model = [{"beat": 0, "length": 2, "step": 0, "lyric": "dryk"}, {"beat": 3, "length": 2, "step": 0, "lyric": "dri"}]
    return {
        "id": "ol-4-letters", "title": EN("Eleven letters"),
        "steps": [
            learn("Shchedryk, a Ukrainian New Year song. Its first line in Cyrillic: Щедрик, щедрик, щедрівочка. In our letters: Shchedryk, shchedryk, shchedrivochka.",
                  [("щ is \"shch\"", "As in \"fresh cheese\", never a plain \"sh\""), ("и and і", "dryk as in \"sit\"; dri as in \"see\""), ("г is a soft h", "A voiced h, never a g")]),
            play("The figure slowly, each sound held: Shche-dryk, shche-dri-voch-ka.", {"tempo": 60, "notes": slow, "turn": True, "score": "lock"}, STEADY),
            selfcheck("\"Dryk\", then \"dri\", then hear them back.", model, ["Did \"dryk\" sound like \"sit\", and \"dri\" like \"see\"?"], tempo=60),
        ],
    }


def ol_4_figure():
    late = [{"notes": [dict(n, beat=n["beat"] + (0.2 if k else 0)) for k, n in enumerate(c["notes"])]} for c in [figure(1, 80)]]
    on = [{"notes": figure(1, 80)["notes"]}]
    rounds = pair_rounds("Which one keeps every syllable on the beat?", "In the other, the syllables after the first drag late.", [(on[0], late[0]), (on[0], late[0])])
    ex = figure(4, 96)
    ex["score"] = "keyDrift"
    return {
        "id": "ol-4-figure", "title": EN("The figure, faster"),
        "fact": fact("leontovych-twenty-years", "Mykola Leontovych was a perfectionist who could spend years on one arrangement before showing it to anyone. Shchedryk was first heard in Kyiv in 1916, when the conductor Oleksander Koshyts persuaded him to let it be sung.",
                     "McDermott, America Magazine (17 November 2022)", "https://www.americamagazine.org/arts-culture/2022/11/17/carol-bells-ukraine-centennial-244117"),
        "steps": [
            learn("Four notes, round and round. Choirs go flat repeating it, so the key is the test, a step faster each time.",
                  [("Every o whole", "VOCH-ka, never \"vuch-kuh\""), ("The shch early", "Before the beat, the vowel on it"), ("Light", SHCH_SAFETY)], visual="ladder"),
            choose("Listen to each, then choose.", rounds, tempo=80),
            play("The figure twice, at 60.", figure(2, 60)),
            play("Four times round, at 80, in the same key.", dict(figure(4, 80), score="keyDrift"), KEY_HELD),
            play("Four times round, at 96. " + SHCH_SAFETY, ex, KEY_HELD),
        ],
    }


def ol_4_swallow():
    model = [{"beat": k, "length": 1, "step": 0, "lyric": w} for k, w in enumerate(["las-", "ti-", "voch-", "ka"])] + \
            [{"beat": 5 + k, "length": 1, "step": 0, "lyric": w} for k, w in enumerate(["las-", "ti-", "voch-", "ka"])]
    return {
        "id": "ol-4-swallow", "title": EN("The swallow's line"),
        "fact": fact("wilhousky-new-words", "\"Carol of the Bells\" is Shchedryk's tune with new English words by Peter Wilhousky, published in 1936. They aren't a translation: the Ukrainian words are about a swallow, not bells.",
                     "America Magazine (17 November 2022)", "https://www.americamagazine.org/arts-culture/2022/11/17/carol-bells-ukraine-centennial-244117"),
        "steps": [
            learn("Line 2: Прилетіла ластівочка, \"Pryletila lastivochka\": a little swallow has flown in.",
                  [("The stress", "prih-leh-TEE-lah, LAHS-tee-voch-kah"), ("ti is soft", "A t with the tongue high, never \"chee\""), ("A dark l", "As in \"full\"")]),
            play("Line 2 at 80.", line(SHCH, [1], 80, SHCH_2), PITCH_BEAT),
            selfcheck("Tourist, then local: \"LAS-tuh-vuch-kuh\", then every vowel whole.", model, ["Which one sounds Ukrainian?"], tempo=80),
        ],
    }


def ol_4_challenge():
    two, _ = tune(SHCH, [0, 1], SHCH_1 + SHCH_2)
    return {
        "id": "ol-4-challenge", "title": EN("Shchedryk"), "challenge": True,
        "steps": [
            learn("Your first Japanese line, from lesson 1, and now; then Shchedryk with the choir, in its own letters.",
                  [("Then and now", "Lesson 1's line, today"), ("The two lines", "In our letters, at 96"), ("The choir", "In Cyrillic, with the other parts")]),
            play("Lesson 1's line.", first_line(thenAndNow="ol.first-line"), PITCH_BEAT),
            play("Lines 1 and 2 at 96. " + SHCH_SAFETY, {"tempo": 96, "notes": two, "turn": True}, PITCH_BEAT),
            learn("The same two lines in Cyrillic: Щедрик, щедрик, щедрівочка, прилетіла ластівочка.",
                  [("Щедрик", "Shche-dryk"), ("щедрівочка", "shche-dri-voch-ka"), ("прилетіла ластівочка", "pry-le-ti-la las-ti-voch-ka")], visual="harmony"),
            play("The song's last two lines with the alto, tenor and bass, at 96.", song("shchedryk", [12, 13], 96), PITCH_BEAT),
        ],
    }


course = {
    "id": "other-languages", "version": 1, "reviewed": False, "title": EN("Singing in another language"),
    "units": [
        {"id": "ol-japanese", "title": EN("One sound, one note"), "colour": 5, "lessons": [ol_1_sakura(), ol_1_vowels(), ol_1_mora(), ol_1_challenge()]},
        {"id": "ol-spanish", "title": EN("Vowels that join"), "colour": 5, "lessons": [ol_2_habanera(), ol_2_join(), ol_2_light(), ol_2_challenge()]},
        {"id": "ol-latin", "title": EN("The long line"), "colour": 5, "lessons": [ol_3_latin(), ol_3_letters(), ol_3_line(), ol_3_challenge()]},
        {"id": "ol-ukrainian", "title": EN("Quick words, light tongue"), "colour": 5, "lessons": [ol_4_letters(), ol_4_figure(), ol_4_swallow(), ol_4_challenge()]},
    ],
}
# A self-check is never a lesson's last step (the game review): it goes just before the last sung
# step, so the contrast comes first and the lesson ends on a scored take.
for unit in course["units"]:
    for lesson in unit["lessons"]:
        steps = lesson["steps"]
        if steps[-1]["kind"] == "selfcheck":
            check = steps.pop()
            last = max(i for i, st in enumerate(steps) if st["kind"] == "play")
            steps.insert(last, check)

for where in add_breaths(course):
    print("no room to breathe:", where)


def natum_breath():
    """"Natum de Maria virgine" breathes once, between words, after "Maria": its "a" is cut to three
    quarters of a beat and the rest comes three quarters later (a beginner's comma, at 80). The
    general rule would breathe after the held "na-", inside a word."""
    notes, _ = tune(AVE, [2])
    out = []
    for n in notes:
        n = dict(n)
        if n["beat"] == 7:
            n["length"] = 0.75
        elif n["beat"] >= 8:
            n["beat"] += 0.5
        out.append(n)
    return out


def breath_after(phrases, beat, cut, shift):
    """A Latin line's notes with one breath between words: the note at `beat` shortened by `cut`,
    everything after it `shift` beats later. The general rule breathes after long melisma notes,
    inside words ("cru-ce", "ho-mi-ne")."""
    notes, _ = tune(AVE, phrases)
    out = []
    for n in notes:
        n = dict(n)
        if n["beat"] == beat:
            n["length"] -= cut
        elif n["beat"] > beat:
            n["beat"] = round(n["beat"] + shift, 4)
        out.append(n)
    return out


def set_notes(lesson_id, notes, tempo):
    """The lesson's last sung step gets these notes."""
    lesson = next(l for u in course["units"] for l in u["lessons"] if l["id"] == lesson_id)
    step = [st for st in lesson["steps"] if st["kind"] == "play"][-1]
    step["exercise"].update(notes=notes, tempo=tempo)


set_notes("ol-3-line", natum_breath(), 80)
set_notes("ol-3-letters", breath_after([4], 7, 0.5, 0.25), 80)  # after "cruce", before "pro"
OUT.parent.mkdir(parents=True, exist_ok=True)
json.dump(course, open(OUT, "w"), ensure_ascii=False)
