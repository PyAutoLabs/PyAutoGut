## raw-guard-migration
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/354
- completed: 2026-07-27
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/355, https://github.com/PyAutoLabs/autogalaxy_workspace/pull/171
- summary: Leg 3 of the dataset-bulk series. Migrated 116 (autolens, 113 scripts) + 61 (autogalaxy, 59 scripts) raw `if not dataset_path.exists():` auto-simulate guards to al./ag.util.dataset.should_simulate — functional in these repos because their smoke/release profiles set PYAUTO_SMALL_DATASETS=1 (stale full-res data now force-regenerates at the cap; raw guards only fired on absence). Safety came from per-site classification before conversion: guard body must run a paired simulator subprocess AND the site must not be on the (file,line) exclusion list — 7 download guards over real data (incl. the 96 MB RELICS mosaic), the inverted SDP.81 guard (raises-when-absent; conversion would delete committed non-regenerable data), 9 results-bootstrap guards (_quick_fit on output dirs), 5 inline-write/path-fallback bodies, 11 file-path guards (rmtree on a file crashes), all left byte-identical. Census reconciliation exact: 118 = 116 + 2 latent dataset_Path() NameError sites deferred to a filed bug prompt. HowToFit/autofit_workspace migration REJECTED and recorded (no PYAUTO_SMALL_DATASETS in their profiles, no autoarray import; would need a new af.util.should_simulate — note af.util is a flat module, autofit/__init__.py:114 — plus a new env contract in PyAutoFit, for zero functional gain). Notebooks (113+59, pairing verified exact), navigator catalogues and .script_sizes.json regenerated in-diff. Smoke 14/14 + 10/10. Shipped under the 2026-07-27 heart-ack. Follow-ups filed: draft/maintenance/workspaces/file_path_guard_decision.md, draft/bug/autolens_workspace/subhalo_sensitivity_dataset_path_nameerror.md. Merged 2026-07-27: autolens 7f6ba9954, autogalaxy f0efa50a9.

## Original prompt

# Migrate raw auto-simulate guards to should_simulate (autolens + autogalaxy)

Type: maintenance
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 3 of the dataset-bulk series, rescoped 2026-07-27 after a full four-repo guard
census (supersedes the HowToFit-centric framing of
`howtofit_should_simulate_migration.md`). Migrate every safe raw
`if not dataset_path.exists():` auto-simulate guard to
`al./ag.util.dataset.should_simulate(str(dataset_path))` in the two repos whose smoke
and release profiles set `PYAUTO_SMALL_DATASETS=1` — there the migration is functional
(force-regeneration at reduced resolution), not cosmetic.

## Census (2026-07-27, verified per-site)

| Repo | safe SIMULATE sites | existing should_simulate | PYAUTO_SMALL_DATASETS |
|---|---|---|---|
| autolens_workspace | **118** | 60 | SET (smoke+release) → functional gain |
| autogalaxy_workspace | **61** | 17 | SET → functional gain |
| autofit_workspace | 24 | 0 | not set → **do not migrate** |
| HowToFit | 11 | 0 | not set → **do not migrate** |

**HowToFit/autofit_workspace decision (recorded):** rejected. Neither imports autoarray;
migration would need a new `af.util.should_simulate` in `PyAutoFit/autofit/tools/util.py`
(note: `af.util` is a flat module bound at `autofit/__init__.py:114` — an `autofit/util/`
package would collide) plus a brand-new `PYAUTO_SMALL_DATASETS` contract in PyAutoFit,
to buy zero functional benefit (their profiles never set the var; the 1D Gaussian
datasets have nothing to cap). Revisit only if those profiles ever adopt the var.

## Exclusions — NEVER migrate these (should_simulate rmtree's the path)

- **DOWNLOAD guards (7, autolens):** `weak/start_here.py:116`, `weak/real_data/a2744.py:74`,
  `weak/features/strong_lensing/a2744.py:90`, `multi/features/imaging_and_point_source/modeling.py:75`,
  `cluster/start_here.py:150`, `cluster/lenstool/data.py:122`, `cluster/lenstool/data.py:331` —
  bodies download real data (up to 96 MB RELICS mosaic); conversion would delete it.
- **Inverted guard:** `interferometer/start_here.py:179` raises FileNotFoundError for the
  shipped SDP.81 data — conversion deletes a non-regenerable committed dataset.
- **OTHER (5):** `point_source/start_here.py:150,:368` (inline json writes),
  `autogalaxy guides/hpc/example_cpu_and_gpu.py:207,:242` (path fallback rebinding),
  (HowToFit tutorial_5:103 mkdir — out of scope repo anyway).
- **Results-bootstrap (8):** `guides/results/start_here.py` (both repos) + 6 autogalaxy
  `guides/results/aggregator/*.py` — guard a search-output dir and run `_quick_fit.py`;
  conversion would rmtree + re-fit on every smoke run.
- **File-path guards (11):** guard a file, not a dir — `NotADirectoryError` under rmtree;
  split to `draft/maintenance/workspaces/file_path_guard_decision.md`.

## Plan

1. Deterministic migration script: convert `if not dataset_path.exists():` →
   `if al./ag.util.dataset.should_simulate(str(dataset_path)):` ONLY where the guard body
   (next ~12 lines) runs a `subprocess` on a `simulator` script AND the site is not in
   the exclusion list above. Assert final counts: 118 (autolens) + 61 (autogalaxy).
2. py_compile every touched file; regenerate notebooks both repos (pairing verified
   clean: every guard script has a paired notebook, zero orphans); refresh navigator
   catalogue + `.script_sizes.json` per bulk-edit policy.
3. Smoke both repos; ship one PR per repo (uniform sweep — no phase split).

## Follow-ups (separate)

- `draft/maintenance/workspaces/file_path_guard_decision.md` — the 11 file-path guards.
- `draft/bug/autolens_workspace/subhalo_sensitivity_dataset_path_nameerror.md` — latent
  `dataset_Path()` NameError ×2, masked by no_run.yaml.
