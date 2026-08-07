- issue: none (no GitHub issue — worked directly from the draft prompt in a cloud session on explicit human instruction; the create_issue/start_dev machinery was bypassed)
- completed: 2026-08-07
- pr: https://github.com/PyAutoLabs/PyAutoCTI/pull/106 (MERGED, merge f40b2f78) + https://github.com/PyAutoLabs/autocti_workspace/pull/17 (MERGED, merge 50b701d1)
- notes: PyAutoCTI gained the one-line `from autoarray.util import dataset_util as dataset` export in `autocti/util/__init__.py` (mirroring autolens), making `ac.util.dataset.should_simulate` real. autocti_workspace then migrated its raw `if not path.exists(dataset_path):` auto-simulate guards to `ac.util.dataset.should_simulate(dataset_path)`, restoring PYAUTO_SMALL_DATASETS=1 force-regeneration. Census correction: the prompt said 21 guards; the sweep found **22 sites across 21 files** (`data_preparation/start_here.py` carries two). Side findings fixed in the same workspace PR: `simulate_datasets_missing.sh` pointed at the nonexistent `overview/non_uniform_charge_injection.py` (real file `non_uniform_cosmic_rays.py`), and `extract.py` / `cosmic_ray_flagging.py` each had a dead first `dataset_name =` assignment.
- evidence: full `test_autocti/` suite green with the export (271 passed, 0 failed; Python 3.12, arcticpy 2.6 built from source with apt libgsl-dev). Workspace validation: `extract.py` end-to-end with dataset absent (guard fired, simulated, exit 0); force-regen witnessed via a marker file deleted by a PYAUTO_SMALL_DATASETS=1 rerun; `cosmic_ray_flagging.py` exit 0. All 21 edited files pass py_compile; zero raw guards remain in scripts/.
- merge-context: merged 2026-08-07 on explicit human authorization ("monitor ci once green merge"), library first then the workspace sibling. PyAutoCTI CI green on both matrix legs (3.12/3.13). autocti_workspace has **no CI workflows at all** (resurrection-epic Phase 3 pending), so its merge evidence is the local validation above.
- traps: (1) autocti is NOT a registered PyAutoHands generate target (absent from `COLAB_PROJECTS` in build_util.py and workspaces.yaml), so notebooks could not be hand-regenerated — the 22 matching guard occurrences across 21 notebooks pick up the change at the next release-pipeline regen. (2) 8 of the workspace scripts are entirely CRLF (pre-existing); the sweep preserved each replaced line's ending to keep the diff at one line per site. (3) The library-first gate was satisfied by merge order; the release floor was waived by the owner's merge instruction — workspace scripts now require an autocti with the export until the next PyPI release.
- leftovers: the prompt's optional candidates were deliberately left for a sibling task — purging tracked `dataset/overview/` (48 files) and `dataset/dataset_1d/` (239 files) by the leg-1 recipe. Also retired in the same session (separate Mind commit): the stale `draft/bug/autolens_workspace/subhalo_sensitivity_dataset_path_nameerror.md`, already fixed on main by autolens_workspace fe9031e.

## Original prompt

# Export util.dataset in PyAutoCTI + migrate the 21 raw guards

Type: maintenance
Target: pyauto_cti
Repos:
- PyAutoCTI
- autocti_workspace
Difficulty: easy
Autonomy: supervised
Priority: low
Status: formalised

Found during dataset-bulk leg 6 (autocti_workspace#11): `ac.util.dataset` does not
exist — `autocti/util/__init__.py` lacks the `from autoarray.util import dataset_util
as dataset` line that `autolens/util/__init__.py` has (autoaray's
`dataset_util.should_simulate` is installed and works). Consequence: the 21
auto-simulate guards added in leg 6 use the raw `if not path.exists(dataset_path):`
idiom and lose `PYAUTO_SMALL_DATASETS=1` force-regeneration.

1. PyAutoCTI: add the one-line export, mirroring autolens (library PR).
2. autocti_workspace: mechanical sweep of the 21 guards to
   `ac.util.dataset.should_simulate(str(dataset_path))` + notebook regen
   (library-first merge gate applies; workspace PR waits on the release floor).

Also fold in the leg-6 side findings: `simulate_datasets_missing.sh` references the
nonexistent `simulators/overview/non_uniform_charge_injection.py` (real file:
`non_uniform_cosmic_rays.py`); `extract.py` and `cosmic_ray_flagging.py` each carry a
dead first `dataset_name =` assignment. Candidates for the same PR or a sibling:
`dataset/overview/` (48 files) and `dataset/dataset_1d/` (239 files) remain tracked
with simulators — purgeable by the leg-1 recipe.
