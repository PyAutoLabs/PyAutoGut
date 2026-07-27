## purge-simulated-datasets
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/352
- completed: 2026-07-27
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/353
- summary: Leg 1 of the dataset-bulk series. Purged 7 committed simulated datasets (~17 MB: cluster/simple 15.7 MB, imaging/{mass_stellar_dark,double_einstein_ring,extra_and_scaling_galaxies}, group/{mass_stellar_dark,double_einstein_ring,scaling_relation}) — untracked + .gitignore allowlist re-includes dropped; migrated the 20 consumer scripts from raw `if not dataset_path.exists():` guards to al.util.dataset.should_simulate and regenerated the 20 paired notebooks. interferometer/uv_wavelengths KEPT — verified real SMA uv coverage (read-only simulator input, no writer; both workspaces share this pattern) and marked non-regenerable in .gitignore. Verification: clean-tree regeneration proofs for all 7 via guarded consumers (7-246 s; not merely rc=0), check_dataset_allowlist OK (57 files, 9 patterns), smoke 14/14. Shipped under the 2026-07-27 Heart YELLOW heart-ack. Gotcha for future audits: the "5 unguarded datasets" premise was wrong — all consumers were raw-guarded; grepping only should_simulate misses the raw idiom (autolens still has 132 raw-guard files, folded into the series migration draft). Condemned entry release-datasets/autolens-regenerable-leg2 (pre-purge SHA 0bb170c57, sweep-after 2026-08-27). Merged 2026-07-27; PR #353 merge commit b0b7a41d5.

## Original prompt

# Purge committed simulated datasets from autolens_workspace

Type: maintenance
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

`autolens_workspace/dataset/` is 99 MB on disk. ~17 MB of that is **committed** data
that a simulator script in the same repo regenerates on demand — it should not be in
the repo. This is the next leg of the force-committed-dataset purge (PyAutoBuild#126;
prior legs: autolens_workspace#272 category A + multi, autofit_workspace#92,
autogalaxy_workspace#129).

This was surfaced while auditing PyAutoBrain#167 (`clean_slate.sh` simulator-provenance
sweep). `clean_slate` correctly refuses to touch tracked files, so it can never reclaim
these — the fix is to stop tracking them, not to widen `clean_slate`.

## The mechanism

`autolens_workspace/.gitignore` ignores `dataset/**` wholesale and re-includes specific
datasets with `!dataset/<type>/<name>/**` entries (the allowlist regime, PyAutoBuild#126
leg 4, guarded by `PyAutoHands/autohands/check_dataset_allowlist.py`). Every dataset below
is on that allowlist deliberately. Purging one means removing its `!` re-include AND
`git rm -r --cached` — not just deleting files.

## Candidates — committed, with simulator provenance

Verified by the PyAutoBrain#167 rule applied exactly: both the dataset's `<name>` and its
`<type>` appear as string literals in one `scripts/**/simulator*.py`.

| Dataset | Size | Simulator |
|---|---|---|
| `dataset/cluster/simple` | 15,700 KB | `scripts/cluster/simulator.py` |
| `dataset/imaging/mass_stellar_dark` | 636 KB | `scripts/imaging/features/advanced/mass_stellar_dark/simulator.py` |
| `dataset/imaging/double_einstein_ring` | 580 KB | `scripts/imaging/features/advanced/double_einstein_ring/simulator.py` |
| `dataset/group/scaling_relation` | 64 KB | `scripts/group/features/scaling_relation/simulator.py` |
| `dataset/imaging/extra_and_scaling_galaxies` | 56 KB | `scripts/imaging/features/scaling_relation/simulator.py` |
| `dataset/group/double_einstein_ring` | 40 KB | `scripts/group/features/advanced/double_einstein_ring/simulator.py` |
| `dataset/group/mass_stellar_dark` | 40 KB | `scripts/group/features/advanced/mass_stellar_dark/simulator.py` |
| `dataset/interferometer/uv_wavelengths` | 16 KB | `scripts/interferometer/simulator.py` |
| **total** | **17,132 KB** | |

`dataset/cluster/simple` alone is 15.7 MB and is the source of the two
`WARNING: committed dataset ... is 7 MB (>5 MB)` lines `clean_slate.sh` emits every run.

## The blocker — auto-simulate coverage is partial

