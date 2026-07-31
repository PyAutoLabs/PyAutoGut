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
