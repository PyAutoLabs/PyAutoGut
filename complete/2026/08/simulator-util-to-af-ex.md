## simulator-util-to-af-ex
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1444
- completed: 2026-08-04 (all three PRs merged 2026-08-03; closed out 2026-08-04)
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1445 (MERGED 2026-08-03T17:36:47Z)
- workspace-prs: https://github.com/PyAutoLabs/autofit_workspace/pull/130 (MERGED 2026-08-03T21:40:46Z) + https://github.com/PyAutoLabs/HowToFit/pull/42 (MERGED 2026-08-03T21:40:50Z)
- summary: moved the four 1D-Gaussian simulator helpers out of the duplicated
  workspace `util.py` files into the library as `af.ex.util`, deleting the two
  copies and repointing the scripts/notebooks in both workspaces. Additive API
  only; 4 functions moved, 2 files deleted, 4 scripts edited.
- evidence: parity proven — old workspace `util.py` vs new `af.ex.util` under an
  identical seed give identical file sets and byte-identical JSON for all four
  helpers; new `test_autofit/tools/test_example_util.py` 5 passed
  (`example/util.py` had ZERO coverage before); full PyAutoFit suite 1647 passed
  / 2 skipped; all 4 notebooks execute clean via `run_notebook.py`; all 4 `.py`
  siblings pass; `run_smoke.py` 10/10 in BOTH workspaces;
  `check_navigator.py --banners=fail` OK in both.
- discovery: a SECOND failure was masked behind the first in
  `HowToFit/scripts/simulators/simulators.py` — a trailing `runpy.run_path` used
  `path.dirname(path.abspath(__file__))`, and `__file__` is undefined in a
  notebook kernel (it survived into `notebooks/simulators/simulators.ipynb`
  cell 41), so that notebook failed again the instant the util import was fixed.
  Fixed in the same PR with a root-relative `path.join("scripts", "simulators",
  "simulators_sample.py")`.
