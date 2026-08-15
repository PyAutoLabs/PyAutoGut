- library-prs: https://github.com/PyAutoLabs/PyAutoFit/pull/1475, https://github.com/PyAutoLabs/PyAutoGalaxy/pull/572
- merge-commits: PyAutoFit `004f798a89e621ab7320b46fe0494201720260fd`; PyAutoGalaxy `695b27c545fa1328a34366d56e579b1bbc55f95e`
- issue: none — filed straight from investigation via `/intake`, never issued
- summary: Added a third disjoint lane counter to the multi-start gradient search
  for lanes that are finite *and* differentiable but sit on a saturating plateau
  with no gradient along the saturated direction, so they can never leave. Both
  existing counters are blind to them and the flat figure of merit reads as
  convergence. Detection reads a new class-declared `__model_constraint__`
  protocol; `EllProfile` declares the `ell_comps` saturation region, reaching
  every elliptical light and mass profile through the one site where `ell_comps`
  is assigned.
- validation: PyAutoFit 1745 passed +15 new, CI green on 3.12/3.13/docs;
  PyAutoGalaxy 1101 passed 1 skipped +12 new, CI green on 3.12/3.13/docs. Five
  PyAutoFit failures are pre-existing, verified identical on a stashed clean tree
  (missing `astropy`; a nautilus pool test).
- release: not performed; both merged PRs remain in the pending-release queue.

## The finding that shaped the design

A component-wise zero-gradient test — the obvious detector, and the one this
task was originally filed to build — **does not work**, and a JAX reproduction
proved it before any code was written. The clamp kills only the *radial*
derivative; the angle still comes from an unclamped `arctan2`, so in general
position both `ell_comps` components carry a large non-zero gradient while their
radial projection is zero only to floating-point residue. Scored against 17
genuinely trapped lanes:

| candidate detector | caught |
|---|---:|
| gradient component exactly zero | 0/17 |
| all components exactly zero | 0/17 |
| radial derivative exactly zero | 6/17 |
| per-parameter prior-limit escape | 17/17 |
| declared model constraint | 17/17 + corner region |

Prior-limit escape scores well only because Prodigy overshoots grossly (trapped
magnitudes ran 1.62 to 6.78). It provably cannot see the corner region — both
components inside `(-1, 1)` with magnitude above 1, the whole `4 - pi` area
between the unit disc and the unit square.

## Why the exception could not be reused

`validate_ell_comps` already owns the geometry but signals by raising, which
needs a concrete boolean. A `raise` on a traced condition gives
`TracerBoolConversionError`, which is why `validate.py:153-154` returns early for
non-concrete scalars — that escape hatch is load-bearing, not an oversight.
`jax.experimental.checkify` does survive `vmap` + `value_and_grad` with finite
values and gradients, but collapses a batch to one abort-shaped error, so it
cannot serve a per-lane counter that must let surviving lanes finish. The
predicate returned as a traced value gives 32 independent verdicts with no
exception machinery.

## Two thresholds, and drift that already existed

The clamp saturates at `0.999` (`convert.py`); the guard rejects at `1.0`
(`validate.py`). They answer different questions — where the *gradient* dies
versus where the *geometry* stops meaning anything — and the annulus between
them is reachable: at magnitude 0.9995 the radial derivative is already exactly
zero while `validate_ell_comps` still calls the point valid. The constraint is
therefore keyed to the clamp, not the guard.

The clamp was a bare literal at **three** sites — `convert.py`'s JAX and NumPy
branches and the Sersic Cartesian eccentric-radius path from PyAutoGalaxy#571 —
with the guard's `1.0` in a fourth file and nothing relating them.
`ELL_COMPS_MAGNITUDE_CLAMP` now states it once. Value unchanged at every site.

## Architecture

The protocol is **assertions with two changes**: declared on the class rather
than attached per model instance, and evaluated as a traced non-negative measure
rather than raised. It attaches through `Model.__init__`, which is already a
class-introspection site (`gather_namespaces`, `get_type_hints`, per-argument
prior resolution) — not through `__default_fields__`, which is a narrow
`ConfigException` escape hatch with two usages and is *not* a constraint
registry. No user-facing composition call changes.

