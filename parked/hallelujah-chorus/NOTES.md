# Hallelujah Chorus: research notes

Template: templates/library/hallelujah-chorus.json, built by build/build.py from build/trans.txt (the four voice parts as
printed, score bar numbers, printed key) and build/meta.json. Rebuild: `python3 -I parked/hallelujah-chorus/build/build.py`
(it writes the template; every change from the print is a line in its SHORTEN, REPITCH and DELAY lists). Scans and crops
are kept out of the repo, in ~/Code/arranger-keep/new/hallelujah-chorus-scans/ (fetch again from the URLs below).

## Printings seen (read from the page images)

1. **Prout's full score, 1902 (the source).** Messiah, a Sacred Oratorio, composed in the year 1741 by G. F. Handel,
   "edited, and the additional accompaniments largely re-written, by Ebenezer Prout" (London: Novello and Company,
   Limited, and Novello, Ewer and Co., New York; "Copyright, 1902, by Novello and Company, Limited"; "Price 31/6";
   plate 11570; "Novello & Company, Ltd: Engravers & Printers"). University of Toronto, Faculty of Music copy:
   archive.org/details/messiahsacredora00hand_0.
   - n285 to n303 (pp. 260 to 278): No. 44, Chorus, Hallelujah, "Allegro. crotchet = 72", D major, common time; the
     voices on four staves under the strings (soprano and alto in treble clef, tenor in tenor clef, bass in bass clef).
   - Preface signed at its end "Ebenezer Prout. London, April, 1902". p. xv (n20) on No. 44:
     - "In this chorus Handel several times writes the last syllable of the word 'Hallelujah,' and the first syllable of
       the same word repeated, to one note. The first instance of this is in the alto of bar 24 ... All published
       editions of the oratorio give Walsh's reading ... I have restored Handel's text here, and in the similar passages
       (soprano, bar 30; bass, bars 31 and 32)." (Our template keeps it: "jah, Hal-" on one note.)
     - "At bars 70 and 71 every edition, whether of the full or vocal score, has the words wrong in the tenor. All
       read [and He shall reign for ev - - er] which, it will be seen, omits the final words 'and ever.' An examination
       of the autograph shows that Handel at first wrote [and He shall reign for]. He did not complete the sentence, but
       erased the word 'for' and altered the notes in bar 71; his final version is [and He shall reign, and He . . shall
       reign] which I have of course adopted in the text." (Our tenor sings this.)
     - "there is no authority in the autograph for the traditional piano (bar 33) at the words 'The kingdom of this
       world.' I have not felt justified in omitting it, but have put it in brackets." (Printed "(p)" in both scores.)
     - "Throughout this number Mozart has treated Handel's trumpet parts in the most arbitrary manner ... I have felt it
       to be an obvious duty to restore the original parts as far as possible", with a few high passages eased (bars 20,
       55, 56, 79 and 86); "I have also added trombones and a fully written out organ part."
   - p. iv/v (n10 area): Mozart's additional accompaniments; Prout restores Handel's own chord in "The kingdom of our
     Lord, and of his Christ" ("Wherever Handel and Mozart come into collision, the latter must give way").
   - Printing date: the New York imprint is Novello, Ewer and Co. (Novello's later New York agents were the H. W. Gray
     Co.), and the library catalogues it 1902. No printing date on the leaf beyond the copyright line.
2. **Prout's vocal score (checked against; a later printing).** Novello's Original Octavo Edition, The Messiah,
   "edited, and the pianoforte accompaniment largely re-written, by Ebenezer Prout"; "Copyright, 1902, by Novello and
   Company, Limited"; New York: The H. W. Gray Co., sole agents; price "Two Shillings and Sixpence" (corrected by hand
   from "Two Shillings"); Coventry University copy, archive.org/details/bwb_KT-315-920. No. 44 on pp. 149 to 157 (n162
   to n170), "Allegro. crotchet = 72", tenor in treble clef; voice parts identical to the full score in every bar
   compared (all of them; see DECISION.md). Its preface (n11, p. v) repeats the note on alto bar 24 ("treble, bar 30").
   The printing is undated, so it is used only as a reading aid; the rights rest on the 1902 full score.

- **Does the edition change Handel's notes?** In the voices, no reharmonisation: Prout's preface says he restored Handel's own text from the autograph where all earlier editions followed Walsh, and "in no single instance have I arbitrarily added anything of my own"; his rewriting is of Mozart's additional accompaniments (the orchestra, not sung here). His only mark added to a voice part is a small optional lower D under the alto's top D at bars 46 and 79.

