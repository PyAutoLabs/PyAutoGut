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

The claim is verbatim, at `search.py:119` under the `resurrect` parameter:

> Default ``False`` — the parametric (MGE-class) cell has only the measure-zero
> singularity, so the ``apply_if_finite`` guard suffices and behaviour/results
> are unchanged.

The human reports that the first run of the **trapped-lane counter** — shipped
today as PyAutoFit#1475 (`_constrained_lane_count`, merged `004f798`) with its
PyAutoGalaxy leg #572 (`EllProfile.__model_constraint__`, merged `695b27c`) —
contradicts this on the `imaging/mge` cell: **~62% of lane-steps died to
value-NaN, and the population fell to alive 2/16.**

The same run reportedly **cleared the `ell_comps` plateau as a suspect** for
this cell, which is coherent with what #1475/#572 do: #572 declares the
`ell_comps` saturation constraint, #1475 counts lanes sitting outside it, and a
near-zero `constrained N/16` reading on the MGE cell exonerates the plateau. The
"positive control validating the zero" is the load-bearing part of that — a zero
reading only means something if the detector is proven able to fire, which is
exactly the point of #1475's note that a component-wise gradient test *"caught 0
of 17 genuinely trapped lanes in a JAX reproduction"* while the declared-
constraint detector caught them.

So the plateau is cleared and the value-NaN rate is the finding. **The 62% and
alive 2/16 figures themselves are reported from a local run log and are not in
any pushed artefact** — see "Provenance gap" below. Reproducing them is step 1
of this task, not an assumption of it.

If the 62% holds at production budget, it is not a measurement curiosity: it
means the MGE cell's likelihood is undefined over a *set of positive measure*
along the descent path, every benchmark number produced on that cell was
produced by a search running on 2 of 16 lanes, and the resurrection policy
deliberately deferred in #1472 ("decide AFTER the counters show how often frozen
lanes actually occur") now has its answer.

## Three counters, not one — keep them straight

The lane accounting shipped in two waves, and the second is a day old. Anything
written about "the counter" needs to say which:

| Counter | Failure mode | Shipped as |
|---|---|---|
| `n_value_nan_lane_steps` | likelihood **undefined** (today's `resurrect` trigger) | PyAutoFit#1472 → **#1473** (`fbfcece`) |
| `n_grad_nan_lane_steps` | likelihood defined but **not differentiable** — the frozen zombie lane | same PR |
| `_constrained_lane_count` | finite **and** differentiable, but **trapped** on a saturating plateau with no restoring force | PyAutoFit **#1475** (`004f798`) + PyAutoGalaxy **#572** (`695b27c`) |

All three are disjoint by construction ("one lane, one bucket") and all three are
**measurement only** — none gates a redraw or changes stepping. The reported 62%
is in the **first** bucket, which is the one whose resurrection policy already
exists. That matters for step 3.

## Provenance gap — resolve before or during step 1

The PRs are real and merged; the **write-up and the run artefacts are not
pushed**.

- `complete/2026/08/frozen-lane-counter.md` does not exist. PyAutoMind
  `origin/main` is at `1f7cca8`, which predates both #1475 and #572 (merged
  2026-08-15 ~15:52 UTC), so no completion record for that wave has been written
  yet. The nearest existing records are
  `complete/2026/08/multistart-nan-step-diagnostics.md` (the #1473 wave) and
  `complete/2026/08/multistart-gradient-resume-fom-sanity-check.md` (resume
  accumulation, verified on a clean Gaussian fit with synthetic NaN traps — not
  a production MGE run).
- No pushed artefact anywhere carries the 62% or the `alive 2/16`.
  `autolens_profiling` `main` is at `a34d6191` (the #127 merge) with nothing
  since and no lane-death branch; PyAutoFit has no such branch either. The only
  MGE NaN artefact in the profiling repo is
  `results/searches/multi_start_nan_accounting/local_cpu.json`, and that is the
  **overhead benchmark** — `imaging`/`mge`/`hst`, `n_starts: 16`, `n_steps: 5`,
  `reps: 3`, `local_cpu`, verdict `"fused accounting costs 4.1us on a 1.027s
  step"`. It reports no NaN counts and no alive-lane trajectory, and at 5 steps
  it could not resolve a rate that accumulates along a descent path anyway.

So the figures live in a local run log. **Recover and commit that log (or the
`search.summary` / `samples_info` / `results/searches/**` JSON behind it) as the
first act of step 1** — otherwise the reproduction has nothing to be graded
against, and a disagreement between the GPU run and the remembered number will
be unresolvable.

## Step 1 — reproduce at production budget on GPU (do this first)

The reported 62% is a reduced-budget CPU number. Do not let it generalise
untested.

- Run `imaging/mge` at **production** `SEARCHES_N_STARTS` / `SEARCHES_N_STEPS`
  on GPU, across **at least two seeds**, and record
  `n_value_nan_lane_steps`, `n_grad_nan_lane_steps`, the `_constrained_lane_count`
  reading, `n_resurrections`, and the `alive N/16` + `constrained N/16`
  trajectory for each. Record **all three** counters even though only the first
  is expected to be large — a step-3 argument that "the plateau is cleared"
  needs the constrained column present and near zero on the production run, not
  inherited from the reduced-budget one.
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
- The `ell_comps` plateau is reported as already cleared for this cell by the
  #1475/#572 constrained counter; confirm that from the production run artefacts
  rather than inheriting it (cf.
  `complete/2026/08/circular-ell-comps-image-gradient.md`,
  `complete/2026/08/resolve-sersic-ell-comps-gradient.md`).
- **A cleared plateau does not clear the constraint mechanism generally.** #572
  declares `__model_constraint__` on `EllProfile` only. If a *different*
  saturating clamp is in play on this cell, the constrained counter reads zero
  because nothing declared it — not because nothing is trapped. Enumerate which
  classes in the MGE cell's model declare a constraint before reading a zero as
  an all-clear.

## Step 3 — what the answer changes

- **The docstring.** If the singularity is not measure-zero, the `resurrect`
  docstring is wrong and misleads every future reader about which cells are safe.
- **The `resurrect` default, not the resurrection trigger.** This is the
  distinction to get right. #1472 deferred whether `resurrect` should *also*
  trigger on non-finite gradients. But a 62% **value**-NaN rate says nothing
  about that deferral — value-NaN is already the trigger. What it says is that
  the MGE cell's `resurrect=False` **default** is wrong: the docstring justifies
  that default by asserting the cell has only a measure-zero singularity, and if
  62% holds, the justification is false and the cell has been running with
  resurrection off through a landscape that needs it. Recommend on the default;
  leave the gradient-trigger question where #1472 left it.
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
- PyAutoFit `004f798` and PyAutoGalaxy `695b27c` themselves — the constrained
  counter and the `EllProfile` constraint have no completion record yet, so the
  commit messages are currently the only write-up.

<!-- filed by /start_dev on 2026-08-15 from human launch context. PyAutoFit#1475
(004f798) and PyAutoGalaxy#572 (695b27c) verified merged; the resurrect
measure-zero claim verified verbatim at search.py:119. The 62% / alive-2/16
figures are the human's report from a local run log and appear in no pushed
artefact in PyAutoMind, autolens_profiling or PyAutoFit. -->
