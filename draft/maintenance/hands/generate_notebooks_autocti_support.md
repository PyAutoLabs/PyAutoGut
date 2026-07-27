# generate.py: support autocti + stop rmtree-before-validation

Type: maintenance
Target: hands
Repos:
- PyAutoHands
- PyAutoNerves
Difficulty: easy
Autonomy: supervised
Priority: low
Status: formalised

Found during dataset-bulk leg 6: `python generate.py autocti` is unsupported AND
destructive — `autocti` is absent from `COLAB_PROJECTS` in
`PyAutoHands/autohands/build_util.py`, and `generate.py` does
`shutil.rmtree("notebooks")` BEFORE validating the project name, so it deleted all 79
autocti notebooks and then crashed (leg 6 restored them from git and regenerated the
21 affected ones via `build_util.py_to_notebook` directly, byte-identically).

1. Move the rmtree after project validation (fail fast, destroy nothing).
2. Decide whether to add autocti to `COLAB_PROJECTS` + the `_PROJECTS` registry in
   `autonerves/setup_colab.py` — note this is a deliberate content change (autocti
   notebooks currently lack the Colab setup cell; adding it touches all 79).
3. Regression test: unknown project name must exit non-zero with notebooks/ intact.
