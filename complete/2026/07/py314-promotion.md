Promoted Python 3.14 to fully supported across the ecosystem — required CI
matrix legs, trove classifiers, and a silent import banner — the same day its
forkserver blocker was fixed (see py314-fork-context).

- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/219 (closed)
- prs (all merged 2026-07-31, human-authorized batch merge under the same
  unrelated Heart-RED override as the fix): PyAutoHands#220 (matrix),
  PyAutoNerves#145 (banner + classifier), PyAutoArray#429, PyAutoFit#1440,
  PyAutoGalaxy#544, PyAutoLens#683 (classifiers)
- matrix: 3.14 promoted from the non-required `experimental_python_314`
  unit-evidence job into the REQUIRED unit matrix (3.12/3.13/3.14 × five
  libraries) and the workspace smoke matrix; the experimental job, its
  continue-on-error plumbing and summary caveats deleted; allow-prereleases
  dropped (3.14 stable).
- banner: `_RECOMMENDED_PYTHON_VERSIONS` now {(3,12),(3,13),(3,14)}; the
  supported-version strings derive from the constant so the next promotion is
  one line. Experimental-branch + bypass tests retargeted to 3.15;
  no-warn test parametrized over 12/13/14 (155 passed). Verified live:
  importing autonerves on 3.14.4 is silent.
- classifiers: `Programming Language :: Python :: 3.14` added to the five
  core pyprojects; `requires-python >=3.12` unchanged.
- evidence: python_matrix workflow_dispatch run 30646078121 concluded
  SUCCESS, zero non-green jobs — 15/15 unit legs and 9/9 smoke legs green,
  including 3.14 autofit_workspace smoke (runs the formerly-failing
  `overview_1_the_basics.py`).
- out of scope (deliberate): docs prose still calling 3.14 experimental
  (python-312-floor campaign docs phase owns the supported-version wording);
  AutoCTI/AutoReduce (independent floors/cadence); PyAutoHeart
  install-verify 3.14 leg.

## Original prompt

# Promote Python 3.14 to supported (matrix, classifiers, banner)

Type: feature
Target: libraries
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

## Original request

> do all follow ups now

(Follow-ups from the py314-fork-context task, PyAutoFit#1439 / issue #1437,
merged 2026-07-31: the Python 3.14 forkserver blocker is fixed and the
previously-failing tutorial completes end-to-end on 3.14.4.)

## Scope (the three named follow-ups)

1. **PyAutoHands `.github/workflows/python_matrix.yml`** — promote 3.14 from
   the non-required `experimental_python_314` unit-evidence job into the
   required unit matrix (3.12/3.13/3.14) and the workspace smoke matrix (the
   leg that actually exercises the fixed factor-graph path). Delete the
   now-redundant experimental job. Drop `allow-prereleases` (3.14 is stable).
2. **Classifiers** — add `Programming Language :: Python :: 3.14` to
   PyAutoNerves, PyAutoArray, PyAutoFit, PyAutoGalaxy, PyAutoLens
   `pyproject.toml`. `requires-python >=3.12` unchanged.
3. **PyAutoNerves banner** — add `(3, 14)` to
   `_RECOMMENDED_PYTHON_VERSIONS` in `autonerves/__init__.py` so 3.14 no
   longer warns as experimental; derive the supported-version strings from
   the constant so the next promotion is one line.

Evidence: after merge, `workflow_dispatch` the python_matrix run and confirm
the 3.14 legs are green.

Out of scope (report only): prose in workspace/RTD docs still calling 3.14
experimental — that wording belongs to the python-312-floor campaign's docs
phase; AutoCTI/AutoReduce (independent floors/cadence); PyAutoHeart
install-verify 3.14 leg.
