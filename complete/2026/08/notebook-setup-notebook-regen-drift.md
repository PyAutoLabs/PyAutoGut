Regenerated the 285 autolens_workspace notebooks that had drifted from
PyAutoHands generator output. autolens_workspace#481 MERGED 2026-08-07
(f3006b3d), closing issue #480. Branch `claude/dev-script-title-underline-5d3c3p`,
restarted from main 573bde8 after #478 merged (same session-designated branch,
new PR — merged-branch restart rule).

- **The drift:** PyAutoHands build_util.py uncomments
  `# from autolens import setup_notebook; setup_notebook()` when generating
  notebook cells, but committed notebooks carried the commented form — so
  none of them called setup_notebook() on main, and every notebook-touching
  PR either dragged the churn or hand-restored around it (as #478 did).
- **Sweep:** clean-main `generate.py autolens`, notebooks-only, 285 files /
  288±288 lines. Audited: 285 setup_notebook flips + 2 JSON-indent
  normalizations of a hand-inserted batch_size comment line (imaging/ and
  multi_galaxy/ start_here.ipynb) — direct evidence committed notebooks were
  hand-edited rather than generated. Catalogue zero diff. Count came in at 285,
  not the prompt's ~290 estimate.
- **Verification:** second regeneration on the swept tree is a no-op (same
  285-file set, stable); check_navigator --banners fail green; underline state
  from #478 preserved (0 typos / 14 banners); CI both smoke legs + all three
  navigator checks green (~9 min).
- **SIBLING DRIFT MEASURED AND FILED (not fixed):** clean-tree dry-runs
  2026-08-07 with PyAutoHands 2a4fb11 — autogalaxy_workspace 127 modified
  (126 flips + 6 OTHER diff lines, audit before committing),
  autofit_workspace 31 (32 flips), HowToFit 13 (13 flips); HowToLens and
  HowToGalaxy CLEAN. Follow-up prompt:
  `draft/maintenance/workspaces/notebook_setup_notebook_drift_siblings.md`
  (one task, three PRs — mge-sigma phase-2 precedent).
- **Environment trap (repeat of #478's):** ipynb-py-convert cannot pip-install
  on modern setuptools; vendor the package into site-packages + a CLI shim.

## Original prompt

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
