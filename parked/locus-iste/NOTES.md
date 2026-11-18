# Locus iste (Bruckner): research and build notes

Template: templates/library/locus-iste.json, built by parked/locus-iste/build/build.py from build/score.txt (the four
parts as read from the scan, one line per printed system) and build/meta.json (the song's fields and chords). Rebuild
with `python3 -I parked/locus-iste/build/build.py` from the worktree's root; the breaths are its BREATHS list. Scans
and crops are kept out of the repo, in ~/Code/arranger-keep/new/locus-iste-scans/ (p01 to p04 at the IIIF server's
full size, 1067 px wide, the largest it serves; crops in sc/). Reading tools in build/: sc.sh (zoomed crops), dump.py
(an ASCII map of a region, to place a head against the staff lines), probe.py and staves.py (staff lines and filled
heads; rough), chords.py (a first draft of the chord names, then curated by hand in meta.json).

## The source (read from the page images)

**Anton Bruckner, Vier Graduale für Sopran, Alt, Tenor u. Bass** (title page, scan WAB023-01): "Heft I. No. 1
'Christus factus est', No. 2 'Locus iste' ... Heft II. No. 3 'Os justi', No. 4 'Virga Jesse'"; prices "Partit. 60 Kr.
/ Mk 1", "Stimm. 75 Kr. / Mk 1.30 Pf", "Einzelne Stimmen Pr. à 20 Kr. / 35 Pf"; "Eigenthum des Verlegers für alle
Länder / Den internationalen Verträgen gemäss deponirt / Verlag v. TH. RÄTTIG. Wien / I. Bellariastrasse 10 /
Leipzig R. Forberg"; "Musikaliendruckerei v. Jos. Eberle & Co. Wien VII". Undated. Library stamp "M.S. 5216" and
the watermark "Österreichische Nationalbibliothek, Digitale Services": the Austrian National Library's copy.
- pp. 8 to 10 (scans WAB023-02 to -04): "2. GRADUALE. Locus iste.", "Anton Bruckner.", "Allegro moderato.", four
  staves (Sopran, Alt, Tenor, Bass), the tenor in the treble clef (sounding an octave lower), C major, common time
  (C), 48 bars, plate "T.R. 41" at the foot of each page. No editor, arranger or translator is named anywhere.
- Where it was found: Bruckner Online (Austrian Academy of Sciences, ACDH), first prints ("Erstdrucke"), WAB 23,
  "First Print: Theodor Rättig, Wien 1886": viewer www.bruckner-online.at/erstdrucke?wabId=WAB023, IIIF manifest
  iiifpresentation.acdh.oeaw.ac.at/bruckner/drucke/WAB023/manifest, images
  iiif.acdh.oeaw.ac.at/iiif/images/bruckner/drucke/WAB023/WAB023-01.jp2 to -04.jp2 (/full/full/0/default.jpg).
  IMSLP lists the same print as its #437277 ("First edition", Rättig, engraved by Eberle, plate T.R. 41, n.d.
  [1886]); its download page is behind a bot check, so the ACDH scan was used (the same ÖNB copy, by the watermark).
- The year 1886 is the catalogues' (Bruckner Online's "Theodor Rättig, Wien 1886"; IMSLP "n.d. [1886]"): the print
  itself is undated. firstPublished is 1886, AT, as the earliest known printing.

## Makers and the rights bar

- Anton Bruckner (music and his own four parts): born Ansfelden 4 September 1824, died Vienna 11 October 1896
  (Neue Deutsche Biographie and every reference). AT.
- Words: the Latin gradual of the Mass for the dedication of a church (Commune dedicationis ecclesiae), anonymous
  liturgy: no maker.
- The edition names no editor; Theodor Rättig was the publisher (not an editor or arranger), and Jos. Eberle & Co.
  the music printer. Nobody else's work is used.
- Every maker died in 1925 or earlier: the bar is met. Doubt: none on the notes; the date 1886 is the catalogues'.

## What we sing, and what changed

All 48 bars, every part, every pitch and rhythm as printed (the whole motet is 3 minutes 11 seconds at 60), in C as
printed (C has the fewest notes outside the beginner ranges of any key: 18; B-flat 19, B 23, D-flat 30). The tenor is
written at its sounding pitch. Ties and same-pitch slurs (the "fac-" of bars 46 and 47 in the soprano, tenor and bass)
are one held note. Dynamics, hairpins and cresc. are not carried (the app has no dynamics); the tempo word
"Allegro moderato" is sung at 60 to a crotchet (no metronome mark is printed; see DECISION.md).

