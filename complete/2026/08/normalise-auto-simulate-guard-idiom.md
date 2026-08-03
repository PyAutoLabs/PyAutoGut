Converted the four hand-rolled auto-simulate guards in `autolens_workspace` onto
`al.util.dataset.should_simulate`. The class is now closed: **zero hand-rolled
guards remain** against 249 standard sites.

- autolens_workspace#463 (issue #462)

Follow-up left open by choice from #455 / #460 (missing-auto-simulate-guards) —
deliberately not folded in there because it changes behaviour in scripts that
were not failing.

## The behaviour that differed

`should_simulate` is not a synonym for `not (dataset_path / "data.fits").exists()`.
Under `PYAUTO_SMALL_DATASETS=1` (a `config/build/profile_smoke.yaml` default) it
`rmtree`s the dataset so the simulator rebuilds it at the capped resolution; a
bare `.exists()` check reuses whatever is on disk. The four scripts therefore
read a **full-resolution** dataset left by an earlier uncapped run inside a run
meant to be capped.

Isolated old-vs-new, the divergence is exactly one cell:

```
PYAUTO_SMALL_DATASETS=0   stale full-res -> old=False  new=False   (identical)
PYAUTO_SMALL_DATASETS=1   stale full-res -> old=False  new=True
```

Uncapped runs are untouched. The prompt's "can only make them slower" caution
therefore applies only to capped runs, where rebuilding is the entire point —
and measured, the two runnable scripts cost 12–22s either way.

## The failure mode is SILENT — correcting the prompt's prediction

The prompt predicted a shape-mismatch *crash*. Measured, it is quieter and
worse. Controlled run of `cluster/likelihood_function.py` under the capped
profile with a stale **(1000, 1000)** dataset on disk, the only variable being
whether the dataset is rebuilt:

| | pre-change | post-change |
|---|---|---|
| dataset after run | **(1000, 1000)** reused | **(16, 16)** rebuilt |
| image-plane log likelihood | `-2.3951e+07` | `1.7518e+01` |
| library image-plane log likelihood | `-3.1784e+07` | `1.7518e+01` |
| script's own `Match (rtol=1e-2)` | **False** | **True** |
| process exit | **0** | 0 |

A capped run silently computed on full-resolution data; the script's hand-rolled
likelihood disagreed with the library's by ~33%; its own consistency check said
`False`; and it **exited 0 anyway**. A teaching script demonstrating a wrong
number while reporting success. From an empty dataset dir the same script gives
`Match: True`, confirming the stale dataset is the cause.

**The generalisable lesson:** the `PYAUTO_SMALL_DATASETS` hazard is not
principally a crash. Where data and geometry can broadcast against each other it
degrades into wrong numbers with a zero exit code — which no CI gate that only
checks exit status can catch. Any future audit of this class should compare
*values*, not just exit codes.

## The finding the prompt did not have: two of the four never worked

`imaging/features/advanced/subhalo/sensitivity/slam_source_parametric.py` and
`slam_source_pixelized.py` guarded on **`dataset_Path()`** — an undefined name.
They raised `NameError: name 'dataset_Path' is not defined` the moment the
dataset was absent, i.e. the guard had never once executed successfully. A
botched `dataset_path` → `dataset_Path()` edit, presumably.

**Why nobody noticed:** the prompt's premise that "all four scripts currently
PASS smoke" is false — none of the four is in `smoke_tests.txt` at all, and
`config/build/no_run.yaml` excludes *every* sensitivity script ("all sensitivity
scripts need updating when visualization refactored"). Two scripts were carrying
a hard NameError behind a policy exclusion.

Lesson for the next guard sweep: **a static sweep for guard *idiom* also needs an
undefined-name pass**, because a guard that cannot run looks identical to a guard
that is merely non-standard. `pyflakes` catches it in one line and would have
flagged both at #455 time.

## Verification

Capped profile (`PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1` + the rest of
`profile_smoke.yaml`), from an empty dataset dir **and** a stale full-resolution
one — the second being the case that actually misbehaved:

| Script | Case A (absent) | Case B (stale full-res) |
|---|---|---|
| `cluster/likelihood_function.py` | exit 0, 13.7s, own `Match (rtol=1e-2): True` self-check passes | exit 0, 11.8s — stale **(1000, 1000)** rebuilt to **(16, 16)** |
| `interferometer/.../many_visibilities_preparation.py` | exit 0, 22.0s | exit 0, 18.3s — rebuilt (`data.fits` md5 `2d36bc69…` → `ee334711…`) |
| `subhalo/sensitivity/slam_source_parametric.py` | guard fires, dataset simulated, reaches line 974 (was NameError at 876) | n/a — `no_run` |
| `subhalo/sensitivity/slam_source_pixelized.py` | guard fires, dataset simulated | n/a — `no_run` |

Also: `scripts/check_sizes.sh` clean, full `run_smoke.py` green, notebooks
regenerated (exactly the four `.ipynb`, diffs confined to the guard lines),
navigator catalogue unchanged.

## Deliberately not done

- **`should_simulate(required_files=[...])`** (a PyAutoArray change, prompt item
  4). Only 1 of 249 call sites needs a stricter check, so a library API for a
  single caller is not earned. `cluster/likelihood_function.py` keeps its
  `mass.csv` clause inline instead, with `should_simulate` evaluated **first** so
  its rebuild side-effect always runs before `or` short-circuits. Recorded on
  #462 rather than silently dropped.
- **The two sensitivity scripts' remaining failures.** Both still fail further
  down on pre-existing stale-API faults — `'Model' object has no attribute
  'centre'` (parametric) and `module 'autolens' has no attribute 'MapperValued'`
  (pixelized). That is the standing `no_run` reason, not this task; this change
  strictly improves both and does not claim to fix them. A future task that
  un-`no_run`s the sensitivity tree inherits exactly these two.

## Sweep result (the class is closed)

The remaining `.exists()` checks under `scripts/` are deliberately different and
were left alone: a `FileNotFoundError` for the committed SDP.81 dataset
(`interferometer/start_here.py`), a path fallback
(`guides/hpc/example_cpu_and_gpu.py`), and secondary-artifact guards
(`positions.json`, `point_dataset_*.json`) that correctly sit *after* a primary
`should_simulate` — converting those would `rmtree` the dataset twice.

## Original prompt

# Normalise the two auto-simulate guard idioms

Type: maintenance
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: low
Status: active

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
