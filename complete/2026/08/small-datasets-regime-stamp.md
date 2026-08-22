- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/153
- completed: 2026-08-22
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/154 (merged 4ae8e8f)
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/474 (merged 82b5d16)
- workspace-pr: none — no workspace change needed (zero-call-site held)

`PYAUTO_SMALL_DATASETS=1` caps simulated datasets but nothing on disk recorded
which regime a dataset was written under, so a capped dataset could survive into
a full-resolution run and be loaded silently. PyAutoArray#471 closed the imaging
case by inferring the regime from `data.fits`'s shape. **The regime is now
stamped at write time** (`SMALLDAT` header card), which is truthful by
construction and — unlike shape — can reach the interferometer case, where the
visibility count is fixed by the committed uv file while the grid behind it is
capped, so a capped run writes identical `NAXIS` with garbage values and trips
no assertion at all.

**THE ISSUE'S CENTRAL PREMISE WAS WRONG, and not where it first appeared.**
#153 said every FITS write funnels through `output_to_fits` (`fitsable.py:89`).
It is the only *definition* of that name but not the only write path. Verified
inventory: **18 library FITS writes** — 2 via `write_hdu_list`, **14 in
PyAutoGalaxy/PyAutoLens calling `hdu_list.writeto` directly** (neither repo
imports `write_hdu_list`), 4 via PyAutoFit's `paths.save_fits`
(`directory.py:131`, confirmed to `writeto` the passed list as-is). All 18 build
through `hdu_list_for_output_from`. The stamp went in BOTH that and
`write_hdu_list`. Stamping only `output_to_fits` would have missed 16 of 18.

Note the first-pass framing was ALSO wrong in the other direction: the
interferometer *simulator* does use `output_to_fits` (separate-file arm,
`simulator.py:166`), so the issue's proposal would still have caught the
motivating case. The hole is elsewhere and larger.

**ADVERSARIAL REVIEW CAUGHT A DATA-LOSS REGRESSION IN THE FIRST CUT.** The
question no research lane asked: *is the proposition the stamp records the same
one `should_simulate` acts on?* It is not. The stamp records "the env var was
set in the writing process"; the predicate read it as "this data is capped,
therefore disposable". The library already makes those diverge —
`Kernel2D.from_gaussian` passes `respect_small_datasets=False`
(`convolver.py:729`), `Interferometer.from_fits` never caps, and anyone
converting real telescope data in a shell exporting `PYAUTO_SMALL_DATASETS=1`
(the documented harness default) stamps `T` on full-resolution data.

REPRODUCED: a 300x300 image written under the cap, read in a full run, was
DELETED — and the #471 shape heuristic had explicitly REFUSED to delete it. The
first cut was a strict WEAKENING of the safety property #471 established, not a
residual risk. Fixed by corroborating a destructive `T` against the data:
every capped 2D image is rewritten to exactly (16,16), so `T` on an image larger
than the cap in BOTH axes is a contradiction, resolved toward keep.

**TRAPS**
- BOTH axes, never either. Interferometer `data.fits` is `(n_visibilities, 2)` —
  108384x2 for committed sdp81 — so an "either axis" guard would refuse to delete
  the one family the stamp exists for.
- Only a genuine FITS boolean counts. `bool("F")` is `True` in Python, so
  coercing a hand-edited or third-party string card would invert the regime and
  hand a `True` to `shutil.rmtree`.
- The key must stay <= 8 chars. A 9-char keyword is silently promoted to
  HIERARCH by astropy rather than raising, and `header.get()` by the short name
  then returns None — a silent un-fix, not a loud failure. Pinned by test.
- Absence must never mean "full". Every pre-stamp dataset on disk is absent.
- The shape fallback is NOT throwaway work and must stay exercised, or every
  legacy capped dataset loses its protection.
- Committed FITS fixtures became regime-DEPENDENT: the suites write into 14
  tracked paths, so running under the harness default left a dirty tree. Fixed
  with one autouse conftest fixture per repo, not by rewriting 14 tests.

**Scope corrections to the issue text, both verified**
- Point-source datasets are NOT JSON-only. They write a top-level `data.fits`
  and are covered. Only weak lensing is FITS-free.
- `dataset/weak/simple` is regime-INVARIANT (`via_tracer_from` reads no env var),
  so there is no bug there to fix at all.
- Read side covers ~228 of 253 `should_simulate` call sites. The ~23 misses
  (datacube `channel_XXX/`, multi_dataset `{waveband}_data.fits`, sample
  `dataset_N/`, weak lensing) all fail SAFE to keep. Widening a destructive
  predicate's match was deliberately left as its own change.

**Risk surface was smaller than the prompt feared.** No hash/golden-file/checksum
pin over any `.fits` in the stack. Every header consumer indexes named keys;
nothing iterates or `**kwargs`-expands, so mask/geometry reconstruction cannot be
perturbed. Card is byte-size neutral in practice (5760 -> 5760 B; a header block
holds 36 cards, real headers carry ~10).

**Follow-ups filed**
- `draft/bug/pyautolens/point_source_json_datasets_record_no_regime.md` — the
  deferred JSON decision, scoped to point-source only (NOT "JSON datasets"), with
  both expiring justifications recorded as explicit re-check triggers:
  PyAutoLens#480 keeps `point_source/multiple_sources` in `no_run.yaml`, and
  `weak/simple`'s invariance depends on it using `via_tracer_from`. Also names
  `point_datasets.csv` (`output_to_csv`), a third representation no stamp reaches.
- UNFILED: the capped branch of `should_simulate` still rmtrees unconditionally
  and ignores the stamp it now has, so every smoke run re-simulates everything.
  Pre-existing; `if stamp is not True:` is now a cheap fix.
- UNFILED hygiene: `autogalaxy/util/plot_utils.py` and
  `autogalaxy/plot/plot_utils.py` are byte-identical duplicates; every
  `header_dict` card on disk carries the literal comment `['']` because
  `hdu_list_for_output_from` passes `[""]` as the comment.

**Method note.** Deep research (6 agents) established the funnel inventory but
every lane asked the same question and missed the semantic gap. The completeness
critic — asking what NOBODY asked — found the data-loss bug. Fable's 24-agent
adversarial pass then independently reproduced it and found the fixture
regression, with 13 of 18 findings correctly refuted. Two independent reviewers
converging on the same failure mode is what made the guard trustworthy.

## Original prompt

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
