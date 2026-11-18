# Cantique de Jean Racine: research notes

Template: templates/library/cantique-de-jean-racine.json, built by parked/cantique-de-jean-racine/build/build.py from
build/transcription.txt (the four voice parts as read, bar by bar, sounding pitch), build/breaths.py (where each part
breathes and how) and build/meta.json. Rebuild: `python3 -I parked/cantique-de-jean-racine/build/build.py`. The
reading tools (crop.sh, hz.sh, look.py, heads.py, heads2.py, notes.py, probe.py, staffzoom.py, strips.py,
voicecrops.py, img2pgm.swift, ppm2png.swift) are in build/; the scan and its crops are kept out of the repo, in
~/Code/arranger-keep/new/cantique-de-jean-racine-scans/bnf.

## The printing read (the source of the template)

**Écho des Maîtrises**, "Collection nouvelle de chants religieux inédits des plus célèbres compositeurs modernes,
publiée sous la direction de M. R. Bussine, Professeur au Conservatoire", "À Sa Sainteté Pie IX", première livraison
(Paris: F. Schoen, éditeur de musique, 42 boulevard Malesherbes; undated). Plate F. 309 S. on every music page
(read at 8x; IMSLP's listing of a Schoen copy, #407799, gives "F. 39 S." and dates it "n.d. [1876?]").
- Cover: the issue's ten pieces: 1 O Salutaris (Saint-Saëns, organist of the Madeleine), 2 Pie Jesu (Ch. Magner),
  3 Veni Creator (César Franck, organist of Sainte-Clotilde, professor of organ at the Conservatoire), 4 Benedictus
  (Th. Dubois), 5 Ave Maria (Gustave Lefèvre), 6 O Salutaris (D. Magnus), 7 Ecce panis (J. Koszul), 8 Pater noster
  (J. Cressonnois), 9 Ave Verum (Charles Lefebvre), "No 10. Cantique de Jean Racine. Chœur à quatre voix. G. FAURÉ,
  Organiste de la Maîtrise de l'Église Saint-Sulpice", 2 francs; "Les parties séparées des chœurs, chaque: 20
  centimes". Schoen's stamp (Musique & Pianos, 42 boul. Malesherbes).
- p. 2 (first music page): "A Monsieur CÉSAR FRANCK. / Cantique de Jean Racine / CHŒUR / Gabriel FAURÉ / Organiste
  de la Maîtrise de St Sulpice". Staves: Sopranos, Contraltos, Ténors (treble clef), Basses; "Orgue ou Piano".
  D-flat major, common time, Andante (no metronome mark); the organ alone for 12 bars ("Cantabile", "legato").
- pp. 3 to 9: the choir from bar 13 (the basses, pp, "Ver-be é-gal au Très-Haut") to the end (bar 89, "Poco rall.",
  a fermata over two tied whole notes). The choir rests from bar 31, beat 3 (after "yeux!") to bar 39, beat 4 ("Ré-"):
  bars 32 to 35 are the organ alone, 36 to 38 the organ with the choir silent ("Dolce" at the re-entry). Engraver's
  footer on p. 9: "Imp. Michelet 6 r. du Hasard". The back page: Schoen's catalogue, printed by J. Claye, A. Quantin et
  Cie (a dating hint, not checked).
- Copy: Bibliothèque nationale de France, Musique, Vmg. 17107 (I,10), "Dépôt de la Société des Concerts du
  Conservatoire" (Gallica's footer on every page). The scan was read from the Gallica PDF (14 images, 1024 px wide).
  gallica.bnf.fr and imslp.org both refuse automated downloads from here; the PDF came from a public folder linked in
  the description of archive.org item faure-gabriel-cantique-de-jean-racine-choeur-seul-dvg_202412 (a modern 2024
  typeset "chœur seul" edition, Collection "A voce plena", DVG). That modern edition was NOT used: only its first page
  was opened, to see what it was. Every note was read from the BnF scan.
- Worth a human check: open Gallica's or IMSLP's own copy (#407799) once and compare two or three pages with
  build/transcription.txt, since the PDF came through a third-party folder (it carries the BnF shelfmark, stamps and
  Gallica footers throughout, so it looks untouched).

## How the notes were read

The scan is low resolution (a staff space is about 4.8 px). Each bar was read from enlarged strips, filled heads
measured by build/heads2.py against the staff lines where they stand (the pages are skewed), and every open head
(halves, wholes) checked by eye at 8x or in build/look.py's character pictures, with the lines marked. A harmony scan
(build/sanity.py) then listed every sonority no chord explains; each was rechecked on the scan (one misreading found
and fixed: the bass in bar 41 is C3 throughout, not A-flat 3). What is left are Fauré's own appoggiatura chords: a
dominant seventh over a tonic pedal at bars 23 ("si-len-ce", C7 over F), 43 (F7 over B-flat) and 47 (B-flat 7 over
E-flat), the tenor's D-flat over C major in bar 50, and the suspensions in bars 70 and 82.

Words: every syllable read under its notes. The bass prints "Re-pands" (bar 39) where the other three print "Ré-":
sung here as "Ré-". "Très-Haut" is written "Très--" + "Haut," so the song page shows the hyphen. Elisions as Fauré
sets them share a note ("Ver-be é-gal": "be é-"; "No-tre u-ni-que es-pé-": "tre u-", "que es-"; "ter-re et", "gloi-re
im-", "fa-vo-ra-ble à", "of-fre à").

## People and dates

- **Gabriel Fauré**, music: born 12 May 1845, Pamiers; died 4 November 1924, Paris (Library of Congress name
  authority n81018450, citing New Grove, 2nd ed.: "d. Nov. 4, 1924, Paris"). The first printing calls him "Organiste de
  la Maîtrise de St Sulpice".
- **Jean Racine**, words: 1639 to 1699 (Mesnard's edition, below). The hymn is his French version of the Latin
  "Consors paterni luminis", "Le mardi, à matines" (Tuesday, at Matins), among his Hymnes traduites du Bréviaire romain.
- **Romain Bussine**, director of the series (the edition): born 4 November 1830, Paris; died 21 October 1899, Paris
  (French Wikipedia, citing his death record, Paris 9e, No. 1381). Singing teacher at the Conservatoire from 1872;
  co-founder with Saint-Saëns of the Société nationale de musique (1871) (same article, unsourced there).
- **César Franck**, the dedicatee (not a maker of what we sing).
- Every maker of what we use died by 1925: Racine 1699, Bussine 1899, Fauré 1924. No other editor or arranger is named.

## The words' history (for the story)

Œuvres de J. Racine, ed. Paul Mesnard (Les Grands Écrivains de la France), vol. 4 (Paris: Hachette, 1865),
archive.org/details/oeuvres04raci (University of Toronto copy):
- n125 (p. 112): "LE MARDI. A MATINES." The French in four-line verses, as the Bréviaire romain prints it: "Verbe égal
  au Très-Haut, notre unique espérance, / Jour éternel de la terre et des cieux, / De la paisible nuit nous rompons le
  silence: / Divin Sauveur, jette sur nous les yeux. // Répands sur nous le feu de ta grâce invincible; / Que tout
  l'enfer fuie au son de ta voix; / Dissipe ce sommeil qui rend l'âme insensible, / Et la conduit dans l'oubli de tes
  lois." The Latin below: "AD MATUTINUM. Consors paterni luminis, / Lux ipse lucis et dies, / Noctem canendo rumpimus:
  / Assiste postulantibus." Note 1: the hymn is in the Bréviaire romain, winter part p. 110, summer p. 101, autumn p.
  104; a manuscript in the British Museum. Note 2: Corneille translated "Lux ipse lucis et dies" more literally, "Jour
  du jour, clarté des clartés". Note 3: Louis Racine's edition reads the strophe "Répands sur nous le feu de ta grâce
  puissante; ..."
- n126 (p. 113): "O Christ, sois favorable à ce peuple fidèle, / Pour te bénir maintenant assemblé; / Reçois les chants
  qu'il offre à ta gloire immortelle; / Et de tes dons qu'il retourne comblé." (Fauré: "rassemblé".) Note 3 goes on:
  "Que tout l'enfer fuie au son de ta voix; / Dissipe ce sommeil d'une âme languissante, / Qui la conduit dans l'oubli de
  tes lois." Mesnard does not believe this variant is Racine's ("que nous ne croyons pas de Racine"), and asks what to
  think, then, of the British Museum manuscript, "prétendu autographe", which follows Louis Racine's reading.
- n105 (p. 92): the notice: the eighteen hymns attributed to Racine appear in le Tourneux's Bréviaire, mixed with others;
  Louis Racine's attribution is not proven; "la seconde strophe de l'hymne du mardi à Matines" carries "cette
  importante variante", which Mesnard thinks is the son's correction.
- So Fauré set Louis Racine's text (puissante, languissante), with "le sommeil" for "ce sommeil", "à l'oubli" for "dans
  l'oubli" and "rassemblé" for "assemblé": which printing of Racine he took it from is not known here (a lead).

## Origins as the sources state them

- The 1876 date is IMSLP's "[1876?]" for the Schoen printing; the printing read here is undated. firstPublished 1876
  (FR), "earliest known printing": the Schoen Écho des Maîtrises issue.
- Composition in 1864 or 1865 at the École Niedermeyer (a first prize, as commonly said) is NOT checked on a source
  here; two archive.org concert notes give "Cantique de Racine (1864)" (LP sleeve text, not a source). A lead for the
  story: Grove's or Koechlin's Fauré (1927).
- Grove Music (per IMSLP's page): first with organ; a version with harmonium and string quintet 1866; orchestrated 1906.
  Not checked here.

## Choices (the decision text is in DECISION.md)

- The whole choral piece, bars 13 to 89, in the printed key (D-flat), tempo 60, the organ left out: its 12-bar
  introduction (the song starts on the bass's entry), its bars 32 to 38 (the choir's 8-bar rest becomes 5 beats), and
  the final two tied bars under a fermata become a 3-beat chord (the song ends a pickup short of a bar line).
- 4 singers only, like Ave verum: Fauré's parts enter one by one and cross; no 2- or 3-singer voicing would keep them.
- Breaths written in at Racine's commas and where a choir breathes, never inside a word (build/breaths.py).
