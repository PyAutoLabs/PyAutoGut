# Point-source JSON datasets record no resolution regime

Type: bug
Target: pyautolens
Repos:
- @PyAutoLens
- @PyAutoArray
- @PyAutoNerves
Difficulty: medium
Autonomy: supervised
Priority: low
Status: formalised

Split out of PyAutoNerves#153 on 2026-08-22, which stamped the small-datasets
regime into every FITS the stack writes and deliberately left the JSON side
alone. This is that leftover, scoped down to what the evidence actually
supports.

## What is exposed

Exactly **one** dataset directory: `dataset/point_source/multiple_sources`. It
is regime-dependent and writes no FITS — only `point_dataset_*.json` plus a
`point_datasets.csv` (`autonerves/csvable.py:21 output_to_csv`, written at
`multiple_sources/simulator.py:257`). A capped run and a full run therefore
leave indistinguishable files, and `should_simulate` degenerates to
existence-only there.

That is 5 of 268 `should_simulate` call sites, and `point_datasets.csv` is a
third on-disk dataset representation that neither the FITS stamp nor any JSON
stamp currently reaches.

## Why it was deferred rather than fixed

Two facts made it cost-free to defer. **Both expire** — do not re-derive them,
re-check them:

1. `dataset/point_source/multiple_sources` is excluded from harness execution by
   `config/build/no_run.yaml:41-42`, blocked on **PyAutoLens#480**. When #480
   lands the script runs again and the exposure goes live. *This is the trigger
   for doing this work.*
2. `dataset/weak/simple` — the other FITS-less directory, and the one the
   original issue named — is regime-**invariant**. Its script uses
   `via_tracer_from`, not `via_tracer_random_positions_from`
   (`autolens/weak/simulator.py:118` vs `:140-142`), and nothing in that path
   reads `PYAUTO_SMALL_DATASETS`. There is no bug to fix. Anyone switching that
   script to the random-positions helper reintroduces regime dependence with
   nothing to catch it.

Note the issue text this came from claimed point-source datasets are "JSON with
no FITS". That is wrong: ordinary point-source datasets write a top-level
`data.fits` and are already covered. Only `multiple_sources` is not.

## Constraints on any fix (verified, do not rediscover)

- **In-payload stamping is survivable, but only at the top level.** An unknown
  key alongside `type`/`class_path`/`arguments` is silently ignored by both
  `autonerves.dictable.from_dict` and autofit's `ModelObject.from_dict`
  (`assertions` is the existing precedent). A key *inside* `arguments` reaches
  `cls(**arguments)` and raises `TypeError`, breaking every existing on-disk
  JSON dataset's load path.
- **A generic stamp in `output_to_json` is the wrong shape.** Of 146 non-test
  call sites only 18 serialise a dataset; ~88% are tracers, galaxies and
  position lists with no resolution regime to record. Stamping the funnel would
  attach a meaningless marker to thousands of model files per run in autofit
  search-output directories.
- **A sidecar must not use a `.json`, `.pickle`, `.csv` or `.fits` suffix.**
  `autofit/aggregator/search_output.py:88-97` rglobs search-output directories
  admitting exactly those four, so a `*.json` sidecar becomes a spurious
  aggregator entry in every result loaded from a search that wrote any JSON.
- **`to_dict` can return a bare scalar**, so any in-payload stamp needs an
  `isinstance(payload, dict)` guard or it silently no-ops.
- **The read side has no file to key on.** `multiple_sources` offers only
  `point_dataset_*.json` (a glob) or `tracer.json` (not unique to the family).
  A glob in a predicate ending in `shutil.rmtree` is explicitly forbidden by the
  `autolens_workspace_test#260` traps. This needs a naming-convention decision
  first, and that decision is the real work here.

## Suggested scope

1. Re-check both expiring facts above. If #480 is still open and `weak/simple`
   still uses `via_tracer_from`, this task is still not worth doing — say so and
   re-park it rather than building.
2. Decide the read-side naming convention. Without it there is nothing to build.
3. Then choose in-payload top-level key vs non-colliding sidecar, honouring the
   constraints above.
4. Cover `point_datasets.csv` in whatever is chosen, or state why not.

<!-- Sizing: medium. The code is small; the naming-convention decision is the task. -->
