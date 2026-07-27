# clean_slate: write-site provenance, tests, and polish

Type: maintenance
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 5 of the dataset-bulk series — the machinery leg. PyAutoBrain#167 gave
`bin/clean_slate.sh` a simulator-provenance sweep; a 2026-07-27 dry-run audit + rule
replay shows what it misses and where it is fragile. Goal: the wake_up cleanup actually
reclaims regenerated dataset bulk across the workspaces **and** the HowTo repos, safely,
with tests.

## Current rule (for reference)

`clean_slate.sh:88-135`: remove an untracked dir at exactly `dataset/<type>/<name>`
(depth 3, no tracked files inside) iff both `"<name>"` and `"<type>"` appear as quoted
literals in one `scripts/**` file named `simulator*` or under `simulator/`/`simulators/`.
Repos: hard-coded `DATASET_REPOS` at `:55-56` (both workspaces, autofit_workspace,
autocti_workspace, all three HowTo). Dry-run via `DRY_RUN=1`. Invoked for real by
`wake_up.md:42-43`; `--packaging` leg also called by the hygiene conductor.

## Verified misses (rule replayed 2026-07-27)

Written by **non-simulator scripts** — invisible to the rule:

| Repo | Path | Size | Writer |
|---|---|---|---|
| autolens_workspace | `dataset/interferometer/simulated_lens` | 5.0 MB | `scripts/interferometer/start_here.py` |
| autolens_workspace | `dataset/imaging/simulated_lens` | 180 KB | `scripts/imaging/start_here.py` |
| autolens_workspace | `dataset/point_source/{simulated_lens,start_here_example}` | 20 KB | `scripts/point_source/start_here.py` |
| autolens_workspace | `dataset/cluster/csv_api_example` | 24 KB | `scripts/cluster/csv_api.py` |
| autogalaxy_workspace | `dataset/imaging/simulated_galaxy` | 772 KB | `scripts/imaging/start_here.py` |
| autogalaxy_workspace | `dataset/interferometer/simulated_galaxy` | 40 KB | `scripts/interferometer/start_here.py` |
| HowToLens | `dataset/imaging/howtolens` | 28 KB | `tutorial_6_data.py:365-372` |
| HowToGalaxy | `dataset/imaging/howtogalaxy` | 28 KB | `tutorial_3_fitting.py:576` |

The HowTo repos are a **100% miss**: their entire live dataset payload is
tutorial-written, so clean_slate is a silent no-op there today. Also missed:
`autolens_workspace/dataset/imaging/tutorial` (188 KB, **no writer anywhere** — orphan),
empty leftover dirs (`autogalaxy_workspace/dataset/multi/`, `HowToFit/dataset/example_1d/`).

## The safety constraint that shapes the design

Widening to "any script mentions the name" is **wrong** — `start_here.py` files both READ
real data and WRITE simulated data (`purge_committed_simulated_datasets.md`, "the trap"
section). Must-never-delete set that a naive rule would catch:
`dataset/cluster/smacs0723` (52 MB GPL download), `dataset/cluster/a2744/data.fits`,
`dataset/weak/a2744_pyrrg` (2.8 MB, named in `scripts/weak/real_data/a2744.py`),
`dataset/multi/rxj1131`. Judge by **write site** — `output_to_fits` /
`dataset.output_to_fits` with the dataset path feeding the output call — never by name
occurrence. Note the current `grep -F` literal match is already inconsistent
(`Path("dataset") / "imaging" / "howtolens"` matches; `Path("dataset", dataset_type,
dataset_name)` never does) and produces right-outcome-wrong-reason cross-file hits.

## Scope

1. **Write-site provenance** replacing/augmenting the name-literal rule, covering
   non-simulator writers; keep the tracked-file guard (`:124`) and the depth handling
   (currently hard-pinned to 3 — `:108`, `:125`).
2. **Orphan handling**: decide policy for untracked dataset dirs with *no* writer
   (e.g. `imaging/tutorial`) and for empty leftover dirs — sweep or report.
3. **Tests — currently zero** for phases 1/1b/2/3 (`tests/test_clean_slate.py` only
   exercises `--packaging`). Net-new coverage must assert: never delete tracked files;
   never delete the real-data set above (fixture-shaped); read-vs-write discrimination on
   a `start_here.py`-style fixture that reads one dataset and writes another.
4. **Size warning** (`:173-177`): per-dataset-dir not per-file, and acknowledgeable —
   after series leg 1 purges `cluster/simple` the current spam disappears anyway, but the
   mechanism stays broken.
5. **wake_up doc truth**: `wake_up.md:18-21` claims clean_slate is "non-destructive …
   git-aware and reversible"; phase 1b `rm -rf`s untracked dirs git cannot restore. Fix
   the claim (and confirm auto-run is still the right default).
6. **Recurring `git gc`**: HowTo repos had 13.9/11.1/17.7 MiB of never-packed loose
   objects (one-off `git gc` run 2026-07-27). Add a periodic `git gc --auto` (or
   equivalent) to the wake_up/clean_slate path so it does not regrow.
7. Consider sweeping `__pycache__`/`.ipynb_checkpoints` (6 dirs in autolens_workspace
   alone; nothing cleans them today) — or explicitly decide they're not worth it.
8. `tests/test_hygiene_conductor.py` references clean_slate (packaging delegation only)
   — re-check if the CLI surface gains flags.

## Out of scope

Committed-dataset purges (series legs 1–2) and HowTo guard migration (leg 3) — this leg
is the PyAutoBrain machinery only.
