# Purge committed simulated datasets from autocti_workspace (~120 MB)

Type: maintenance
Target: autocti_workspace
Repos:
- autocti_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 6 of the dataset-bulk series. Every clean_slate run warns about six committed
`dataset/imaging_ci/*` datasets totalling ~120 MB — by far the largest committed-data
mass left in the organism:

| Dataset | Size |
|---|---|
| `dataset/imaging_ci/cosmic_rays` | 25 MB |
| `dataset/imaging_ci/bias_uncorrected` | 19 MB |
| `dataset/imaging_ci/non_uniform` | 19 MB |
| `dataset/imaging_ci/parallel_x2__serial_x2` | 19 MB |
| `dataset/imaging_ci/serial_cti` | 19 MB |
| `dataset/imaging_ci/simple` | 19 MB |

Apply the leg-1 recipe (autolens_workspace#352 / PR#353): establish simulator
provenance per dataset by WRITE SITE (bin/dataset_provenance.py is now on PyAutoBrain
main and can be run directly for the verdicts), audit guard coverage of every consumer
(autocti uses the `ac.` namespace — check whether `ac.util.dataset.should_simulate`
exists; CTI datasets may be large enough that regeneration needs PYAUTO_SMALL_DATASETS
handling), add missing guards, PROVE clean-tree regeneration per dataset via a guarded
consumer (files re-created and read back, not rc=0), then purge: untrack + drop any
`.gitignore` allowlist re-includes (check whether autocti_workspace even has the
allowlist regime — it was not a #126 leg; if it lacks `dataset/**` + `!` pins, adopt
the regime as part of this task) + `check_dataset_allowlist` if applicable.

Cautions carried from prior legs:
- A dataset whose guard cannot be added cleanly STAYS COMMITTED, stated explicitly.
- Judge by write site, never name mention; real/reference data (if any) is untouchable.
- Check consumers in autocti_workspace_test as well — its scripts may read these
  datasets and would break on a purge without guards (test workspaces are code-heavy;
  memory: no smoke tests live in library test dirs).
- arcticpy pip DOWNGRADES numpy (memory) — do not pip-install anything.
- Condemn purged bytes via PyAutoGut with the pre-purge SHA; smoke autocti after.

Out of scope: `autolens_workspace/dataset/imaging/cosmos_web_ring` (11 MB) — real JWST
data, permanent keep. History-blob removal — that is leg 7
(`draft/maintenance/workspaces/history_blob_purge.md`), human-gated.
