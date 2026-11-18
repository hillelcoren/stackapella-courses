"""es_strings.py missing.json out.json : Spanish for the song course's new English strings (the patterns other song
courses use, and this song's two facts), for tools/i18n.py add es songs."""
import json, re, sys
T = 'Cantique de Jean Racine'
FIXED = {
    T: T,
    f'{T}: hear the whole song first, then the tune on its own.': f'{T}: escucha primero la canción entera y luego la melodía sola.',
    f'Record the tune of {T} in Sing, with the other parts playing.': f'Graba la melodía de {T} en Cantar, con las demás voces sonando.',
    'The first printing calls Fauré "organist of the choir school of Saint-Sulpice" and is dedicated "To Monsieur César Franck". Schoen of Paris printed it as No. 10 in the first issue of Écho des Maîtrises, a new series of unpublished church music edited by Romain Bussine.':
        'La primera impresión llama a Fauré "organista de la escolanía de Saint-Sulpice" y está dedicada "A Monsieur César Franck". Schoen, de París, la publicó como n.º 10 del primer número de Écho des Maîtrises, una nueva colección de música religiosa inédita dirigida por Romain Bussine.',
    'Écho des Maîtrises, first issue (Paris: F. Schoen, undated, plate F. 309 S.), cover and p. 2, No. 10; Bibliothèque nationale de France, Vmg. 17107 (I,10), read from the scan':
        'Écho des Maîtrises, primer número (París: F. Schoen, sin fecha, plancha F. 309 S.), cubierta y p. 2, n.º 10; Bibliothèque nationale de France, Vmg. 17107 (I,10), leído en el escaneo',
    'In the French Roman Breviary that printed Racine\'s hymns, the second verse asks for "ta grâce invincible" and a sleep "qui rend l\'âme insensible". "Puissante" and "languissante", the words Fauré set, come from the edition of Racine\'s son Louis, and Racine\'s 1865 editor thought the change was the son\'s.':
        'En el Breviario romano en francés que imprimió los himnos de Racine, la segunda estrofa pide "ta grâce invincible" (tu gracia invencible) y habla de un sueño "qui rend l\'âme insensible" (que vuelve insensible el alma). "Puissante" y "languissante", las palabras que puso Fauré, vienen de la edición de Louis Racine, hijo del poeta, y el editor de Racine de 1865 pensaba que el cambio era del hijo.',
    'Œuvres de J. Racine, ed. Paul Mesnard, vol. 4 (Paris: Hachette, 1865), pp. 112 and 113, "Le mardi, à matines", and note 3; University of Toronto copy, read from the scan':
        'Œuvres de J. Racine, ed. Paul Mesnard, vol. 4 (París: Hachette, 1865), pp. 112 y 113, "Le mardi, à matines", y la nota 3; ejemplar de la University of Toronto, leído en el escaneo',
}
PART = {'alto': 'contralto', 'tenor': 'tenor', 'bass': 'bajo', 'soprano': 'soprano'}

def es(en):
    if en in FIXED:
        return FIXED[en]
    m = re.fullmatch(re.escape(T) + r': hear the whole song first, then the (\w+) part on its own\.', en)
    if m:
        return f'{T}: escucha primero la canción entera y luego la voz de {PART[m.group(1)]} sola.'
    m = re.fullmatch(r'Record the (\w+) part of ' + re.escape(T) + r' in Sing, with the other parts playing\.', en)
    if m:
        return f'Graba la voz de {PART[m.group(1)]} de {T} en Cantar, con las demás voces sonando.'
    m = re.fullmatch(r'Now lines (\d+) (and|to) (\d+) joined, with the guide\.', en)
    if m:
        return f'Ahora las frases {m.group(1)} {"y" if m.group(2) == "and" else "a"} {m.group(3)} seguidas, con la guía.'
    m = re.fullmatch(r'Lines (\d+) (and|to) (\d+)', en)
    if m:
        return f'Frases {m.group(1)} {"y" if m.group(2) == "and" else "a"} {m.group(3)}'
    m = re.fullmatch(r'Now lines (\d+) and (\d+) in their places, the other parts singing the lines? between, with the guide\.', en)
    if m:
        between = int(m.group(2)) - int(m.group(1)) - 1
        tail = 'la frase intermedia' if between == 1 else 'las frases intermedias'
        return f'Ahora las frases {m.group(1)} y {m.group(2)} en su lugar, con la guía; las demás voces cantan {tail}.'
    m = re.fullmatch(r'(.+) start to end, with the guide\.', en)
    if m:
        return f'"{m.group(1)}", de principio a fin, con la guía.'
    raise SystemExit('no Spanish for: ' + en)

items = json.load(open(sys.argv[1], encoding='utf-8'))
out = {x['en']: es(x['en']) for x in items}
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'strings')
