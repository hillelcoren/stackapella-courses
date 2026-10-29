# The course format

Every course, free and Plus, is one JSON file in the same shape, shared by the web app and the Flutter
apps: `web/course/course.json` (the free course) and `web/course/plus/<id>/course.json` (each Plus
course, listed in `web/course/plus/courses.json`). This folder says what a course file may contain:

| File | What it is |
|---|---|
| `course.schema.json` | A JSON Schema of the file's structure (course, units, lessons, steps, notes, words), for editors and other apps |
| `steps.json` | Every step kind and field: what each means, and which app plays it (`web`, `flutter`: yes, no or unknown) |

`web/tool/course_check.py` checks every course file against both, with Python's standard library
only, and runs with the web tests (`web/tool/test.sh`). It fails on:

- a step kind or a field that `steps.json` doesn't list;
- a word that isn't `{ "en": "..." }` (every word people read is one string per language);
- a lesson id used twice anywhere (progress is kept by it);
- a listening round whose answer isn't one of its options;
- a clip slot that isn't in `web/course/plus/clips.json`.

It also counts the lessons an app can't play yet: a lesson with a step kind or a field that app marks
`no` (or `unknown`, until someone checks). `python3 web/tool/course_check.py --apps` lists them with
the reason, so the Flutter app can say "open this lesson on the web" until it catches up.

## Adding a step kind or a field

1. Build it in the web app (a step kind is registered in `web/js/lesson-steps.js`).
2. Add it to `steps.json` with a line saying what it is, and `flutter: "no"`.
3. Describe it in the course's own outline (`docs/courses/<id>.md`).

A field the check doesn't know fails the tests, so the format never drifts from what the apps play.