Nothing flows *up* through the likelihood: the constraint is a pure function of
the parameter vector, evaluated beside `fitness.call`, which is untouched. It
rides the fused `value_and_grad` as a fourth output on a device→host sync that
already happens. Cost is a flat +20 HLO lines at every scale tested (grid
31→256, starts 32→128) — fixed, not proportional to likelihood cost.

## Evidence the counter fires

End to end on a real `ag.mp.Isothermal` under `af.MultiStartProdigy`, the
constraint arriving purely through inheritance:

```
prodigy step 300/300 | best log_post -431.7808 | alive 22/32 | constrained 6/32
n_value_nan_lane_steps      2344
n_grad_nan_lane_steps          0
n_constrained_lane_steps    1057
best lane einstein_radius = 1.5968   (truth 1.6)
```

Severity is honest: the trap wastes start budget rather than corrupting results
— surviving lanes still recovered the truth. It becomes a correctness risk only
where `n_starts` is small or the good basin is rare, which is the pixelized-mesh
regime.

## Traps

- **The original question is still unanswered.** Whether the *real* Prodigy mesh
  or MGE runs entered the region cannot be determined retrospectively:
  `autolens_profiling` stores summary records with no per-start traces, and the
  Prodigy mesh cells (`scripts/imaging/searches/multi_start_prodigy/`) were never
  persisted to `results/searches/multi_start_prodigy/` at all, which holds only
  `point_source/` and `cluster/`. Re-running those cells with this counter is the
  follow-up that answers it.
- **Spherical profiles inherit the constraint.** `IsothermalSph` subclasses
  `Isothermal`, so it carries the declaration with `ell_comps` pinned at `(0, 0)`
  — always satisfied, a few wasted ops. A test asserting the opposite failed and
  was corrected; the real behaviour is now pinned.
- **A grid with a pixel at the exact centre masks this hazard entirely.** The
  first reproduction returned NaN gradients everywhere from `sqrt(0)` — the
  *separate* r=0 non-finite-gradient hazard — hiding the plateau under
  investigation. Use an off-centre grid, as the hazard scans do.
- **`black` is not enforced on the PyAutoFit files touched.** It wants to
  reformat all three at `main` too, so running it would bury the change in
  unrelated churn. Left alone deliberately.

## What the penalty term inherits

The counter reads only `violation > 0.0`, a sign test, so it is scale-free and
carries no lambda. That leaves two properties of the measure untested by anything
shipped, both landing on the penalty task:

- **Units.** The measure is in the constraint's own units (ellipticity
  magnitude); the figure of merit is in log-likelihood. That mismatch is what a
  lambda has to absorb, and why a constant cannot work across cells whose scales
  differ by orders of magnitude.
- **The reduction.** `model_constraint_from_vector` combines components with
  `maximum` — correct for counting, wrong for a penalty, where two constraints in
  different units would let whichever is numerically larger silently dominate.
  Per-constraint lambdas or normalised measures, not one max.

Also unresolved for the penalty: it must be moved *inside* the differentiated
call (today the violation is computed after `value_and_grad`, so it has no
gradient effect), and kept out of the reported likelihood or made invertible in
`log_likelihood_from`.

## Original prompt

# Count frozen lanes in the multi-start gradient search

Type: feature
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

@PyAutoFit

Add a third lane counter to `AbstractMultiStartGradient._nan_lane_counts`
(`autofit/non_linear/search/mle/multi_start_gradient/search.py:219-255`).

It counts two disjoint failure modes today — **value-NaN** (likelihood
undefined; the death `resurrect` triggers on) and **gradient-NaN** (defined but
not differentiable; `apply_if_finite` zeroes the update). A third mode escapes
both: a lane whose value and gradient are both finite, but which sits on a
saturating plateau with **no gradient along the saturated direction**, so it can
never leave.

## Why it matters

