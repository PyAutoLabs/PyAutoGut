# MGE-cell lane death: is the parametric MGE likelihood only measure-zero singular?

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
- PyAutoFit
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

## Phasing (one prompt = one task = one PR)

Only **step 1 is issued from this prompt** — reproduce the rate at production
budget on GPU across seeds, with the control, and write up the number. That is
one task and one autolens_profiling PR.

Steps 2 and 3 are gated on step 1's result and are spun off as their own prompts
when it lands: if the rate comes back near zero, step 2 never happens and the
task closes as "the docstring was right, the reported 62% was a
reduced-budget/CPU artefact". Do not open all three as one PR.

## The claim under test

The `resurrect` docstring in
`@PyAutoFit/autofit/non_linear/search/mle/multi_start_gradient/search.py`
characterises the parametric MGE-class cell as having only a **measure-zero
singularity** — lane death should therefore be rare and incidental, not a
structural property of the likelihood surface.

The human reports a first run of the newly shipped value-NaN / gradient-NaN
lane-step counters (PyAutoFit#1472 → #1473, `n_value_nan_lane_steps` /
`n_grad_nan_lane_steps`) on the `imaging/mge` profiling cell that contradicts
this: **~62% of lane-steps died to value-NaN, and the population fell to alive
2/16.** The same run is reported to have cleared the `ell_comps` plateau as a
suspect for that cell, and to have carried a positive control validating the
zero.

**These figures are reported, not yet reproduced, and are not present in the
PyAutoMind record** — see "Provenance gap" below. Reproducing them is step 1 of
this task, not an assumption of it.

If the 62% holds at production budget, it is not a measurement curiosity: it
means the MGE cell's likelihood is undefined over a *set of positive measure*
along the descent path, every benchmark number produced on that cell was
produced by a search running on 2 of 16 lanes, and the resurrection policy
deliberately deferred in #1472 ("decide AFTER the counters show how often frozen
lanes actually occur") now has its answer.

## Provenance gap — resolve before or during step 1

The launch context cites a completion record `complete/2026/08/frozen-lane-counter.md`
and PRs **PyAutoFit#1475 / PyAutoGalaxy#572**. None of these exist in PyAutoMind
as of `origin/main` @ `1f7cca8`:

- The frozen-lane (gradient-NaN) counter shipped as
  `complete/2026/08/multistart-nan-step-diagnostics.md` — issue PyAutoFit#1472,
  library PR **PyAutoFit#1473** (merged `fbfcece3`), profiling PR
  **autolens_profiling#127** (merged `a34d6191`). There is **no PyAutoGalaxy leg**:
  the change was confined to `search.py` and `autofit/text/text_util.py`.
- No record anywhere in the repo mentions a 62% rate, `alive 2/16`, an
  `ell_comps` plateau clearance for the MGE cell, or a positive control for this
  run. The most recent counter work
  (`complete/2026/08/multistart-gradient-resume-fom-sanity-check.md`, updated
  2026-08-15) is **resume-accumulation** verification on a clean Gaussian fit
  with synthetic NaN traps — not a production MGE run.

`autolens_profiling` was checked too, and does not have the run either. Its
`main` is at `a34d6191` — exactly the #127 merge the Mind record cites, so
nothing has landed since. The only MGE NaN-accounting artefact in the repo is
`results/searches/multi_start_nan_accounting/local_cpu.json`, and that is the
**overhead benchmark**, not a lane-death rate: `imaging`/`mge`/`hst`,
`n_starts: 16`, `n_steps: 5`, `reps: 3` on `local_cpu`, whose only verdict is
`"fused accounting costs 4.1us on a 1.027s step = 0.00039% of run time"`. It
reports no NaN counts and no alive-lane trajectory. No remote branch in
autolens_profiling carries lane-death work.

So the 62% run exists in no pushed artefact in either repo. Either it was run in
a session whose results were never pushed, or the identifiers and figures are
misremembered. Recover the actual run artefacts (`search.summary`,
`samples_info`, the `results/searches/**` JSON) before treating 62% as a
baseline; if they cannot be recovered, step 1 *establishes* the number rather
than reproducing it.

Note also that the 5-step, 3-rep budget of the one real artefact is far too
short to say anything about a rate that accumulates along a descent path — which
is consistent with the launch context's own warning not to let a reduced-budget
CPU number generalise.

## Step 1 — reproduce at production budget on GPU (do this first)

The reported 62% is a reduced-budget CPU number. Do not let it generalise
untested.

- Run `imaging/mge` at **production** `SEARCHES_N_STARTS` / `SEARCHES_N_STEPS`
  on GPU, across **at least two seeds**, and record
  `n_value_nan_lane_steps`, `n_grad_nan_lane_steps`, `n_resurrections` and the
  alive-lane trajectory for each.
