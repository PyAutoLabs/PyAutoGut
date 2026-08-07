# Regenerate 331 autolens_workspace notebooks drifted from generator output (setup_notebook line)

Difficulty: small
Autonomy: supervised
Priority: low

## The problem

A full PyAutoHands regeneration dry-run (`generate.py autolens`) against
**unmodified** scripts on `@autolens_workspace` main modifies **331 committed
notebooks by exactly one line each**: `PyAutoHands:autohands/build_util.py`
(line ~204) uncomments

```
# from autolens import setup_notebook; setup_notebook()
```

into the active form for notebook cells, but the committed notebooks carry the
commented form. Net effect: every one of those notebooks on main currently
**never calls `setup_notebook()`**, and any PR that regenerates notebooks drags
this 331-file churn into its diff (or must hand-restore, as the underline task
did).

Measured 2026-08-07 on autolens_workspace `8f1965c` with PyAutoHands `2a4fb11`.

## Likely cause

The committed notebooks were last produced either by a generator version
predating the uncomment transformation or by lockstep hand-edits. The
transformation itself predates the autobuild→autohands rename, so the drift has
been accumulating across recent notebook commits.

## Proposed fix

One dedicated sweep PR: run `generate.py autolens` on clean main, commit the
notebook-only diff (expected: 331 files × 1 line, the setup_notebook flip —
verify nothing else rides along), and confirm `check_navigator.py` stays green.
Check whether `autogalaxy_workspace` / `autofit_workspace` / the HowTo repos
have the same drift and file siblings if so.

41 notebooks were already brought to generator truth by the underline task
(autolens_workspace#476), so the count at sweep time will be ~290.

## Verification

- After the sweep, a regeneration dry-run on clean main is a no-op
  (`git status` empty).
- No notebook diff lines other than the setup_notebook flip.

## Provenance

Surfaced as a side-observation while shipping the title-underline fix
(autolens_workspace#476, PyAutoMind
`active/script_title_underline_off_by_one.md`), which introduced none of it —
that task's regeneration dry-run against unmodified scripts is the measurement.