The reference case is the ellipticity magnitude clamp `jax.lax.min(fac, 0.999)`
in PyAutoGalaxy's `convert.py:71-77`. Past `|ell_comps| >= 0.999` the axis ratio
pins at `q = 5.0025e-4`, so the likelihood is exactly constant along the radial
direction — measured identical to 10 significant figures at `|ell_comps|` of
1.0, 1.2 and 5.0. For a multi-start gradient search that is an absorbing trap:

- Starts are safe: `_broad_starts` draws in the unit cube at `(0.15, 0.85)`,
  capping start magnitude near 0.44 under the default `TruncatedGaussian(0, 0.3)`.
  Measured start range in the toy run was 0.087 to 0.362.
- But `optax.apply_updates(params, updates)` (`search.py:743`) steps the physical
  vector with no re-projection into prior limits, so trajectories walk in — 17 of
  32 lanes did, reaching `|ell_comps|` as high as 6.78.
- Once inside there is no radial restoring force, so the lane cannot come back.
- `apply_if_finite` and `resurrect` are both no-ops here — value and gradient are
  finite.
- `multi_start_prodigy_autoconv` runs `check_for_convergence=True`, so trapped
  lanes flatten the figure of merit and can false-trigger early stopping.

A trapped lane is therefore indistinguishable from a converged one in the
figure-of-merit trace, which is exactly the hazard `_nan_lane_counts` was
written to expose for the gradient-NaN case.

## Scope

Instrumentation only. Add the count alongside the existing two, accumulate it
across steps, record it into `search_internal`, restore it on resume, and report
it on the progress line — mirroring `n_value_nan_lane_steps` and
`n_grad_nan_lane_steps` exactly. Keep it pure-NumPy and free of search state so
it stays directly testable like its two siblings.

The search must produce identical results with the counter present. Do not add a
penalty term, and do not touch `resurrect`, `apply_if_finite`, the convergence
check, stepping behaviour, or the clamp itself.

## Detector: use the saturation predicate, not a zero-gradient test

A JAX toy reproduction (32 starts, 400 Prodigy steps, PyAutoGalaxy's clamp
verbatim, `apply_if_finite` + unbounded `apply_updates`, truth at
`|ell_comps| = 0.90`) settled the detector question empirically. **Do not
implement a component-wise zero-gradient test — it does not work.**

Measured on the 17 of 32 lanes that ended on the plateau:

| candidate detector | caught | false pos |
|---|---:|---:|
| gradient component exactly zero | **0/17** | 0 |
| all gradient components exactly zero | **0/17** | 0 |
| radial derivative exactly zero | 6/17 | 0 |
| **per-parameter prior-limit escape** | **17/17** | **0** |

The reason is that the clamp kills only the *radial* derivative. The angle still
comes from an unclamped `arctan2`, so in general position both `ell_comps`
components carry a large non-zero gradient while their radial projection is zero
— at `ell_comps = (0.867, 0.593)` the components are `+2.7e4` and `-3.9e4` while
the radial projection is `-3.4e-12`. Only on the measure-zero axis where one
component is exactly zero does a component itself read zero. Floating-point
residue from the rotation is also why the radial test scores 6/17 rather than
17/17: the projection is ~1e-12, not an exact zero.

### Reuse the guard's predicate, not its exception

`validate_ell_comps` already owns the authoritative constraint, but it cannot
raise under a trace and deliberately does not try — `validate.py:153-154` returns
early for non-concrete scalars. That escape hatch is load-bearing: a plain
`raise` on a traced condition gives `TracerBoolConversionError`, so without it
every jitted likelihood would crash rather than sample.

Measured on the three candidate mechanisms:

| mechanism | works under `vmap` + `grad`? | shape |
|---|---|---|
| plain `raise` | no — `TracerBoolConversionError` | — |
| `jax.experimental.checkify` | yes, values/grads stay finite | **one error per batch**, abort-shaped |
| **guard predicate as a traced boolean** | yes | **per-lane verdict** |

`checkify` is the genuine JAX exception mechanism and it does survive
`vmap`+`value_and_grad`, but it collapses a batch to a single error and is built
to abort. That is the wrong shape here: the run must continue so the surviving
lanes finish, and the counter needs 32 independent verdicts, not one.