Breaths written in (singable rule 1; each takes half a beat from the note before a new line, which keeps at least
half a beat), listed in build.py:
- soprano, alto, tenor: before "sa-" in bars 15 and 19 (the slurred last note of "le" gives up half a beat);
- soprano and alto: before the mf "pre-" of bar 27; soprano, alto and tenor: before "est" in bar 29;
- bass, which sings bars 1 to 4 and 5 to 20 with no printed rest: before "a" in bars 2, 6, 31 and 35; at the printed
  comma "est, a" in bars 8 and 37; before the second "De-o" (bars 10 and 39); before "fac-tus" in bar 11; before
  "in-æ-sti-" in bars 12 and 16 (the second at the printed comma "tum,"); before "sa-" and "men-" of each
  "sa-cra-men-tum" (bars 14, 15, 18, 19);
- everyone: at bar 41, inside the twelve-beat melisma on "De-", singing the vowel again as "(e)-" (the alto's tied
  B-flat and the tenor's and bass's notes re-struck on the bar line); before "fac-" (bar 46) and before "est." (bar 48).
No line is over 8 seconds at 60.

Review (2026-11-18): an independent read of every bar against the scan found one misreading, now fixed: the tenor's
"ir-re-pre-hen-" in bar 21 is C4 (written C5, in the space under the D line), not D4. Nothing else differed.

## Facts for the story (read on the scan unless marked "lead")

- The print's own facts: the title page above (four graduals in two books, the prices); "2. Graduale"; "Allegro
  moderato"; pp (bars 21 to 25), cresc. (bar 25), p and mf (bars 26 and 27) in the middle; mf on the second "locus
  iste" (bar 5) and f on "a Deo" (bar 7), ff on the second "inaestimabile" (bar 16); the basses rest for nine bars
  (21 to 29) while the tenors begin "irreprehensibilis est" alone, pp, and the upper voices answer; the "De-o" of bars
  40 to 42 is the only long melisma, under one slur from cresc. to f; bar 43 is a whole bar's rest in every part; it
  ends pp, "est." on a dotted minim.
- Leads (not seen on a scan; from IMSLP's work page and the Wikipedia article's sources): composed 11 August 1869
  (Cornelis van Zwol, Anton Bruckner: Leven en Werken, 2012); written for the dedication of the votive chapel
  (Votivkapelle) of the New Cathedral in Linz, the first part of the cathedral finished (Cambridge Companion to
  Bruckner, 2004); first performed there on 29 October 1869 (van Zwol; Iso Camartin, Neue Zürcher Zeitung, 2005),
  though some say 29 September 1869, with the Mass in E minor (Stephen Johnson, Hyperion notes); dedicated to Oddo
  Loidol, a student at the Vienna Conservatory (Peter Strasser, 2008); Bruckner's first motet written in Vienna
  (Heather Garbes, 2007). Manuscripts at IMSLP: a copyist's score (Franz Schimatschek) with Bruckner's corrections,
  ÖNB Mus.Hs.28268 (by 1877); a copy in the Diözesanarchiv Linz; the engraver's copy for the 1886 print, ÖNB
  Mus.Hs.37283. A later printing: Robert Lienau, Berlin (took over Rättig's catalogue; IMSLP dates its Os justi about
  1911, plate 9613; Locus iste's place in it not checked). Earliest recording: Karl Luze and the choir of the Vienna
  Court Chapel (Hofmusikkapelle), a 78 about 1907 (Wikipedia, not checked). Max Auer (1927) heard Mozart's Ave verum
  in its opening (lead).
- The text: the gradual "Locus iste a Deo factus est, inaestimabile sacramentum, irreprehensibilis est" ("This place
  was made by God, a priceless sacrament; it is without fault"); its verse ("Deus, cui adstat angelorum chorus ...")
  is not set by Bruckner (lead: the Roman Missal's common of the dedication of a church; not checked on a scan).
  Programme notes tie it to Jacob's words at Bethel, Genesis 28:16 to 17 (lead).

## Choices

- For 4 singers only, like Ave verum, The Lord Bless You and Deep River: the parts take turns (the tenor alone in bar
  21, the basses silent for nine bars, the bass leading each "a Deo" in the outer sections), so 2 or 3 singers would
  leave whole bars empty or the chords without their bass.
- Intermediate: the soprano runs B3 to G5 and the bass F2 to C4 (Bruckner's), and the middle is chromatic.
- Words as printed under each part: "æ" in "inaestimabile" kept, capitals as printed ("Lo-cus" at the starts of
  bars 1 and 30, "lo-cus" in bars 5 and 34), commas only where that part's staff prints one ("est," bar 8 soprano and
  bass; "tum," bars 16 and 20 bass; "est," bar 26 tenor), "est." at the end.
