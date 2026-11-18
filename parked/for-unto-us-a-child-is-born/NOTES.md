# For Unto Us a Child Is Born: research notes

Template: templates/library/for-unto-us-a-child-is-born.json, built by build/build.py from build/notes.txt (the bar-by-bar
reading, printed pitches in G) and build/meta.json. Rebuild: `python3 -I parked/for-unto-us-a-child-is-born/build/build.py`.
Reading aids in build/: crop.py (crops in a 1400-tall frame), scanlib.py, heads.py (finds filled noteheads and names their
pitch from the staff lines, after straightening the scan's tilt), measure.py (the pitch at given x positions), parse.py,
analyse.py (range excursions by key, long lines). Scans and crops are kept outside the repo in
~/Code/arranger-keep/new/for-unto-us-a-child-is-born-scans/ (fs-NNN.jpg full score leaves, vs-NN.jpg vocal score leaves,
fsv/ the voice-staff crops).

## For the other Messiah arrangers (archive ids)

- **messiahsacredora00hand_0** (archive.org): Prout's FULL SCORE, Novello 1902, University of Toronto, Faculty of Music
  copy. Title page n6: "edited, and the additional accompaniments largely re-written, by Ebenezer Prout. Full score.
  Ent. Sta. Hall. Price 31/6. London: Novello and Company, Limited and Novello, Ewer and Co., New York. Copyright, 1902,
  by Novello and Company, Limited." The New York imprint is Novello, Ewer and Co., so this printing is from before the
  H. W. Gray Co. became Novello's New York agent. Plate 11570. Preface pp. i to xiv (n8 onwards; p. iv is n9, p. v n10,
  p. vi n11). No. 12 is pp. 93 to 113 (n118 to n138; BookReader n = page + 25 here). **The source of the template.**
- messiah0000gfha_z0r4: Prout's VOCAL SCORE (Novello's Original Octavo Edition, "Copyright, 1902"), an H. W. Gray Co.,
  159 East 48th Street, New York, printing, undated (that address is later than the 1902 first printing; not used for the
  rights). No. 12 is pp. 47 to 56 (n58 to n67; n = page + 11). Used only to read bars 7 to 32 more easily; every bar was
  then checked against the full score.
- bwb_KU-103-937, bwb_KU-103-948, bwb_KU-103-949: the same vocal score in 1960s reprints (Mills Music agent, Boosey and
  Hawkes Bonn, library stamps of 1968). Not usable as a pre-1931 printing.
- The Schirmer 1912 vocal score (messiahoratoriof00hand_0 and others) names T. Tertius Noble (died 1953): fails the bar.
- IMSLP also lists Prout's vocal score from the Sibley Library (Novello, plate 8332) and Chrysander's Handel Society full
  score (1902); not used.

## The chorus as printed

- No. 12, Chorus, "For unto us a Child is born", G major, common time, "Andante allegro", crotchet = 76 (Prout's mark,
  read on both scores). 105 bars: the strings' introduction is bars 1 to 6, the voices sing bars 7 to 91, the orchestra
  ends alone from bar 92 (p. 113, second half, and p. 114).
- Entries: soprano bar 7, tenor bar 12, alto bar 18 (answer in D), bass bar 19 (in D). "Wonderful, Counsellor" blocks at
  bars 33 (D), 49 (G), 68 (C) and 85 (G). "con Rip." over the strings at each "Wonderful" (seen on p. 99, bar 33).
- The voices are in treble, treble, tenor C clef and bass clef in the full score; treble, treble, treble (tenor) and bass
  in the vocal score.

## People

- **George Frideric Handel**, music: born Halle 1685, died London 14 April 1759 (his death year is beyond doubt; IMSLP and
  every library record agree). Nationality left out (German-born, a British subject from 1727).
- **Charles Jennens**, compiled the words of Messiah from the Bible: died 1773 (archive.org's Library of Congress-style
  name heading on the Schirmer 1912 score reads "Jennens, Charles, 1700-1773"; a lead, not read from a page of his).
  The words here are Isaiah 9:6 in the King James Version.
- **Ebenezer Prout**, editor: 1835 to 1909 (IMSLP's editor heading "Prout, Ebenezer 1835-1909"; a lead for the story,
  confirm in a printed obituary if the story uses the date). His preface is signed in London; he wrote it for the full score.

Every maker died in 1925 or earlier: the rights bar is met (Prout 1909 is the latest).

## For the courses lead's story (read on the scans)

- Prout's preface, p. v (n10): "The employment of only a few desks of the strings, in contrast to the whole force, was a
  frequent device of Handel's; he indicates it by the words senza Ripieni and con Ripieni. The so-called 'Dublin score'
  ... contains full indications, in the composer's writing ... The senza Rip. are mostly found in the songs, but sometimes
  in the choruses also, e.g., in 'For unto us,' the greater part of which is accompanied by the strings senza Ripieni".
- p. vi (n11): "In 'For unto us,' a great part of which Handel scored in this way, I have preferred to fill up the
  accompaniments on the wind, and to reserve the organ for the great bursts at 'Wonderful! Counsellor!' and for the latter
  part of the chorus. An examination of the score will show that I have introduced the organ exactly where Handel marks
  'con Ripieni' for the strings."
- p. iv (n9): "Mozart (or possibly Hiller) has given a large part of the choruses 'And He shall purify,' 'For unto us,'
  and 'His yoke is easy' to solo voices, because in this country these movements are invariably sung as Handel intended."
  The same page: Mozart's score is "after", not "in", Mozart's arrangement; much of it is Hiller's.
- Preface (OCR of p. ii, not yet read on the image): a footnote says Schoelcher dated the first complete edition of
  Messiah 1768, "but it appeared in the year 1767". IMSLP lists a Randall & Abell full score, London, n.d. [1767]: the
  earliest known printing of the choruses, a lead.
- Preface, the notes on No. 12 (OCR of p. xi or so, leaf n14, not yet read on the image): Prout added flutes, clarinets,
  trombones and organ to Mozart's orchestra for this chorus, and some drum notes in its last part.
- Widely said (not read here): the chorus reworks Handel's Italian duet "No, di voi non vo' fidarmi" (HWV 189, 1741);
  Prout's preface names an Italian duet only for another chorus. Leave it out unless a scan of Chrysander's edition is read.
- Isaiah 9:6 (KJV): Prout prints "Child", "Son", "His", "Name" and "The Mighty God, The Everlasting Father, The Prince of
  Peace" with capitals; the template keeps them.