The predicate as a traced boolean gives exactly that, returned alongside the FoM
— no exception machinery at all. Scored against the 17 real trapped lanes plus
three synthetic corner-region lanes (both components inside `(-1, 1)`, magnitude
above 1):

| detector | caught | missed |
|---|---:|---:|
| per-parameter prior-limit escape | 17/20 | 3 |
| **saturation predicate `|ell_comps| >= 0.999`** | **20/20** | **0** |

**Use the clamp's threshold (0.999), not the guard's (1.0).** They differ, and
the gap is reachable: at `|ell_comps| = 0.9995` and `0.99999` the radial
derivative is already exactly zero while `validate_ell_comps` still calls the
point valid. A detector keyed to the guard's `magnitude_squared >= 1.0` misses
that annulus; one keyed to the clamp does not.

This supersedes the prior-limit-escape recommendation below, which is provably
incomplete — the corner region it misses is the whole `4 - pi` area between the
unit disc and the unit square.

### How it attaches (no new composition call)

The model-composition API does not gain a user-facing call — `af.Model(al.mp.Isothermal)`
is unchanged.

What makes that possible is that `Model.__init__` is **already** a class
introspection site: it runs `gather_namespaces(cls)` and
`typing.get_type_hints(cls.__init__, ...)`, walks the constructor signature and
resolves a prior per argument. Per-class knowledge is already gathered there, so
this is one more lookup in an existing mechanism, not a new one.

Do **not** build this on `__default_fields__`. That is a narrow escape hatch —
`prior_model.py:200` consults it only when `make_prior` returns a
`ConfigException`, and it has exactly two usages (`messages/normal.py:412`,
`truncated_normal.py:485`, both `("log_norm", "id_")`). It marks "this argument
is not a model parameter"; it is not a constraint registry.

The real relative is **`add_assertion`** (`abstract.py:441`), PyAutoFit's
existing constraint concept. It is wrong here on exactly two counts: it attaches
per *model instance* rather than per class (so every elliptical profile would
need the user to remember it), and it raises `FitException`, which is numpy-only
for the reasons above.

So frame the work as **assertions with two changes** — class-declared rather than
per-model, and a traced predicate rather than a raise — not as a new validity
subsystem. The two should likely share a home rather than sit as unrelated
features.

Placement is clean because `validate_ell_comps` has exactly **one** call site,
`geometry_profiles.py:237` in `EllProfile.__init__` — the single base every
elliptical light and mass profile inherits. The declaration goes on that class,
beside the existing call.

Do **not** let this become a second statement of the constraint. Extract the
predicate out of `validate_ell_comps` as a pure `xp`-generic function; leave
`validate_ell_comps` raising on concrete scalars as it does today, now calling
that predicate; point the class-level declaration at the same function.

Note that the drift this guards against **already exists**: the clamp is `0.999`
in `convert.py:71-77`, the guard is `1.0` in `validate.py:158`, in different
files with nothing relating them. That gap is precisely the reachable annulus
where the radial gradient is already dead while the guard still calls the point
valid. The two thresholds answer different questions and both should survive —
but their relationship should be stated in one place, which this work is the
opportunity to do.

### What it costs, and what it cannot see

Nothing flows *up* through the likelihood. The saturation predicate is a pure
function of the parameter vector, so it is evaluated at the top beside the
likelihood, which is left untouched — measured with the toy's
`log_likelihood` imported unmodified, gradients bit-identical (`atol=0`).

Cost on the toy: +23 HLO lines (700 -> 723, +3.3%). Wall-clock overhead measured
at +40 us on a ~1090 us call, which is **below the noise band** on a shared CPU
(interleaved burst spreads overlapped) — treat it as an upper bound, and expect
it to be proportionally smaller against a real pixelized likelihood.

The ceiling is worth stating before anyone assumes one mechanism covers the
whole hazard index: this works *only* for parameter-only properties. The tier-2
likelihood hazards — which basis components the NNLS active set pinned at zero,
how a conditioning floor bit against real flux — are genuine likelihood-internal
state, are not recoverable from the parameter vector, and would need real upward
plumbing.

