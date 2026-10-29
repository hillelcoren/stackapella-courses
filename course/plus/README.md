# The Plus courses: how to fix or improve a lesson

These folders hold the Plus courses: the words, the exercises and the songs' lines for every lesson.
They're public, and you're welcome to improve them with an issue or a pull request: a clearer line,
a wrong fact, a note pitched badly, a lesson that's too long. Contributions come in under the same
terms as the content goes out: the content licence at the top of the repository
(`CONTENT-LICENSE`).

The code that plays a lesson (the lesson screen, the trace lane, the scoring) lives in `web/js/`
and isn't needed to fix a lesson. How the courses are built, and the rules every lesson keeps, are in
[docs/plus-courses-build-plan.md](../../../docs/plus-courses-build-plan.md), section 6a. Each course
has its own outline, with what every unusual field means, in `docs/courses/<id>.md`.

## Where things are

```
web/course/plus/
  courses.json          the list of all 27 courses: id, slug (the site's page), group (skills, styles
                        or beyond), order in its group, featured, status (live or soon), title, line, file
  clips.json            clips a real singer records for the lessons (see "Clips" below)
  vibrato/course.json   one course: its units, lessons and steps
  folk/course.json
  pitch/course.json
  ...
```

The free course is `web/course/course.json`, one level up, in the same shape.

## A lesson

A course has `units`; a unit has `lessons`; a lesson has `steps`, played one at a time. Every word
people read is an object of languages, `{ "en": "..." }`.

```json
{
    "id": "vib-1-laser",
    "title": { "en": "A calm, straight line" },
    "steps": [
        {
            "kind": "learn",
            "headline": { "en": "A straight tone is how chords ring. It's light and calm, never a held throat." },
            "steps": [
                { "title": { "en": "Start from the easy note" }, "detail": { "en": "The same sigh, the same ease" } }
            ],
            "visual": "steady"
        },
        {
            "kind": "wave",
            "text": { "en": "Hold a calm, straight \"oo\" for 4 seconds." },
            "exercise": { "tempo": 60, "lead": 2, "step": 0, "lyric": "oo", "drone": { "step": 0 }, "target": [{ "seconds": 4, "kind": "straight" }] },
            "measures": { "en": "Your stars are for how long it stayed straight." }
        }
    ]
}
```

- **Pitches are steps from the learner's own comfortable note** (`step: 0` is that note, `4` a
  major third above, `-5` a fourth below), so every exercise fits every voice. Never write a
  fixed note.
- **Beats** run from 0 at the step's `tempo`. A note is `{ "beat", "length", "step", "lyric" }`.
- A lesson's **stars come from its last scored step**, and its `measures` line says what they
  measured.
- **Lesson ids never change** once a lesson is live: progress and stars are kept by them.

## The step kinds

| Kind | What the learner does | Its main fields |
|---|---|---|
| `learn` | Reads a headline and up to three cards, sees a picture, may hear an example | `headline`, `steps`, `visual`, `listen` |
| `try` | Wait for me: each note plays and waits until it's found | `exercise` (`notes`, `tempo`, `drone`) |
| `play` | Hears it, then sings it back (`turn: true`), or sings over a drone or chords (`turn: false`); scored | `exercise` (`notes`, `turn`, `drone`, `chords`, `score`) |
| `wave` | The trace lane: rides a ribbon (a steered wave, a straight line, a bloom, a free hold) | `exercise.target`: `[{ "seconds", "kind", "hz", "cents" }]` |
| `choose` | Listens to clips and taps the answer; no mic | `exercise.rounds`: `[{ "prompt", "clips", "options", "answer", "why" }]` |
| `selfcheck` | Hears a model, records, compares, answers self-check questions; not scored | `exercise.model`, `exercise.questions` |
| `bullseye` | Hears a call and sings the answer (the same notes, a leap from them, a chord's root, home); each sung note lands as a dart; scored on where they landed | `exercise.echoes` (`[0, [0, 7], { "call", "sing", "chord", "key" }]`), `tempo`, `lengths`, `think`, `drone`, `home`, `reveal`, `named`, `stack`, `score`, `generous`, `compare`, `under` (each explained in `docs/courses/perfect-pitch.md`, section 9) |
| `breathhold` | Holds one long note over a drone as long as it's easy; the take ends when they stop; scored on how it ended, how steady it was and their own goal | `exercise.step`, `lyric`, `drone`, `lead`, `max`, `baseline`, `goal`, `compare`, `generous` (see `docs/courses/breath.md`, section 9) |

## A `play` exercise's extra fields

Every one is optional; an exercise without them plays exactly as the free course's do.

| Field | Where | What it does |
|---|---|---|
| `with` | the exercise | Partner voices that sound while you sing, faint on the lane, never scored: `[{ "notes": [...], "volume": 0.5 }]`, or the sung line itself later, for a round or a canon: `[{ "delay": 12, "steps": -12 }]` (12 beats later, an octave down). Afterwards, Hear it together plays your take with them. See `docs/courses/counterpoint.md`. |
| `answer` | the exercise (`turn: true`) | Call and response: the guide sings `notes`, and you sing back these notes instead. |
| `choices` | a note | Steps any of which is right (`"choices": [3, 4, 7]`): each lights, and the one you sing is the one scored. |
| `cents` | a note | Tunes a note off the piano's: `-14` is a pure major third, as barbershop singers tune it. |
| `listenOnly` | a note | Heard, never sung or scored (an echo's call, or notes to distract you). |
| `guide: false` | the exercise | A cold start: the notes you sing don't sound first, and show no names until your turn ends. With `droneAfter` (beats), the drone comes in that far into your turn. |

## Clips: recordings a real singer makes

Where the guide voice can't model a sound well enough (a natural vibrato, a twang), a clip in a
listening round can name a slot, `"clip": "vibrato.natural"`, and still carry its own notes. The slot
is described in `clips.json`: what to sing, the pitch (in steps from the singer's own comfortable
note, or a range), how long, the style, and a fallback. Beta singers record the slots from their
My parts page; once one is accepted, the lesson plays the recording, credited, and until then its
notes. **A slot's id never changes once it's recorded**: to change what's asked, add a new slot.

## The rules a change must keep

- **Plain, warm and short.** One or two lines to say why; no lectures. Sentence case. No em dashes.
- **True.** A fact needs a source, and no living famous person is named as a model.
- **Safe.** Nothing at the edge of a voice's range; holds of eight seconds at most; a safety line
  wherever a voice could strain.
- **Public domain** for tunes and words. If you're not sure, choose another.
- **Honest.** The stars measure only what the app can really hear. What it can't hear yet is a
  `selfcheck`, which says so.

## Trying your change

1. Run the app locally (the repository's README, "web" setup): `cd web && php -S localhost:8081 tool/serve.php`.
2. Open `http://localhost:8081/?api=mock&as=admin`, then go to `/learn/<lesson id>`. Before launch,
   Plus courses show only to staff, which `as=admin` is.
3. Run the tests: `sh web/tool/test.sh` (they check every course file's shape and that
   every lesson id is unique).
