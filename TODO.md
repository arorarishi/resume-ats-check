# TODO / Future Work

## Master Resume as manageable JSON files

Currently the Master Resume (and its profiles) live only inside `data/applications.db` (see `app/database.py`: `get_master_resume`, `save_master_resume`, `get_all_master_resume_profiles`, etc.), edited only through the UI.

Goal: make each Master Resume profile available as a standalone JSON file so it can be:
- Opened and edited directly in a text/JSON editor.
- Diffed/compared between profiles or versions (e.g. via `git diff` or a JSON diff tool).
- Edited by hand — deleting or deselecting individual sections/entries (e.g. a job, a bullet, a skill) without going through the UI.

Rough shape of the work (not started, needs design):
- Export: write each profile to `data/master_resumes/<profile_name>.json` (or similar), kept in sync with the DB, or make the JSON file the source of truth and the DB a cache/index.
- Import: detect external edits to the JSON file and reload into the DB (file watcher, or an explicit "reload from file" action).
- Decide source of truth: DB-primary with JSON export, vs file-primary with DB as derived index — affects how conflicts/concurrent edits are handled.
- UI: surface the file path, and add an action to open/reveal the JSON file, plus a way to re-import after manual edits.
