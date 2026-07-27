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
