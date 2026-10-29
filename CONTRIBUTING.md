# Proposing a change

Fixes are welcome: a wrong note, a confusing line, a lesson that asks too much, a song that sits
badly for a voice. A singer's ear is as welcome as a teacher's.

## The licence of what you send

**Inbound = outbound.** By sending a pull request, you agree that your contribution is licensed
under `CONTENT-LICENSE`, and that you have the right to license it so. There's no separate
agreement to sign. A song must be in the public domain (its words and its tune), or yours.

## How

- **Open an issue first** for anything bigger than a typo: which lesson (its id, for example
  `vib-1-laser`, and the step) or which song and part, what's wrong, and what you'd change.
- **Then a pull request** that changes one lesson, one song or one fix at a time, saying what you
  heard or saw and why your change is better.
- **The checks must pass** (`tools/course_check.py`, `tools/template_check.py`); CI runs them.
- **Who reviews it:** a course's maintainer reviews the music and the teaching; the arranger
  reviews songs (ranges, voicings, the arrangement review); Stackapella (Hillel) merges. A change to
  how a lesson is scored, or a new step kind, is a change to the app too, and starts as an issue.

## Commits

Small and focused, each saying what changed for a singer, for example
"Vibrato: the second lesson's wave starts slower". No co-author or attribution trailers.
