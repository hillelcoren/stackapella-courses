# Stackapella courses and songs

The lessons and the arrangements that [Stackapella](https://stackapella.com) teaches harmony with:
the free course, every Plus course, and the songs, as plain JSON anyone can read, fix and improve.

| Folder | What's in it |
|---|---|
| `course/course.json` | The free course |
| `course/plus/` | The Plus courses (`courses.json` lists them; `clips.json` names the real-voice clips their steps play) |
| `course/format/` | The course format: every step kind and its fields (`steps.json`, `course.schema.json`, the README) |
| `templates/free/` | The songs the app bundles, and `index.json` |
| `templates/library/` | The library's songs |
| `templates/format/` | The song format (`template.json`, kept in step with the app's) |
| `tools/` | The checks CI runs on every change |

## Checking a change

```sh
python3 -I tools/course_check.py
python3 -I tools/template_check.py
```

Both use Python's standard library only. The app's own tests (every course played through the
lesson engine, the song review and the catalogue sync) run in the Stackapella repository when a new
commit here is pinned there, before it reaches anyone.

## Trying a change in the app

With a checkout of the Stackapella repository beside this one:

```sh
CONTENT_DIR=~/path/to/this/checkout sh server/tool/content.sh link
```

The app then reads your working copy. Run its server and open a lesson or a song.

## Licence

`CONTENT-LICENSE` (inbound = outbound: what you send is licensed the same way). The Stackapella
name and mark aren't licensed here. How to propose a change is in `CONTRIBUTING.md`.
