# `generate.py autocti` raises — autocti_workspace notebooks cannot be regenerated

Type: bug
Target: hands
Repos:
- PyAutoHands
- PyAutoNerves
- autocti_workspace
Difficulty: small
Autonomy: supervised
Priority: medium

`python PyAutoHands/autohands/generate.py autocti`, run from
`autocti_workspace/`, aborts partway through with:

```
ValueError: inject_colab_setup: unknown project 'autocti' — add it to
COLAB_PROJECTS here and to the _PROJECTS registry in PyAutoNerves's
autonerves/setup_colab.py. Known: ['autofit', 'autogalaxy', 'autolens',
'howtofit', 'howtogalaxy', 'howtolens']
```

`autocti_workspace`'s 79 notebooks are therefore **unmaintainable by the current
tool**. They track `scripts/` 1:1 (79 scripts, 79 notebooks, no orphans on
either side), so they were maintained at some point — but **0 of the 79 carry a
Colab setup cell**, which dates them to before `inject_colab_setup` became a
hard requirement.

## Damage the crash does on the way out

`generate.py` calls `shutil.rmtree(WORKSPACE_PATH / "notebooks")` *before* the
per-script loop (`generate.py:114`), and `py_to_notebook` writes its
intermediate `.ipynb` next to the source script. So a failed run leaves:

- `notebooks/` **deleted** — 113 staged deletions in the observed run, only
  recoverable with `git checkout -- notebooks/`;
- a stray `.ipynb` beside the script it died on (observed:
  `scripts/dataset_1d/advanced/database/examples/data_fitting.ipynb`).

Worth fixing independently of the registry question: the rmtree should not
happen until the run can succeed, or the crash should restore what it removed.

## Fix options

1. **Register `autocti`** — a `COLAB_PROJECTS` entry in
   `PyAutoHands/autohands/build_util.py` plus a `_PROJECTS` entry in
   `PyAutoNerves/autonerves/setup_colab.py`. This is the path the error message
   asks for, but it is a *feature*: it adds a Colab setup cell to all 79
   notebooks and needs an autocti package stack. Note `arcticpy` — a hard
   dependency of the CTI stack — is known to downgrade numpy when pip-installed
   ([[project_cti_resurrection_epic_scoped]]), so the Colab install list needs
   care.
2. **Make injection opt-out per project** — skip rather than raise for projects
   with no Colab target. Cheaper, but it reverses a deliberate loud-failure
   choice, so it needs a human call.

Not a decision to take unilaterally: option 1 changes what users get, option 2
changes a policy someone chose on purpose.

## Consequence while this is open

`autocti_workspace` was swept for the `Finished.` / `Finish.` crutch in
PyAutoLabs/autocti_workspace#16 (35 occurrences in `scripts/`), but its
`notebooks/` could not be regenerated. That repo's notebooks currently retain:

- **34 `Finish.` markdown cells**, and
- **4 mangled code cells** containing a literal `# %%` and `'''` (a
  `SyntaxError` if run) in
  `notebooks/imaging_ci/modeling/features/{cosmic_rays,non_uniform,serial_cti,visualize_full}.ipynb`.

Both classes are already fixed in `scripts/`, so a single successful
`generate.py autocti` clears all 38 at once.

## Validation

- `generate.py autocti` exits 0 from `autocti_workspace/`.
- All 79 notebooks regenerate; no code cell contains a literal `# %%` or `'''`;
  no markdown cell is `Finish.`.
- A deliberately-failing run leaves `notebooks/` intact and no stray `.ipynb`
  beside any script.

## Notes

- Found 2026-07-30 while sweeping the `Finished.` crutch
  (PyAutoLabs/PyAutoHands#211). `autocti_workspace` is absent from
  `PyAutoHands/pre_build.sh`'s `run_workspace` matrix entirely, so no release
  path exercises this and the breakage has been invisible.
