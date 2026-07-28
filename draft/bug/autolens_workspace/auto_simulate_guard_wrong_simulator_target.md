# Auto-simulate guards point at a simulator that writes a different dataset

Type: bug
Target: workspaces
Repos:
- @autolens_workspace
- @autogalaxy_workspace
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: planned
Issue: https://github.com/PyAutoLabs/autolens_workspace/issues/359

## Symptom

`run_scripts (3.12, autolens, imaging)` and `run_scripts (3.12, autogalaxy, multi)`
fail in `PyAutoHeart/workspace-validation`:

```
scripts/imaging/features/multi_gaussian_expansion/likelihood_function.py ...
  FAIL (7.7s) FileNotFoundError: [Errno 2] No such file or directory: 'dataset/imaging/simple/data.fits'
scripts/imaging/features/pixelization/likelihood_function.py ...
  FAIL (7.8s) FileNotFoundError: [Errno 2] No such file or directory: 'dataset/imaging/simple/data.fits'
```

## Root cause

The auto-simulate guard runs a simulator that writes a **different dataset**
than the one the script then loads.

`scripts/imaging/features/pixelization/likelihood_function.py`:

```python
dataset_path = Path("dataset", "imaging", "simple")          # line 83
...
if al.util.dataset.should_simulate(str(dataset_path)):        # line 91
    subprocess.run([sys.executable,
                    "scripts/imaging/features/no_lens_light/simulator.py"], check=True)
```

but `scripts/imaging/features/no_lens_light/simulator.py` writes:

```python
dataset_type = "imaging"
dataset_name = "simple__no_lens_light"
```

So the guard fires, simulates `imaging/simple__no_lens_light`, and the script
then loads `imaging/simple` — which still does not exist.

## Why it surfaced now

The mismatch is **old** — `git log -S` puts the `no_lens_light/simulator.py`
guard target at `1f39244f` ("Add auto-simulate snippet to all example
scripts"), well before the recent work. What changed is the guard *mechanism*:
autolens_workspace#354 ("migrate 116 raw auto-simulate guards to
should_simulate", merged 2026-07-27 15:00 BST) replaced the raw
`if not path.exists()` checks with `al.util.dataset.should_simulate`. These two
scripts were green in the 06:15 run and red in the post-#354 dispatch, so the
new predicate lets execution proceed where the old one did not.

### RESOLVED 2026-07-28 — it is the first option

`PyAutoArray/autoarray/util/dataset_util.py:54` settles it:

```python
if os.environ.get("PYAUTO_SMALL_DATASETS") == "1":
    if Path(dataset_path).exists():
        shutil.rmtree(dataset_path)          # <-- deletes first

return not Path(dataset_path).exists()
```

With the flag off, `should_simulate` is an exact drop-in for
`not path.exists()`. **There is no wider `should_simulate` bug** — the guard
targets were always wrong and the old check masked them. Fix the targets.

One hazard worth carrying into the fix: `profile_smoke.yaml:16` and
`profile_release.yaml:32` both set `PYAUTO_SMALL_DATASETS=1`, and under that
flag the guard **`rmtree`s the dataset directory before testing it**. So a
mis-targeted guard does not merely fail to produce the right dataset — it
actively destroys a correct one that was previously satisfying the load, then
simulates a different one. That turns a latent mismatch into a hard failure and
is why these went red under validation rather than silently passing.

## Fix

Repoint each guard at the simulator that actually writes the dataset the script
loads — except where the *load path* is the wrong half of the pair, in which
case fix the path and keep the guard.

**Audited on 2026-07-28** with a resolver that evaluates each guard's
`dataset_path` and each invoked simulator's written path, across both
workspaces. Six confirmed mismatches (script → correct action):

| Script | Fix |
|---|---|
| `al scripts/imaging/features/pixelization/likelihood_function.py:91` | guard → `scripts/imaging/simulator.py` (script builds a `lens_galaxy` with a `bulge`, so `simple` is the right data; repointing the *load* to `no_lens_light` would feed it the wrong dataset) |
| `al scripts/imaging/features/multi_gaussian_expansion/likelihood_function.py:80` | **path**, not guard → `Path("dataset", "imaging", dataset_name)`; `dataset_name = "lens_light_asymmetric"` is already set on line 71 and ignored by the hardcoded path. The guard is correct — the docstring is explicitly about asymmetric light needing MGE |
| `al scripts/multi/features/slam/simultaneous.py:94` | guard tests `Path(dataset_main_path, dataset_name)` = `multi/imaging/lens_sersic/lens_sersic`, a doubled path that can never exist, while the loads use `dataset_main_path`. Guard → `dataset_main_path`. Not a `FileNotFoundError` — it re-simulates on *every* run, forever |
| `ag scripts/multi/features/imaging_and_interferometer/modeling.py:64` | guard → sibling `.../imaging_and_interferometer/simulator.py` (writes the interferometer half). **Also** the imaging half (~line 91) has *no* guard at all — add one → `scripts/multi/simulator.py` |
| `ag scripts/guides/plot/examples/mat_plot.py:43` | guard → `scripts/imaging/simulator.py` (writes `imaging/simple`); currently runs `guides/plot/simulator.py`, which writes `imaging/sersic_x2` |
| `ag scripts/guides/plot/examples/visuals.py:60` | same as `mat_plot.py` |

Cleared as correctly wired (do not "fix" these): the `samples/` guards in
`guides/modeling/advanced/{graphical,expectation_propagation,hierarchical}.py`,
the second guard in `multi/features/pixelization/modeling.py`, and the
self-guard in `group/features/multi_gaussian_expansion/simulator.py` (inline
body, not a subprocess).

`al scripts/guides/hpc/example_cpu.py` was a seventh case (guarded an HPC path
no workspace simulator can write). **Self-resolved** — `#360` replaced it with
`example_cpu_and_gpu.py`, which has the local-fallback block and a matching
guard target.

## Why the smoke gate did not catch it

None of the six scripts appear in `smoke_tests.txt` or `smoke_notebooks.txt` in
either workspace. The per-PR gate never executes them, so a fix cannot be
verified by running smoke — it needs a real run against a cleared dataset dir
(see Verification). Do **not** bulk-add them to the smoke list; it is a small
curated subset by design.

## Verification

- The example datasets are **not committed** (`dataset/.gitignore`; only
  `cosmos_web_ring` and `slacs1430+4105` are present locally under
  `dataset/imaging/`), so a clean checkout already reproduces this — no deletion
  step needed for most of them.
- Run each of the six affected scripts from the repo root and confirm it
  simulates and loads without a `FileNotFoundError`. Use `PYAUTO_TEST_MODE=2`
  and `PYAUTO_SMALL_DATASETS=1` to keep runs fast — and note the second flag is
  what exercises the `rmtree` branch, so it is the honest setting to verify
  under, not a shortcut.
- For `slam/simultaneous.py` the symptom is different: confirm the simulator
  runs **once** and that a second invocation of the script skips simulation.
- Full proof is a `workspace-validation` dispatch with both shards green.
- A reusable guard-audit resolver (parses every guard's `dataset_path` and each
  simulator's written path, reports disagreements) was written for this task —
  worth re-running after any future guard migration.

## Notes

- Pre-existing; unrelated to the 2026-07-27 red-jobs sweep.
- Sibling finding filed separately:
  `draft/bug/workspaces/notebook_kernel_cwd_breaks_auto_simulate.md` — the
  notebook-CWD bug that accounts for ~20 of the same job's failing shards.
