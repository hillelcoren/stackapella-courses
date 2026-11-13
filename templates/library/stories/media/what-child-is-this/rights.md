# What Child Is This?: image rights evidence

Three images. Final files made with sips only (BMP round trip, metadata stripped), long side 1600 px:
1.jpg 557 KB (q68), 2.jpg 461 KB (q82), 3.jpg 477 KB (q76); together about 1.5 MB. Originals in raw/, saved
record pages in pages/.

2.jpg and 3.jpg are Internet Archive scans of flat printed pages with no licence field in the record, so each rests
on public domain by age, with the reasoning below. A faithful scan of a flat page adds no new copyright: in the US
under Bridgeman v. Corel, and in the EU under Art. 14 of the 2019 DSM Directive and for lack of originality; Israel
likewise requires originality.

## 1.jpg: Magdalen College, from the river, Oxford (photochrom, between about 1890 and 1900)

- Holder's record: https://www.loc.gov/item/2002708028/ . loc.gov answers plain fetches with a Cloudflare challenge
  (403), so I read it in the Wayback Machine:
  http://web.archive.org/web/20251206170258/https://www.loc.gov/item/2002708028/ , saved as
  pages/loc-2002708028-wayback-20251206.html. Fields: Title "[Magdalen College, from the river, Oxford, England]";
  Created / Published "[between ca. 1890 and ca. 1900]."; Medium "1 photomechanical print : photochrom, color.";
  Call Number/Physical Location "LOT 13415, no. 780 [item] [P&P]"; Source Collection "Views of the British Isles";
  Notes "Title from the Detroit Publishing Co., Catalogue J foreign section, Detroit, Mich. : Detroit Publishing
  Company, 1905." and "Print no. \"10083\"."; Digital Id "ppmsc 08767"; Reproduction Number "LC-DIG-ppmsc-08767
  (digital file from original)"; **Rights Advisory "No known restrictions on publication."**
- File: the Library's own 1024 px copy, https://tile.loc.gov/storage-services/service/pnp/ppmsc/08700/08767v.jpg ,
  saved as raw/loc-ppmsc-08767v.jpg (1024 x 761). For more pixels I used Wikimedia Commons' rendering of LoC's master
  TIFF, File:Magdalen_College,_from_the_river,_Oxford,_England-LCCN2002708028.tif (3639 x 2706; Commons licence
  "Public domain", credit "Library of Congress", catalogue http://lccn.loc.gov/2002708028), 1920 px rendering saved as
  raw/commons-loc-2002708028-river.jpg. Same print as the LoC copy (same frame, same "10,083. OXFORD. MAGDALEN
  COLLEGE." line).
- Crop: sips -c 1305 1845 --cropOffset 35 40 on the 1920 px rendering: the white border and the printed number and
  title line removed; nothing else.
- PD by age as well: a photochrom made from a photograph, published by about 1900 (in Detroit Publishing's 1905
  catalogue), no photographer named. US: published before 1931. EU and Israel: an anonymous work, 70 years from
  publication ended by 1975. A photochrom is a photomechanical colour print from a photographic negative: a photograph
  of a place, not a drawing.
- What it shows: the college's long stone range with battlements, chimneys and pinnacled towers, ivy on the walls, a
  narrow river with trees on the left bank, a balustraded stone bridge in the distance. No people: the bridge and
  banks zoomed at full size, none visible. No drawn figures, logos or trademarks.
- Caption facts: "In 1867 Bramley was a Fellow of the college and Stainer its organist": the Musical Times advert of
  1 December 1867, p. 235 (3.jpg): "The Words edited by the Rev. H. R. Bramley, M.A Fellow and Tutor of S. Mary
  Magdalen College. The Music by J. Stainer, Mus. Doc., Organist of S. Mary Magdalen College, Oxford." Also the
  story, The book of 1867 [^bs1867][^mt1868]. "1890s": the record's date range. I do not name the river (the record
  does not).

## 2.jpg: Bramley and Stainer, Christmas Carols New and Old, first series (1870s printing), Index

- Item: "Christmas carols, new and old : [1st series]", London: Novello, Ewer, IA date [187?]. Creators "Stainer,
  John, Sir, 1840-1901" and "Bramley, Henry Ramsden, 1833-1916". Contributor University of California Libraries; call
  number srlf_ucla:LAGE-3239423. IA field "possible-copyright-status": NOT_IN_COPYRIGHT; "copyright-evidence": "no
  visible notice of copyright; exact publication date unknown." (metadata https://archive.org/metadata/christmascarolsn00staiiala ,
  saved as raw/bs1867_meta.json).
- Record: https://archive.org/details/christmascarolsn00staiiala . Leaf n51 is the "INDEX. First Series." page, the
  one the story cites (image n51): https://archive.org/details/christmascarolsn00staiiala/page/n51/mode/1up ; file
  https://archive.org/download/christmascarolsn00staiiala/page/n51.jpg (1712 x 2844), saved as raw/bs1867_n51.jpg.
- The table is printed sideways on the page. I turned it upright (sips -r 90) and cropped the blank margins (sips -c
  1440 2620 --cropOffset 80 110). The source line says so.
- PD by age: first series published November 1867 (story, [^mt1867]); this printing 1870s. Stainer died 1901,
  Bramley 1916, Dix 1898. The page is the book's own index table, set by the editors and publisher. US: published
  before 1931. EU and Israel: life plus 70; Bramley, the last of the editors, died 1916, so it ended 1986.