- Report the counters as **rates** normalised by `n_starts * total_steps` —
  raw counts are not comparable across budgets (this is the normalisation
  `search.summary` already applies).
- Include the reduced-budget CPU configuration as one arm, so the
  budget-dependence of the rate is measured rather than assumed. If the rate is
  strongly budget-dependent, that is itself the finding.
- Positive control: an analysis with a known-zero NaN rate must report zero
  through the same path, on the same hardware. `_broad_starts` rejects
  non-finite draws, so lanes always *begin* healthy — a control that only proves
  the counter can read zero is weak; pair it with a trap **on the descent path**
  (the `where`/`sqrt` pattern in the `Fitness.call` docstring gives a finite
  value with a NaN gradient) so the counters are proven to fire on the same run
  shape.

## Step 2 — locate the deaths on the likelihood surface

Only if step 1 confirms a materially non-zero rate.

- Which parameters are the dying lanes in when the value goes non-finite?
  The counters are per-step aggregates; getting from a rate to a *cause* needs
  the lane parameter vectors at the death step.
- Distinguish the candidate mechanisms: MGE sigma range degeneracy (cf.
  `complete/2026/08/mge-sigma-min-workspace-sweep.md` and
  `complete/2026/05/mge-cse-fallback.md`), NNLS solver failure on the JAX path,
  underflow in the likelihood normalisation, and genuine model-space
  singularities. These have different fixes and only one of them is
  "measure-zero".
- The `ell_comps` plateau is reported as already cleared for this cell; confirm
  that from the run artefacts rather than inheriting it
  (cf. `complete/2026/08/circular-ell-comps-image-gradient.md`,
  `complete/2026/08/resolve-sersic-ell-comps-gradient.md`).

## Step 3 — what the answer changes

- **The docstring.** If the singularity is not measure-zero, the `resurrect`
  docstring is wrong and misleads every future reader about which cells are safe.
- **The resurrection policy.** #1472 deferred the decision to make `resurrect`
  trigger on non-finite *gradients* until the counters spoke. A 62% value-NaN
  rate with alive 2/16 is a much stronger signal than that deferral anticipated —
  but note that value-NaN is *already* today's resurrection trigger, so a high
  value-NaN rate means resurrection is firing and failing to keep the population
  alive, which is a different problem from the frozen-lane one and needs stating
  separately.
- **Every MGE benchmark number to date.** If the population is routinely 2/16,
  the wsdev #117/#125 comparisons and the sampler benchmark rows are measuring a
  crippled search. Scope the re-run implications; do not silently invalidate.

Deliberately out of scope: changing resurrection behaviour. This prompt is
research — it produces the evidence and a recommendation. A behaviour change is
a separate feature/bug prompt so the benchmark comparability argument from #1472
gets made explicitly rather than by accident.

## Environment (human-supplied; cost real time last session)

- **Python 3.12+** required (autonerves).
- **`jaxnnls` is a required extra** for the JAX NNLS solver path — not pulled in
  by default.
- Install `autolens` with **`--no-deps`** when running editable local
  autofit/autogalaxy, or the released wheels clobber them.
- **`build_for_cell` writes into `dataset/`** — it rewrites the HST FITS, adds
  `positions.json`, and emits `results/simulators/*`. Not read-only.
- Cell scripts honour `SEARCHES_N_STARTS`, `SEARCHES_N_STEPS`,
  `SEARCHES_BATCH_SIZE`, `SEARCHES_DISABLE_VIZ`.
- `imaging/mge` runs on **CPU in ~6 min at 16x150**. The **pixelized mesh cells
  do not** — two attempts timed out emitting zero steps. It is **JIT compile,
  not memory** (`batch_size=1` clears the OOM). Those need the GPU.
- **Shrinking the source mesh is the wrong cost lever** — the image-plane grid
  at `mask_radius 3.5` dominates, not the mesh.
- On A100, set `jax_enable_x64` **explicitly** — it is not inherited under
  `sbatch`, and float32 would understate the quantity under test (carried
  forward from the #1472 "Still owed" note).

## Prior art to read first

- `complete/2026/08/multistart-nan-step-diagnostics.md` — the counters, what
  they mean, the normalisation, and the `_broad_starts` trap.
- `complete/2026/08/multistart-gradient-resume-fom-sanity-check.md` — descent-path
  NaN injection technique and the equality-vs-`>=` assertion lesson.
- `complete/2026/07/pixelized-multistart-prodigy-cpu.md` and the DelaunayNN
  free-AdaptSplit open question in `active.md` (109 resurrections, NaN death vs
  over-regularized-floor death) — the same question, different cell.

<!-- filed by /start_dev on 2026-08-15 from human launch context; the 62% /
alive-2/16 figures and the frozen-lane-counter.md / #1475 / #572 identifiers are
the human's report and are NOT corroborated by the PyAutoMind record -->
