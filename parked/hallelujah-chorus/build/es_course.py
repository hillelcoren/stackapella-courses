# Spanish for the Hallelujah Chorus song course's new words, in the patterns the songs file already uses.
# usage: python3 -I es_course.py missing.json out.json
import json
import re
import sys

PARTS = {'tune': 'la melodía', 'alto part': 'la voz de contralto', 'bass part': 'la voz de bajo', 'tenor part': 'la voz de tenor'}
REC = {'tune': 'la melodía', 'alto part': 'la voz de contralto', 'bass part': 'la voz de bajo', 'tenor part': 'la voz de tenor'}
SECTIONS = {
    'Hallelujah': '"Hallelujah"',
    'For the Lord God Omnipotent reigneth': '"For the Lord God Omnipotent reigneth"',
    'The kingdom of this world': '"The kingdom of this world"',
    'And He shall reign': '"And He shall reign"',
    'King of Kings': '"King of Kings"',
    'And He shall reign, again': '"And He shall reign", otra vez',
    'King of Kings, and Hallelujah': '"King of Kings" y "Hallelujah"',
}
FACTS = {
    'In this chorus Handel sometimes sets the end of one "Hallelujah" and the start of the next to a single note, as in the altos\' "lu-jah, Hal-". Ebenezer Prout wrote in 1902 that every published edition had followed Walsh\'s printing instead, and he restored Handel\'s text: the altos in bar 24, the sopranos in bar 30 and the basses in bars 31 and 32.':
        'En este coro Handel a veces pone el final de un "Hallelujah" y el comienzo del siguiente en una sola nota, como en el "lu-jah, Hal-" de las contraltos. Ebenezer Prout escribió en 1902 que todas las ediciones publicadas habían seguido la impresión de Walsh, y restituyó el texto de Handel: las contraltos en el compás 24, las sopranos en el 30 y los bajos en los compases 31 y 32.',
    'The tenors\' words in bars 70 and 71 were wrong in every edition, Prout found: they sang "and He shall reign for ev-er", leaving out "and ever". Handel\'s own manuscript shows he first wrote "and He shall reign for", crossed out "for" and changed the notes, ending with "and He shall reign, and He shall reign", which is what the tenors sing here.':
        'La letra de los tenores en los compases 70 y 71 estaba mal en todas las ediciones, según comprobó Prout: cantaban "and He shall reign for ev-er" y se dejaban "and ever". El manuscrito del propio Handel muestra que primero escribió "and He shall reign for", tachó "for" y cambió las notas, para terminar con "and He shall reign, and He shall reign", que es lo que cantan aquí los tenores.',
    'Handel, Messiah, edited by Ebenezer Prout (London: Novello and Company, 1902), full score, preface, p. xv, No. 44; University of Toronto, Faculty of Music copy, read from the scan':
        'Handel, Messiah, edición de Ebenezer Prout (Londres: Novello and Company, 1902), partitura completa, prefacio, p. xv, n.º 44; ejemplar de la University of Toronto, Faculty of Music, leído en el escaneo',
}


def lines(nums):
    return nums.replace(' and ', ' y ').replace(' to ', ' a ')


def es(en):
    if en in FACTS:
        return FACTS[en]
    if en == 'Hallelujah Chorus':
        return 'Hallelujah Chorus'
    m = re.fullmatch(r'Hallelujah Chorus: hear the whole song first, then the (tune|alto part|bass part|tenor part) on its own\.', en)
    if m:
        return f'Hallelujah Chorus: escucha primero la canción entera y luego {PARTS[m.group(1)]} sola.'
    m = re.fullmatch(r'Record the (tune|alto part|bass part|tenor part) of Hallelujah Chorus in Sing, with the other parts playing\.', en)
    if m:
        return f'Graba {REC[m.group(1)]} de Hallelujah Chorus en Cantar, con las demás voces sonando.'
    m = re.fullmatch(r'Lines ([\d, ]+(?: and | to )\d+)', en)
    if m:
        return 'Frases ' + lines(m.group(1))
    m = re.fullmatch(r'Hear line (\d+), then sing it back\.', en)
    if m:
        return f'Escucha la frase {m.group(1)} y repítela.'
    m = re.fullmatch(r'Now lines ([\d, ]+(?: and | to )\d+) joined: hear them, then sing them back\.', en)
    if m:
        return f'Ahora las frases {lines(m.group(1))} seguidas: escúchalas y repítelas.'
    m = re.fullmatch(r'Now lines ([\d, ]+(?: and | to )\d+) joined, with the guide\.', en)
    if m:
        return f'Ahora las frases {lines(m.group(1))} seguidas, con la guía.'
    m = re.fullmatch(r'Now lines ([\d, ]+ and \d+) in their places, the other parts singing the lines between, with the guide\.', en)
    if m:
        return f'Ahora las frases {lines(m.group(1))} en su lugar, con la guía; las demás voces cantan las frases intermedias.'
    m = re.fullmatch(r'Line (\d+) is the tune of line (\d+) again, with new words\. Sing it with the guide\.', en)
    if m:
        return f'La frase {m.group(1)} repite la melodía de la frase {m.group(2)}, con otra letra. Cántala con la guía.'
    m = re.fullmatch(r'Line (\d+) is line (\d+) again\. Sing it with the guide\.', en)
    if m:
        return f'La frase {m.group(1)} repite la frase {m.group(2)}. Cántala con la guía.'
    m = re.fullmatch(r'(.+) start to end, with the guide\.', en)
    if m and m.group(1) in SECTIONS:
        return f'{SECTIONS[m.group(1)]}, de principio a fin, con la guía.'
    return None


missing = json.load(open(sys.argv[1], encoding='utf-8'))
out, left = {}, []
for item in missing:
    t = es(item['en'])
    if t is None:
        left.append(item['en'])
    else:
        out[item['en']] = t
json.dump(out, open(sys.argv[2], 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(len(out), 'translated;', len(left), 'left')
for x in left:
    print('LEFT:', x)