- What it shows: a table, no figures, ornaments, logos or watermarks. Every word read: carol titles, authors and
  composers, all Christmas texts; nothing demeaning.
- Not a repeat: the Greensleeves page uses this book's No. XIV music page (n37); God Rest Ye uses No. I (n7), The First
  Noel No. VI (n17). The index page (n51) is used nowhere else (checked the media.json of all three).
- Caption facts: row XIV "What Child is this?", "W. C. Dix", "Old English.", page 32, and no column for a harmoniser:
  read on the page. Story, What the page shows: "The first series' own index gives the words to "W. C. Dix" and the
  air as "Old English", and names no one for the harmony" [^bs1867].

## 3.jpg: The Musical Times, 1 December 1867, p. 235 (detail)

- Item: "The Musical Times 1867-12-01: Vol 13 Iss 298", Internet Archive Serials in Microfilm (collections
  pub_musical-times, sim_microfilm), ISSN 0027-4666, identifier sim_musical-times_1867-12-01_13_298. No rights field in
  the record (metadata saved as raw/mt1867_meta.json).
- Record: https://archive.org/details/sim_musical-times_1867-12-01_13_298 . page_numbers.json maps leaf 26 to printed
  page 235: https://archive.org/details/sim_musical-times_1867-12-01_13_298/page/n26/mode/1up ; file
  https://archive.org/download/sim_musical-times_1867-12-01_13_298/page/n26.jpg (2488 x 3968), saved as
  raw/mt1867_p235.jpg.
- Crop: the top of the page only (sips -c 1424 2080 --cropOffset 360 140): the running head with the date and page
  number, both columns down to the end of the carols advert. Removed: the left margin's bleed from the facing page,
  the microfilm's "XUM" label at the foot, and the lower half of the page.
- PD by age: published London, 1 December 1867. The advert is an unsigned publisher's notice by Novello, Ewer and Co.;
  the people named in the crop all worked in the 1860s (Bramley d. 1916, Stainer d. 1901, Barnby d. 1896, Dykes
  d. 1876, Ouseley d. 1889). US: published before 1931. EU and Israel: an anonymous work, 70 years from publication
  ended 1937; even counted from the named editors' deaths, life plus 70 ended by 1986.
- What it shows: type only (the black-letter heading "Christmas Carols." and drop capitals); no figures, ornaments,
  logos or watermarks. Every word in the crop read: the Dies Irae hymn advert ("Day of wrath! O day of mourning!",
  translated by W. J. Irons), the twenty-carol list, and on the right: "Drop down, ye heavens, from above" (Barnby),
  "An easy anthem for Christmas" ("Behold, I bring you glad tidings", James Vaughan), "Ten Christmas hymns for one
  penny" (Choral Cyclopaedia), "Nine antient Christmas carols" (Edmund Sedding) with three press notices, his second
  and third collections, and "For Christmas, one penny each" ("On Christmas Eve the bells were rung", "Song of the New
  Year", "Hark! the herald angels", "Glory to God in the highest"). Nothing demeaning to any people or faith.
- Caption facts: the list and "14. What Child is this? ... Old English." read on the page; the same issue's p. 232
  ("During the last month, Published by Novello, Ewer & Co. ... Stainer, Dr. John, and the Rev. H. Bramley.
  Twenty Christmas Carols, Old and New. Price 1s. 6d. See page 235", checked in the item's OCR,
  raw/mt1867_djvu.txt) supports "lists among Novello's publications of the past month". Story [^mt1867].

## Rejected

- Photograph of William Chatterton Dix, Commons File:William_Chatterton_Dix.jpg: 139 x 203 px, source a Tumblr
  page, no holding library or record stating public domain. Not used.
- Dix's tomb at St Andrew's, Cheddar (Commons): CC BY-SA 4.0. Not allowed.
- Julian, Dictionary of Hymnology (1892), p. 302: a dictionary text column only, in a Google-digitized copy
  (bub_gb_); it adds little beside the two printed pages chosen. Not downloaded, not used.
- Bramley and Stainer No. XIV music page (n37): already the Greensleeves page's 4.jpg. Not used, as briefed.
- Magdalen photochroms of the Tower (LCCN 2002708030) and Founder's Tower (2002708029): same rights, but one college
  view is enough; the river view was checked for people and is clear.

## Checker's changes (IMAGE-CHECK-8)

- 2.jpg caption: "in a printing of the 1870s" now reads "in a later, undated printing" (es: "en una impresión
  posterior sin fecha"). The 1870s rests only on the catalogue's guess "[187?]"; the story calls it "a later
  printing". The date field is now "undated (catalogued [187?])", and licenceEvidence says the imprint is Novello,
  Ewer and Co., the firm's name until 1898. The old media.json is in dropped/.
- 1.jpg: the caption's "In 1867 Bramley was a Fellow of the college and Stainer its organist" matches the Musical
  Times advert of 1 December 1867 (3.jpg: "Fellow and Tutor of S. Mary Magdalen College", "Organist of S. Mary
  Magdalen College, Oxford") and the story's "The book of 1867". No people at the largest size LoC publishes (the
  1920 px rendering of its master): bridge, banks and water checked.