### Scope consequence

Asking the model "is this instance saturated?" is a **validity channel** between
PyAutoFit and the profile libraries, not something PyAutoFit can answer alone.
It is also the same hook the later penalty term needs, so building it once serves
both. If this task stays PyAutoFit-only it must fall back to prior-limit escape
and accept the corner-region miss; see the open question at the end.

### Superseded: prior-limit escape

Detect the **cause** — a lane that has left its priors' support, which is
possible at all only because `apply_updates` steps the physical vector with no
re-projection. That is fully generic (every `Prior` already carries
`lower_limit`/`upper_limit`), needs no model semantics, no gradient inspection,
and no tolerance.

Record its limit honestly in the docstring: it is a proxy for the cause, not the
effect. It caught every trapped lane here because Prodigy overshoots grossly
(trapped `|ell_comps|` ran 1.62 to 6.78, max component 6.45), not because it is
complete. A lane in the corner region — both components inside `(-1, 1)` but
magnitude above 1, which is the whole of the `4 - pi` area between the unit disc
and the unit square — is beyond the clamp yet inside every per-parameter limit,
and this detector will miss it.

## Severity, for prioritisation

The same run shows the trap **wastes budget rather than corrupting results**:
17/32 lanes died on the plateau, yet the surviving lanes still recovered the
truth (best lane `|ell_comps| = 0.9001`, logL −427.5 against a truth logL of
−430.4). Multi-start redundancy absorbs it. It becomes a correctness risk only
when `n_starts` is small or the good basin is rare — which is exactly the
pixelized-mesh regime the counter is meant to observe.

## Other decisions

- Keep the buckets disjoint: a lane already counted as value-NaN or gradient-NaN
  must not also count as escaped.
- Do not force a per-step device sync if it costs measurable run time. The
  existing NaN accounting measured 0.0004% of step time; stay in that class.


<!-- formalised by the Intake (Conception) Agent on 2026-08-15 from file:/tmp/claude-0/-home-user/ef0adef1-5fcd-5111-9cdf-bcb1014fc23d/scratchpad/frozen_lane_counter.md -->

## Open question for start_dev

Whether to widen this task to the validity channel (PyAutoFit + PyAutoGalaxy,
complete detector, shared with the later penalty term) or keep it PyAutoFit-only
(prior-limit escape, misses the corner region). Widening changes the header:
`Repos:` gains PyAutoGalaxy and difficulty rises from `medium`. Decide before
issuing, not during.

## What the penalty inherits (shipped counter is unaffected)

The counter uses only `violation > 0.0` — a sign test, so it is scale-free and
no lambda exists anywhere in it. Two properties of the shipped measure are
therefore **untested by anything shipped**, because only its sign is ever read,
and both land on the penalty task:

- **Units.** `max(|ell_comps| - 0.999, 0)` is in units of ellipticity magnitude;
  the figure of merit is in log-likelihood. That mismatch is exactly what a
  lambda has to absorb, and it is why a single constant cannot work across cells
  whose likelihood scales differ by orders of magnitude (point-source ~10s,
  pixelized ~30,000s).
- **The reduction.** `model_constraint_from_vector` combines components with
  `xp.maximum`. Correct for counting — any violation makes the lane constrained
  — but wrong for a penalty: two constraints in different units (ellipticity
  magnitude vs a radius, say) would be reduced by `max`, so whichever is
  numerically larger silently dominates. A penalty likely wants per-constraint
  lambdas, or measures normalised to a common scale, rather than one max.

Neither is a defect in the counter. Both are decisions to make before the
measure is multiplied into the figure of merit.

## Status

The counter shipped: PyAutoFit PR #1475 (branch
`claude/jax-sampling-flat-gradients-ptmqnl`), CI green on 3.12, 3.13 and docs.
1745 tests pass, +15 new. PyAutoGalaxy declares no constraint yet, so the
counter reads zero on real lens models until `EllProfile` opts in — a ~4-line
method at the site that already calls `validate_ell_comps`.
