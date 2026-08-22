# Stamp the small-datasets regime at the FITS writer funnel

Type: bug
Target: pyautonerves
Repos:
- @PyAutoNerves
- @PyAutoArray
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

Tracked as PyAutoNerves#153. Follow-up to
`complete/2026/08/jax-grad-local-vs-ci-assertions.md` (PyAutoArray#471), which
closed the **imaging** manifestation of this bug class and deliberately left the
rest open.

`PYAUTO_SMALL_DATASETS=1` caps simulated datasets to a reduced resolution, but
**nothing on disk records which regime a dataset was written under**. That gap
lets a capped dataset survive into a later full-resolution run and be loaded
silently.

## Why the shipped fix is not enough

PyAutoArray#471 made `should_simulate` regenerate on the small->full transition by
*inferring* the regime from `data.fits`'s shape (the cap emits exactly
`SMALL_DATASETS_SHAPE_NATIVE = (16, 16)`). That inference is structurally blind to
two dataset families:

- **Point-source and weak-lensing datasets are JSON** — `dataset/point_source/simple/`
  holds only `.json`, and weak lensing writes `dataset.json`
  (`autolens_workspace/scripts/weak/simulator.py:136`). There is no FITS to infer
  from, so `should_simulate` degenerates to existence-only there.
- **Interferometer corruption is shape-invariant.** The visibility count is fixed
  by the committed uv file (`sma.fits`, 360 baselines) while the real-space grid
  the visibilities are computed from is capped 256x256 -> 16x16
  (`Grid2D.uniform`, `uniform_2d.py:499`). So a capped run writes a `data.fits`
  with **identical NAXIS** and garbage values.

The interferometer case is the reason this is `Priority: high`: unlike the imaging
failure that started all this, it produces **no shape mismatch and trips no
assertion**. It fails silently. A silent wrong answer in a likelihood is worse
than a loud one.

## The proposal

Record the regime at **write** time instead of inferring it at read time.

Every FITS write in the entire stack funnels through **one function** —
`autonerves/fitsable.py:89` `output_to_fits` (verified: it is the only
`output_to_fits` definition across PyAutoNerves, PyAutoArray, PyAutoGalaxy and
PyAutoLens, and is re-exported as `aa.output_to_fits`). A header card written
there when `PYAUTO_SMALL_DATASETS=1` is active is:

- **truthful by construction** — written by the same call that writes the data, so
  it cannot disagree with it, and there is no stamped-but-empty-directory failure
  mode (the reason a marker file written by `should_simulate` was rejected: that
  function runs *before* simulation and cannot write a truthful marker);
- **zero-call-site** — no changes across the ~420 `should_simulate` sites in the
  workspaces;
- **the only discriminant that can catch the interferometer case**, since it does
  not depend on shape.

`PyAutoArray.should_simulate` then prefers the stamp, keeping the existing shape
heuristic as the legacy fallback for datasets already on disk that carry no stamp.

## Risks to weigh before implementing

- This changes a header card on **every FITS the stack writes**. Round-trip tests,
  file-hash regression pins and golden-file comparisons could be disturbed. This is
  exactly why it was kept out of PyAutoArray#471 rather than riding along with it —
  it deserves its own deliberate change and its own CI run.
- **JSON datasets need a separate decision.** `autonerves/dictable.py:370` is the
  equivalent funnel, but stamping there risks round-trip pollution of the dictable
  schema. Point-source and weak lensing stay exposed until that is settled —
  decide it explicitly rather than by omission.
- The stamp only helps datasets written *after* it lands, so the shape fallback in
  PyAutoArray is not throwaway work and must not be removed.

## Suggested scope

1. Add the regime stamp to `output_to_fits`, gated on the env var. Decide the card
   name and whether absence means "full" or "unknown".
2. Teach `should_simulate` to prefer the stamp, shape check as fallback.
3. Run the round-trip / golden-file surface deliberately — that is the real risk,
   not the logic.
4. Take the JSON decision explicitly (stamp `dictable`, or record why not and
   leave point-source/weak-lensing tracked as still-exposed).
5. Validate against the interferometer case specifically: capped run then
   full-regime run must now regenerate, where today it silently does not.

<!-- Sizing: declared large; the sizing faculty derives too-large (11). Not phased —
     this is one coherent change plus one explicit sub-decision (the JSON funnel),
     and the score is prose-driven off an evidence-dense prompt (the same effect noted
     in complete/2026/08/jax-grad-smoke-timeout-budget.md). Revisit if step 3's
     round-trip surface turns out to be wide. -->

<!-- Split out of autolens_workspace_test#260 on 2026-08-22. That task fixed the
     imaging manifestation only and said so in the should_simulate docstring. -->