The purge precedent (autolens_workspace#272) is only safe because each purged dataset is
regenerated on demand by a guarded example script — `should_simulate()`
(`PyAutoArray/autoarray/util/dataset_util.py:54`) or `not dataset_path.exists()` → simulator
subprocess. **Only 3 of the 8 candidates currently have such a guard:**

| Dataset | Guard |
|---|---|
| `cluster/simple` | `scripts/weak/fit.py`, `scripts/weak/likelihood_function.py` (note: cross-type — the guard lives under `weak/`, not `cluster/`; check every consumer) |
| `group/scaling_relation` | `scripts/group/features/scaling_relation/modeling.py`, `modeling_for_luminosities.py` |
| `imaging/extra_and_scaling_galaxies` | `scripts/imaging/features/scaling_relation/modeling.py` |
| `imaging/mass_stellar_dark` | **none** |
| `imaging/double_einstein_ring` | **none** |
| `group/double_einstein_ring` | **none** |
| `group/mass_stellar_dark` | **none** |
| `interferometer/uv_wavelengths` | **none** |

So this is not a pure delete. For the 5 unguarded datasets, **add the auto-simulate guard
to every consuming script first**, prove it regenerates from a clean tree, and only then
purge. A dataset whose guard cannot be added cleanly stays committed — say so rather than
purging it and breaking a user's first run, CI, or Colab.

`interferometer/uv_wavelengths` needs particular care: it is an *input* to
`scripts/interferometer/simulator.py` as well as an output, so purging it may create a
bootstrap cycle. Verify the direction before acting.

## Do NOT touch — real observational data, deliberately committed

These are loaded via `from_fits()`, never written. They appear next to the candidates and
several are named in the same scripts:

- `dataset/imaging/cosmos_web_ring` (11,344 KB — real JWST)
- `dataset/interferometer/sdp81` (5,104 KB — real ALMA)
- `dataset/group/102021990_NEG650312660474055399` (2,048 KB)
- `dataset/interferometer/many_visibilities` (1,636 KB — committed, **no** provenance found)
- `dataset/cluster/a2744` (1,448 KB — real HST; note `.gitignore` line 19 re-excludes
  `data.fits`, which is downloaded at runtime)
- `dataset/imaging/slacs1430+4105` (384 KB)
- `dataset/point_source/rxj1131` (12 KB)

Also untracked and never to be committed: `dataset/cluster/smacs0723` (52,648 KB — GPL
Lenstool files from Mahler et al., download-only, redistribution not permitted).

## The trap that makes this task subtle

**A dataset name appearing in a script does not mean the script writes it.**
`scripts/interferometer/start_here.py` contains both:

```python
dataset_name = "sdp81"
dataset = al.Interferometer.from_fits(...)                          # READS real ALMA data
...
dataset_path = Path("dataset") / "interferometer" / "simulated_lens"
al.output_to_fits(...)                                              # WRITES generated data
```

Classifying by name-mention would mark 11 MB of real JWST and 5 MB of real ALMA data as
regenerable. Judge by **write site** (`output_to_fits`, `dataset_path` construction feeding
an output call), never by name occurrence. The candidate table above is restricted to
`simulator*` scripts precisely because simulators only ever write — that assumption does
not hold for any other script.

## Verification gate

Purged datasets must be re-creatable from a clean tree by an ordinary user, CI and Colab:

1. `git rm -r --cached <path>` + drop the matching `!dataset/...` line from `.gitignore`.
2. Confirm `python -m autohands.check_dataset_allowlist` (or the pre_build leg that calls
   it) still passes.
3. From a tree with the directory physically deleted, run each consuming script and prove
   the dataset is regenerated — not merely that the script exits 0.
4. Run the affected workspace smoke subset. `cluster/simple` feeds `scripts/weak/`, so the
   weak-lensing scripts are in scope even though the dataset lives under `cluster/`.
5. Bytes stay recoverable from history via the pre-purge SHA; condemn via PyAutoGut
   (`PyAutoMind/condemned.md`, sweep-after clock) as prior legs did.

## Series — this is leg 1 of the dataset-bulk cleanup

Sibling drafts (each its own task/PR; do not pull them into this one):

- `draft/maintenance/workspaces/purge_autogalaxy_database_datasets.md` — the last 512 KB
  of committed regenerable (and unconsumed) data in autogalaxy_workspace.
- `draft/maintenance/howto/howtofit_should_simulate_migration.md` — HowToFit is the one
  repo still on raw `not path.exists()` guards.
- `draft/maintenance/howto/howto_markdown_render_bulk.md` — 13.4 MB of committed,
  regenerable `markdown/` render PNGs across the three HowTo repos (decision needed).
- `draft/maintenance/pyautobrain/clean_slate_write_site_provenance.md` — widen the
  PyAutoBrain#167 provenance rule to catch non-simulator writers (~6 MB of untracked
  cruft it currently leaves behind, incl. `dataset/imaging/tutorial`), add tests
  (phases 1–3 currently have none), fix the size-warning spam, correct the wake_up
  "non-destructive" claim.
