## assistant-output-folder-pointer
- issue: https://github.com/PyAutoLabs/autolens_assistant/issues/96 (closed)
- completed: 2026-07-30
- workspace-prs:
  - https://github.com/PyAutoLabs/autolens_assistant/pull/97 (merged 5d4c4559)
  - https://github.com/PyAutoLabs/autofit_assistant/pull/26 (merged ce150b97)
  - https://github.com/PyAutoLabs/autocti_assistant/pull/16 (merged 37cdd1e3)
- summary: All three assistant cells now tell novice/teacher-mode users where an active fit writes output and point at the canonical workspace explanation instead of duplicating a directory tree.
- validation: autofit and AutoCTI CI green unchanged; autolens wiki-currency green and boundary green after the shared policy classifier landed.
- notes: The autolens PR also corrected two stale HPC citations exposed by its existing wiki-currency gate.

## Original prompt

# Assistants point novices at the output folder when a fit starts

Every assistant cell that launches a model-fit should, when the user reads as a
novice or the session is in teacher mode, tell them the output folder is live and
show them how to look at it — rather than leaving them staring at a running
search with nothing to do.

Targets: @autolens_assistant, @autofit_assistant, @autocti_assistant (the three
cells that have `modes/teacher.md` + fit-launching skills; @euclid_assistant has
neither).

The canonical prose already exists and must be pointed at, not re-written:

- **lens / galaxy** — `__Output Folder Layout__` in
  `autolens_workspace/scripts/imaging/modeling.py` (also in `interferometer`,
  `point_source`, `group`, `cluster`, `weak` `modeling.py`, and the same section
  in `autogalaxy_workspace/scripts/{imaging,interferometer,ellipse}/modeling.py`)
  — a full annotated directory tree of `files/`, `image/`, `model.info`,
  `model.results`, `search.summary`, plus the `<unique_hash>` resume behaviour.
- **fit** — the output-folder breakdown in
  `autofit_workspace/scripts/overview/overview_2_scientific_workflow.py`.
- **cti** — `__Output Folder__` / `__On The Fly Outputs__` in
  `autocti_workspace/scripts/{dataset_1d,imaging_ci}/modeling/start_here.py`.

Edit points to consider (confirm during planning):

- `modes/teacher.md` "What changes" — add the output-folder walkthrough as an
  explicit teacher-mode behaviour at fit launch.
- the fit-launching skills — `al_run_search` (its "Output" section already quotes
  the path but does not point at the workspace section or the novice branch),
  `al_configure_search` "Output folder layout", `af_run_search` ("Monitoring a
  running fit"), `ac_fit_cti_model` ("Run the search and read the result").
- `skills/_style.md` "Adaptive depth" / "Newcomer mode" is where the novice cue is
  already defined — reuse it rather than inventing a second depth rule.

Keep it minimal: a pointer plus one line on what to open first (the on-the-fly
`fit.png` / `model.results`), and the fact that results appear *while* the search
runs. Do not copy the directory tree into the assistant repos — it would rot.

## Original request

I would like the assistant to direct uses to __Output Folder Layout__ (see
autolens_workspace/scritps/imaging/modeling.) when they begin modeling if they
sound novice or in teacher mode, so we ned to encourage each assistant tod o
that. i.e. make sure the iknow they an look at the output folder when the model
starts and know how to inspect it.