- unblocked-by: complete/2026/08/dep-floors-source-chain-ci.md (PyAutoNerves#146).
  The latent red was NOT the dependency floors — `setup.py` stamped `1.0.dev0` on
  source builds, below every date release, so the new `>=` floors could not be
  satisfied. Fixed by stamping `9999.0.0.dev0` in all six libraries. #130's smoke
  then went 17:30Z success → 20:07Z ResolutionImpossible → 21:3xZ success on the
  SAME commit — the control-and-recovery pair for the whole diagnosis.
- gate-override: the `pending-release` label gate was OVERRIDDEN on explicit
  human instruction 2026-08-03 ("all five once green"), after the consequence was
  stated and PROVEN by control test: workspace main calls `af.ex.util` helpers
  that exist on PyAutoFit main but not on PyPI, so a user on a released install
  hits `AttributeError` on the first simulator call against released autofit
  2026.7.29.2 in a clean venv — and HowToFit ships NO datasets (`dataset/`
  gitignored, 0 tracked files), so a new user would get no data at all. Releasing
  promptly became the remedy, which is what opened the release drive below.
- sizing-override: the Brain Feature Agent returned too-large (score 13) →
  split-into-4-phases. The factor breakdown measured no property of the change:
  3 repos (+6), library+workspace (+2), prompt length (+2), and keyword hits on
  trap/cross-repo/smoke/regression drawn from the prompt's own DIAGNOSIS prose
  (`architectural_risk` is literally the string "cross-repo"). Shipped as one
  task, one small PR per repo. Same prose-driven false positive as the
  point-source campaign's score of 11.
- correction-log (two things reported wrongly mid-drive, recorded so a later
  session does not inherit them): (a) autolens_workspace#453 was claimed OPEN and
  a three-option "deadlock" was built on it — it had ALREADY MERGED at 18:35:08Z;
  the stale `active.md` line had been read instead of the PR. (b) a fresh
  rehearsal was claimed to clear verify_install check D — it never could, because
  check D resolves dependencies from stable PyPI without `--pre`. Verify PR state
  and check semantics before presenting a decision.
- claim-note at ship time: `worktree_check_conflict` flagged PyAutoFit against
  point-source-defaults-campaign (#1441) and nautilus-1core-serial-pool (#1443);
  both were STALE (PRs merged 2026-08-01 12:47 and 19:12). Those two stale claims
  were finally released on 2026-08-04 — see
  complete/2026/08/nautilus-1core-serial-pool.md and the campaign's
  `claim-released` lines.
- SPLIT OUT, still live: the release drive this task opened is NOT finished and
  was moved to its own `active.md` entry `release-drive-2026-08-03` rather than
  being buried in this record — Stage 2/3 are clear to re-run, and the PUBLISH
  decision is still a separate human call. Its commit-shas, artifacts dir,
  resume commands, `do-not` notes and outcome analysis all travel with that entry.

## Original prompt

# Simulator notebooks cannot `import util` — move the helpers into `af.ex.util`

Type: bug
Target: autofit
Repos:
- PyAutoFit
- autofit_workspace
- HowToFit
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

Four workspace-smoke notebook failures share one cause,
`ModuleNotFoundError: No module named 'util'`:
`autofit_workspace/notebooks/simulators/simulators.ipynb`,
`autofit_workspace/notebooks/simulators/simulators_sample.ipynb`,
`HowToFit/notebooks/simulators/simulators.ipynb`,
`HowToFit/notebooks/simulators/simulators_sample.ipynb`.
Evidence: PyAutoHeart workspace-smoke run 30790463134.

**Diagnosis (done — this is NOT a cwd bug and NOT a regression of the
notebook kernel-cwd fix).** `import util` fails under *both* the old kernel cwd
(`notebooks/simulators/`) and the new pinned one (workspace root); reproduced
directly with `python -c "import util"` from each. The real asymmetry is
**script dir vs. cwd**: `python scripts/simulators/simulators.py` puts
`scripts/simulators/` on `sys.path[0]` and so resolves
`scripts/simulators/util.py` — which is why the `.py` siblings pass. A notebook
kernel has no script dir, `sys.path[0]` is the cwd, and `util.py` exists only
under `scripts/`, so no cwd in the tree resolves it.

`notebooks/simulators/util.py` used to exist as a hand-maintained duplicate
(`git show 73aab12:notebooks/simulators/util.py`, 326 lines). It cannot survive:
`PyAutoHands/autohands/generate.py:131` does
`shutil.rmtree(WORKSPACE_PATH / "notebooks")` on every build and then copies only
`.ipynb`, `.rst` and `.md` — no `.py` is ever copied into `notebooks/`.
Restoring the copy would not fix it anyway now that the kernel cwd is pinned to
the workspace root.

**Sweep (complete).** Exactly these four notebooks — a grep across every
`.ipynb` in the workspace for local (non-package) module imports returns only
these two `import util` sites in two repos. Only four source files import it
(`scripts/simulators/simulators{,_sample}.py` × 2 repos). `util.py` exists in
only these two repos and the two copies are byte-identical apart from four
docstring path strings (`autofit_workspace/dataset` vs `HowToFit/dataset`).
`generate.py` also converts `util.py` into a `util.ipynb` of bare function defs
that nothing can import.

**Approved fix (human-chosen).** Move the four simulate functions
(`simulate_dataset_1d_via_gaussian_from`,
`simulate_data_1d_with_kernel_via_gaussian_from`,
`simulate_dataset_1d_via_profile_1d_list_from`,
`simulate_data_1d_with_kernel_via_profile_1d_list_from`) into PyAutoFit's
existing `af.ex.util` (`autofit/example/util.py`, already home to
`plot_profile_1d`), delete both 346-line workspace `util.py` copies, and call
`af.ex.util.*` from the four scripts. This removes the local-module trap
entirely — it works for scripts, notebooks and Colab alike
(`autonerves/setup_colab.py:250` chdirs to the workspace root, matching the
pinned kernel cwd) — kills the cross-repo duplicate, and removes the useless
generated `util.ipynb`.

**Masked second failure (found while planning).** `HowToFit/scripts/simulators/
simulators.py` ends with a `runpy.run_path(path.join(path.dirname(
path.abspath(__file__)), "simulators_sample.py"))` chain-run that survives into
`HowToFit/notebooks/simulators/simulators.ipynb` (cell 41). `__file__` is
undefined in a notebook kernel, and no `.py` exists in the notebooks tree
anyway — so that notebook fails a second time the instant the `util` import is
fixed. Replace with the root-relative `path.join("scripts", "simulators",
"simulators_sample.py")`, which resolves identically for the script (run from
the repo root by convention), the notebook (kernel cwd pinned to root) and
Colab. Note `simulators_sample.py` is byte-identical across the two repos but
`simulators.py` is not — this trailing block is HowToFit-only.

**Two library-side constraints verified (a naive copy gets both wrong).**
1. *matplotlib must stay an in-function import.* It is not in PyAutoFit's
   `requirements.txt` and the existing `plot_profile_1d` already defers it
   (`autofit/example/util.py:34`); the workspace copies import it at module
   scope, and hoisting that would make matplotlib a hard import of `autofit`.
2. *`from autofit import to_dict` cannot be used at module scope here.*
   `autofit/__init__.py:125` does `from . import example as ex` but `to_dict`
   is not bound until line 172, so the from-import would hit a partially
   initialised module. Use `from autonerves.dictable import to_dict` (the real
   source line 172 re-exports). `af.util.numpy_array_to_json` is fine via
   `import autofit as af` — attribute lookup happens at call time, the
   `example/analysis.py` precedent.

`autofit/example/util.py` currently has no test coverage; add a unit test that
each helper writes `data.json` / `noise_map.json` into a `tmp_path`.

**Brain sizing OVERRIDDEN (recorded per policy).** The Feature Agent returned
`too-large (score 13) → split-into-4-phases`. The factor breakdown contains no
component that measures the change: 3 repos (+6), library+workspace (+2),
prompt length (+2), and keyword hits on `trap`, `cross-repo`,
`smoke`/`regression` taken from this prompt's own diagnosis prose
(`architectural_risk` is literally the string "cross-repo"). The real change is
four functions moved, two files deleted, four scripts edited — uniform per file,
additive API only, nothing removed. Shipped as one task with one small PR per
repo.

Library first (PyAutoFit), then the two workspaces behind the pending-release
merge gate.

<!-- filed 2026-08-03 from a workspace-smoke triage session; diagnosis and fix choice already settled with the human -->
