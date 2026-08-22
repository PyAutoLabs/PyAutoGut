# should_simulate rmtree's committed, gitignore-allowlisted datasets

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
- @autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: medium
Status: formalised

Tracked as PyAutoArray#470. Found during
`complete/2026/08/jax-grad-local-vs-ci-assertions.md`; **independent of that bug**
and untouched by its fix (PyAutoArray#471).

`should_simulate` deletes tracked, version-controlled data and replaces it with
capped-simulator output.

## The defect

`autoarray/util/dataset_util.py`, small-datasets branch:

```python
if os.environ.get("PYAUTO_SMALL_DATASETS") == "1":
    if Path(dataset_path).exists():
        shutil.rmtree(dataset_path)
```

The `rmtree` is unconditional. It never asks whether the directory holds
generated data or committed data.

## The live case

In `autolens_workspace_test`:

- `.gitignore:13` reads `!dataset/point_source/simple/**` — an explicit allowlist
  exception, i.e. the directory is **deliberately committed**. `git ls-files`
  confirms three tracked JSON files under it. The allowlist comments describe this
  class as real/external data that must never be purged.
- `scripts/point_source/visualization/visualization.py:39` calls
  `should_simulate("dataset/point_source/simple")`, and that script declares only
  `ENV: real_plots` (line 22), so it **keeps** `PYAUTO_SMALL_DATASETS=1` under the
  smoke profile defaults.

So an ordinary smoke run deletes committed data. It is then re-simulated through
`PointSolver.solve`, which under the cap short-circuits to a fixed position pair
(`PyAutoLens autolens/point/solver/point_solver.py:119`) — the replacement is not
merely lower-resolution, it is degenerate. Seven full-regime scripts read that
same directory, one of them in `smoke_tests.txt`.

## Severity — recoverable, but wrong

`git checkout -- dataset/point_source/simple` restores it and the deletion shows
as a dirty tree, so this is not unrecoverable data loss. But it silently violates
the invariant the allowlist exists to express, leaves developers with an
unexplained dirty tree after a routine smoke run, and — combined with the seven
full-regime readers — is the same mixed-regime collision class as #260 in a
dataset family the shape-based fix is structurally blind to (JSON, no FITS).

## Options (a design call is needed — do not just pick one)

1. **Skip `rmtree` for git-tracked paths.** Cheap, but puts a git dependency in a
   library utility: wrong layer.
2. **Have the workspace declare the exception** — give
   `point_source/visualization/visualization.py` a `full_datasets`-style profile
   entry so it never enters the small regime against committed data. Narrowest
   fix; leaves the general footgun armed for the next allowlisted dataset.
3. **Regime path separation** — capped runs write to a separate path so the two
   regimes never share a directory. Removes the collision rather than detecting
   it, and would also close #260's remaining gaps, but needs a path-rewrite layer
   in the IO with real sharp edges (committed read-only inputs like
   `uv_wavelengths/sma.fits` need read-fallback; plot outputs; absolute paths).

(2) unblocks the immediate case; (3) is the architecturally correct shape if this
class keeps recurring. Related: PyAutoNerves#153.

<!-- Sizing: declared medium; the sizing faculty derives large (9). Kept at medium —
     the scoped task is 'take the design call, implement the narrow fix', which is
     small; only option 3 (regime path separation) would be large, and taking it is
     explicitly not assumed here. -->

<!-- Split out of autolens_workspace_test#260 on 2026-08-22 under the
     one-prompt-one-task rule: separate defect, separate blast radius. -->
