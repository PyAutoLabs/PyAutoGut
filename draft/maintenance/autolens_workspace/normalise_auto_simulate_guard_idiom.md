# Normalise the two auto-simulate guard idioms

Type: maintenance
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

Surfaced while fixing #455 (missing-auto-simulate-guards). Not folded into that
fix because it is a behaviour change to scripts that currently PASS.

Two auto-simulate guard idioms coexist in `autolens_workspace/scripts/`, and
they are **not equivalent**:

**A — the standard idiom** (now the large majority):

```python
if al.util.dataset.should_simulate(str(dataset_path)):
    subprocess.run([sys.executable, "scripts/.../simulator.py"], check=True)
```

**B — hand-rolled**, in four scripts:

- `scripts/cluster/likelihood_function.py:104` — checks `data.fits` AND `mass.csv`
- `scripts/interferometer/features/pixelization/many_visibilities_preparation.py:82`
- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py:868`
- `scripts/imaging/features/advanced/subhalo/sensitivity/slam_source_pixelized.py:995`

```python
if not (dataset_path / "data.fits").exists():
    subprocess.run([sys.executable, "scripts/.../simulator.py"], check=True)
```

## The difference that matters

`autoarray/util/dataset_util.py:should_simulate` does two things:

```python
if os.environ.get("PYAUTO_SMALL_DATASETS") == "1":
    if Path(dataset_path).exists():
        shutil.rmtree(dataset_path)
return not Path(dataset_path).exists()
```

Under `PYAUTO_SMALL_DATASETS=1` (set by `config/build/profile_smoke.yaml`
defaults) idiom A **deletes and rebuilds** the dataset at reduced resolution;
idiom B does not. So the four B scripts will happily read a
**full-resolution** dataset left on disk by an earlier uncapped run, in a run
that is supposed to be capped. That is the exact shape of the
`PYAUTO_SMALL_DATASETS` shape-mismatch problem `should_simulate` was written to
prevent.

They also differ in what they test: A tests the **directory**, B tests
`data.fits` specifically. B is stricter against a half-written directory; A is
correct about the cap. `cluster/likelihood_function.py` is the strictest of all
(two files) and would lose that if naively converted.

## Proposed work

1. Convert the four B sites to `al.util.dataset.should_simulate`.
2. For `cluster/likelihood_function.py`, preserve the `mass.csv` check —
   either keep an additional `or not (dataset_path / "mass.csv").exists()`
   clause alongside `should_simulate`, or establish that the simulator always
   writes both so the directory check subsumes it. Do not silently drop it.
3. Re-run each of the four under the capped smoke profile
   (`PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1`) from a genuinely empty
   dataset dir AND from a stale full-resolution one — the second case is the
   one that currently misbehaves and the whole point of the change.
4. Consider whether `should_simulate` should grow an optional
   `required_files=[...]` argument so the stricter checks have a home in the
   library rather than in workspace scripts (PyAutoArray change — would make
   this a library+workspace task rather than workspace-only).

## Caution

All four scripts currently PASS smoke. This change can only make them slower
(rebuilding datasets that were previously reused) or newly-failing (if a
simulator misbehaves under the cap). Measure before and after; do not assume
the conversion is free.
