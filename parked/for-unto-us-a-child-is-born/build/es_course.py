"""Spanish for the song course's new words: reads `tools/i18n.py missing es songs` (JSON on stdin) and writes the map
{english: spanish} for `tools/i18n.py add es songs <file>`. Patterns follow i18n/es/songs.json; the facts by hand."""
import json, re, sys
TITLE = 'For Unto Us a Child Is Born'
HAND = {
 TITLE: TITLE,
 "Handel had only a few of the string players accompany most of this chorus, marked \"senza Ripieni\", and brought in the whole band, \"con Ripieni\", for the shouts of \"Wonderful, Counsellor\". Ebenezer Prout's 1902 edition, the one sung here, saves its organ for exactly those places.":
 "Handel hizo que solo unos pocos de los instrumentistas de cuerda acompañaran casi todo este coro, con la indicación \"senza Ripieni\", y que entrara la orquesta entera, \"con Ripieni\", en los gritos de \"Wonderful, Counsellor\". La edición de Ebenezer Prout de 1902, la que se canta aquí, reserva el órgano justo para esos momentos.",
 "Ebenezer Prout (editor), Handel, The Messiah, full score (London: Novello and Company, Limited, copyright 1902), preface, pp. v and vi, and No. 12, pp. 93 to 113; University of Toronto, Faculty of Music copy, read from the scan":
 "Ebenezer Prout (editor), Handel, The Messiah, partitura completa (Londres: Novello and Company, Limited, copyright 1902), prefacio, pp. v y vi, y n.º 12, pp. 93 a 113; ejemplar de la Facultad de Música de la Universidad de Toronto, leído en el escaneo",
 "In Mozart's German arrangement of Messiah, much of this chorus was given to solo voices. Prout wrote in 1902 that in England it was always sung by the whole choir, as Handel intended.":
 "En el arreglo alemán de Mozart del Mesías, buena parte de este coro pasó a voces solistas. Prout escribió en 1902 que en Inglaterra siempre lo cantaba el coro entero, como Handel quería.",
 "Ebenezer Prout (editor), Handel, The Messiah, full score (London: Novello and Company, Limited, copyright 1902), preface, p. iv; University of Toronto, Faculty of Music copy, read from the scan":
 "Ebenezer Prout (editor), Handel, The Messiah, partitura completa (Londres: Novello and Company, Limited, copyright 1902), prefacio, p. iv; ejemplar de la Facultad de Música de la Universidad de Toronto, leído en el escaneo",
}
PART = {'alto': 'la voz de contralto', 'tenor': 'la voz de tenor', 'bass': 'la voz de bajo', 'soprano': 'la voz de soprano'}
RULES = [
 (r'^(.*): hear the whole song first, then the tune on its own\.$', lambda m: f'{m[1]}: escucha primero la canción entera y luego la melodía sola.'),
 (r'^(.*): hear the whole song first, then the (\w+) part on its own\.$', lambda m: f'{m[1]}: escucha primero la canción entera y luego {PART[m[2]]} sola.'),
 (r'^Record the tune of (.*) in Sing, with the other parts playing\.$', lambda m: f'Graba la melodía de {m[1]} en Cantar, con las demás voces sonando.'),
 (r'^Record the (\w+) part of (.*) in Sing, with the other parts playing\.$', lambda m: f'Graba {PART[m[1]]} de {m[2]} en Cantar, con las demás voces sonando.'),
 (r'^Now lines (\d+) and (\d+) joined, with the guide\.$', lambda m: f'Ahora las frases {m[1]} y {m[2]} seguidas, con la guía.'),
 (r'^Now lines (\d+) to (\d+) joined, with the guide\.$', lambda m: f'Ahora las frases {m[1]} a {m[2]} seguidas, con la guía.'),
 (r'^Now lines (\d+) and (\d+) joined: hear them, then sing them back\.$', lambda m: f'Ahora las frases {m[1]} y {m[2]} seguidas: escúchalas y repítelas.'),
 (r'^Now lines (\d+) to (\d+) joined: hear them, then sing them back\.$', lambda m: f'Ahora las frases {m[1]} a {m[2]} seguidas: escúchalas y repítelas.'),
 (r'^Lines (\d+) and (\d+)$', lambda m: f'Frases {m[1]} y {m[2]}'),
 (r'^Lines (\d+) to (\d+)$', lambda m: f'Frases {m[1]} a {m[2]}'),
 (r'^Line (\d+) is line (\d+) again\. Sing it with the guide\.$', lambda m: f'La frase {m[1]} repite la frase {m[2]}. Cántala con la guía.'),
 (r'^Line (\d+) is the tune of line (\d+) again, with new words\. Sing it with the guide\.$', lambda m: f'La frase {m[1]} repite la melodía de la frase {m[2]}, con otra letra. Cántala con la guía.'),
 (r'^(.*) start to end, with the guide\.$', lambda m: f'"{m[1]}", de principio a fin, con la guía.'),
]
missing = json.load(sys.stdin)
out, left = {}, []
for item in missing:
    en = item['en']
    if en in HAND:
        out[en] = HAND[en]; continue
    for pat, fn in RULES:
        m = re.match(pat, en)
        if m:
            out[en] = fn(m); break
    else:
        left.append(en)
json.dump(out, sys.stdout, ensure_ascii=False, indent=1)
if left:
    sys.stderr.write('untranslated: ' + json.dumps(left, ensure_ascii=False) + '\n')