## People

- **George Frideric Handel**, music. Died 1759 (Prout's title page names him; death year standard; not read here).
  Born in Halle, naturalised British: nationality left out of makers.
- **Charles Jennens**, words. Dictionary of National Biography (1885 to 1900), "Jennens, Charles", by Gordon Goodwin:
  "born in 1700, was only surviving son of Charles Jennens of Gopsall, Leicestershire"; "He also wrote the words for
  Handel's 'Saul' (1735), 'Messiah' (1742)"; "died unmarried on 20 Nov. 1773", buried at Nether Whitacre (read on
  Wikisource, en.wikisource.org/wiki/Dictionary_of_National_Biography,_1885-1900/Jennens,_Charles).
- **Ebenezer Prout**, editor. Dictionary of National Biography, 1912 supplement, "Prout, Ebenezer", by Henry Davey:
  born at Oundle, Northamptonshire, 1 March 1835; "He died suddenly at his house in Hackney on 5 Dec. 1909, and was
  buried at Abney Park cemetery"; "A modernised edition of Handel's 'Messiah' (1902) had little success" (Wikisource).
- **Walsh** (John Walsh, the London publisher), named by Prout as the source of the "published editions'" underlay.
- **Mozart**: his additional accompaniments, which Prout rewrote; nothing of them is sung here.

Every maker of what we sing died by 1925 (Handel 1759, Jennens 1773, Prout 1909): the rights bar is met. The words are
the King James Version as Jennens set them; the KJV's UK Crown letters patent is the same open question as for The Lord
Bless You.

## The chorus as printed (score bars)

- Bars 1 to 3: orchestra alone (left out). Choir from bar 4 to the end, bar 94; the choir is never silent for more than
  three beats (bar 33, before "The kingdom", kept) and the two beats' rest before the last "Hallelujah" (bar 92, kept).
- Sections: Hallelujah (4 to 11); "For the Lord God Omnipotent reigneth" in unison (12 to 14), then as a long-note tune
  against Hallelujahs in the sopranos (22 to 24), altos (17 to 19 with tenors and basses), tenors and basses (25 to 27),
  altos and tenors (29 to 31); "The kingdom of this world" (33 to 35, piano in brackets); "is become the Kingdom of our
  Lord, and of His Christ" (36 to 41); "And He shall reign for ever and ever", entering bass (41), tenor (43), alto (46),
  soprano (48): Prout's alto has a small lower D under its top D at bars 46 and 79 (an option; we sing the large note);
  "King of Kings, and Lord of Lords" with the sopranos' held notes rising A, D, E, F-sharp, G (51 to 68, printed key);
  "And He shall reign" again (69 to 81); "King of Kings ... Hallelujah" to the end (82 to 94). No Adagio is printed for
  the last bars in either score.
- Soprano range as printed D4 to A5 (A5 once, bar 49, "He"); bass up to D4 often (114 notes above B-flat 3).

## Review (2026-11-18)

A reviewer who did not build it compared the transcription with both scans: one misreading fixed (tenor and bass, bar 17, "for the Lord" D, E, F-sharp), the bass's "ever" in bar 44 without a comma, two breaths moved (tenor bar 29, bass bar 68). DECISION.md has the details.

## Choices (and why)

- Whole chorus, voices only. 364 beats at 60: about 6 minutes, the longest song in the library (the longest open song
  was 212 s, Were You There); the app's take limit is 600 s and the format sets no length.
- Key B-flat (printed D): down a major third, the transposition with the fewest seconds out of the beginner ranges
  (17.5 s against 97.5 s in D, where the bass is out for 60 s). Remaining excursions are listed in DECISION.md.
- Tempo 60 (Prout prints crotchet = 72): the fastest at which Handel's quaver rests count as a breath (half a second)
  and his semiquaver "Hal-le" stays a quarter second (singable rules 1 to 3). At 72 every Hallelujah line runs on.
- For 4 singers only, like Ave verum corpus: fugal entries and a tune that moves between the parts.

## Leads for the story (not checked here)

- Messiah's first performance (Dublin, 1742) and Jennens's role in choosing the scripture: DNB gives only "wrote the
  words".
- The custom of standing for the chorus (no source read).
- Walsh's early printings (the published underlay Prout corrects).
