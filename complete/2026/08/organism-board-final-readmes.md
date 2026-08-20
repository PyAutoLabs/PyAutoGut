- issue: https://github.com/PyAutoLabs/PyAutoScientist/issues/12 (close on record)
- shipped: 2026-08-19 — direct-main sweep: PyAutoScientist c34eadd..6d60765,
  PyAutoGut 211219a, PyAutoNerves f6d6d52. Organism board LIVE at
  https://pyautolabs.github.io/PyAutoScientist/ (badge "organism | STALE · 151 tasks
  queued"; README strip auto-committed on the first run).
- classification: feature (PyAutoScientist + Gut/Nerves READMEs) — the readability/
  dashboard arc's finale.
- summary: the ORGANISM BOARD — the human's umbrella-router idea ("if heart is ok
  there you'd go to Mind") — scripts/organism_board.py (stdlib; PyAutoScientist's
  first machinery): one row per organ board carrying that board's OWN published
  headline (Heart/Hands/Memory badge.json + Mind dashboard counts parsed from the
  committed page), a where-to-work-next banner keyed off the Heart verdict, 📋 door
  chips (/start_dev · /health · /release · /memory), badge + README
  scientist:begin/end strip; six-hourly organism_board.yml publishes Pages (site
  created out-of-band, the Hands lesson); ad hoc pytest suite (no CI gate by design
  in the umbrella repo — the workflow building the page is the operational check).
  READMEs: PyAutoScientist gained the badge/board paragraph/live strip (generated
  organ table untouched); PyAutoGut restructured to the house pattern (How
  PyAutoGut works: condemn → transit → void; no board — its ledger IS the Mind's
  condemned.md); PyAutoNerves opening in the house voice with organism pointers
  (install/examples untouched; no board — it ships on the Hands release board).
- key traps:
  - badge.json is now a cross-board CONTRACT: the umbrella router consumes each
    board's shields endpoint as its headline — renaming/reshaping a board's badge
    message breaks the router's row (and the Heart's colour drives the organism
    badge + banner).
  - PyAutoScientist had NO .gitignore — a git add -A committed __pycache__ on the
    first push (fixed next commit; .gitignore added). Second add -A slip of the
    day: explicit paths only, always.
- affected-repos:
  - PyAutoScientist
  - PyAutoGut
  - PyAutoNerves

## Original prompt

# Organism board on PyAutoScientist + final organ READMEs

Type: feature
Target: pyautoscientist
Repos:
- PyAutoScientist
- PyAutoGut
- PyAutoNerves
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

The readability/dashboard arc's finale. Human direction (2026-08-19, verbatim):

> ok final task, go oer the final PyAutoScietist repos and update their README.md
> files to the new style, i dont think they need dashboards but give it a quick
> thought and make sure the dashboard task itself we had all those notes is moved
> to complete

> I could imagine PyAutoScientist containing and umbrella dashboard linked to each
> project, which allows one to then know which dashboard to go to do work (e.g. if
> heart is ok there you'd go to Mind).

Scope (plan approved):
- **The organism board** (@PyAutoScientist, its first machinery): a router page on
  Pages — one row per organ board (Mind tasks · Heart health · Hands releases ·
  Memory knowledge) with each board's live headline (badge.json endpoints; Mind
  counts parsed from raw dashboard.md), a "where to work next" banner keyed off the
  Heart verdict, 📋 door chips, badge + README strip. stdlib collector, identity from
  git remote, rows degrade honestly.
- READMEs to the house style: PyAutoGut (How-it-works condemn→transit→void),
  PyAutoNerves (house-voice opening; library install/examples kept), PyAutoScientist
  (organism badge + board paragraph + live strip; the repos_sync-generated organ
  table untouched).
- Dashboard verdict for the small organs: NO boards for Gut (its ledger is the
  Mind's condemned.md) or Nerves (surfaced on the Hands release board) — the
  umbrella board covers routing.
- Close the dashboard-rollout prompt (one_tap_dashboard_more_surfaces.md) with an
  arc completion record; the two unshipped candidate surfaces (complete/-archive
  page, ideas one-tap) recorded as not pursued.
