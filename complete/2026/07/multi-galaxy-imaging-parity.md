`scripts/multi_galaxy/` was materially thinner than `scripts/imaging/` despite being a user's entry point
into the multi-deflector regime. Brought every script to imaging's teaching depth and added the three
missing ones, reusing imaging's prose where it transfers and adapting it throughout to the co-dominant-pair
case.

## What shipped

**autolens_workspace#378** (`77d70f48`), issue #370 closed.

| Script | Before | After | imaging counterpart |
|---|---|---|---|
| `start_here.py` | 347 | 673 | 628 |
| `modeling.py` | 327 | 884 | 716 |
| `fit.py` | 166 | 614 | 435 |
| `likelihood_function.py` | — | 688 | 584 |
| `simulator_sample.py` | — | 343 | 232 |
| `source_science.py` | — | 396 | 258 |
| `simulator.py` | 347 | 441 | 453 |

- `start_here.py` — `__Model__` trimmed to imaging's non-technical register (truncation/dPIE and the EPL
  upgrade path moved down into `modeling.py`); added `__Extra Galaxy Removal__`, the pre-search `__JAX__`
  block, `__Iterations Per Update__`, `__Live Visual Update__`, `__Extra Galaxy Removal GUI__`, an
  imaging-aligned `__Model Your Own Lens__`, and both `__Simulator__` sections plus a `__Sample__` pointer.
- `modeling.py` / `fit.py` — full depth pass against their imaging counterparts.
- Three new scripts ported and adapted; `__Mass/Light Offsets__` removed package-wide.
- `simulator.py` gained a faint extra galaxy + `mask_extra_galaxies.fits` so
  `__Extra Galaxies Noise Scaling__` is demonstrable here as in imaging.

## Two decisions the human made mid-task

**Extra galaxies.** Initially scoped to *omit* the noise-scaling sections because the dataset shipped no
mask. The human overrode: mirror `imaging/simulator.py` instead. That was strictly better and my objection
was wrong — `dataset/multi_galaxy/**` is gitignored, so adding the mask costs no committed binary.

**Shear placement.** Asked for a shear "just like in imaging", then for it "at (0.0, 0.0) not over one
particular galaxy". `al.mp.ExternalShear` takes **only** `gamma_1`/`gamma_2` — **no `centre` argument** — so
"at the system centre" is expressed by giving it its own galaxy:
`al.Galaxy(redshift=0.5, shear=al.mp.ExternalShear(...))`, added to the tracer / as a `shear_galaxy` entry in
the `af.Collection`. Verified `np.allclose`-identical to attaching the shear to `lens_0`, so it is
presentational: the tracer sums every deflection field regardless. `ExternalShear` is a `MassProfile`
subclass, so it also works in the `mass=` slot.

## Sequencing

`worktree_check_conflict` returned 0, but #366 (MultiStartProdigy) held **16 files of uncommitted** edits
including the exact `search = af.Nautilus(...)` block in `multi_galaxy/{start_here,modeling}.py` this task
rewrites. Found by hand-reading `active.md` and diffing the sibling worktree. Human chose to sequence rather
than hand-merge; task parked in `planned.md` with a `blocked-on:` key and resumed once #366 merged. Its
`MultiStartProdigy` swap and `__Multi Start Gradient Optimization__` / `__Posterior__` sections were
preserved, and `__Iterations Per Update__` written against gradient-step semantics.

Two further mid-flight merges: #375 (likelihood_function `__JAX__` → `guides/using_jax.py` pointer) — the new
`multi_galaxy/likelihood_function.py` was written in that shape *before* it landed, then word-aligned to the
landed text — and #376 (point_source extra_galaxies).

## Verification that changed the work

Checked printed numbers, not exit codes. Two claims were wrong before this caught them:

- **Bad-fit residuals go to the arcs, not the perturbed galaxy.** Perturbing only `lens_0`'s mass put
  4230 of 4317 chi²>10 pixels at r>1.0" and just 33 within 0.5" of `lens_0` — the total-deflection-vs-mass-split
  degeneracy. My initial prose asserted the opposite intuition.
- **A magnification comparison was unreconcilable for a reader** (34.4 vs a headline 25.6). Fixed by adding a
  pair+shear row, which lands at 25.600 against the headline 25.588.

Also verified: hand-computed `figure_of_merit` == `FitImaging` exactly; the tracer's traced grid ==
`deflections_0 + deflections_1 + deflections_shear`; `number of planes == 2` for 3 galaxies; generated sample
co-dominance ratios 0.81-0.87. Smoke 16/16 locally, then smoke 3.12+3.13 / navigator / catalogue green in CI.

## Traps hit

- **A smoke run leaves a 15x15 `SMALL_DATASETS` dataset behind**, and `should_simulate` tests directory
  existence only, so a later "full fidelity" run silently reused it. Caught by a changed printed ratio
  (0.80 -> 0.81); re-verified after `rm -rf dataset/multi_galaxy`.
- **`git add` with a pre-`git mv` path stages nothing** and I had suppressed the error with `2>/dev/null`,
  so a Mind commit captured only the rename. Fixed by amend while unpushed.
- **Local `check_navigator.py` PASSED while CI FAILED** on 5 refs in files not in the diff. PyAutoHands #213
  widened the ref scanner, newly gating pre-existing drift; main fixed it in `3dc5058e` *after* this
  branch's merge base. CI also pulls PyAutoHands **fresh** and invokes it as
  `--root <checkout> --banners=fail`, which is not equivalent to `--root .` from inside the workspace.

## Open follow-up

`group/` and `cluster/` still use `shear=af.Model(al.mp.ExternalShear) if i == 0 else None`, so
`multi_galaxy/` now diverges from its siblings on the ladder. Propagating the `shear_galaxy`-at-(0,0) idiom
upward was flagged on the PR and in the closing issue comment, not done.

Also deliberately not done: the three new scripts pass under `PYAUTO_TEST_MODE=2` /
`PYAUTO_SMALL_DATASETS=1` but were **not** added to `smoke_tests.txt` — curated-subset convention, `imaging/`
covers only modeling+fit, and the new `shear_galaxy` idiom is already exercised by the covered
`multi_galaxy/{start_here,modeling}` entries.

The lowercase "mass/light offsets" prose in `simulator.py` was kept: it explains why the simulator offsets
each galaxy's light and mass centres, which it genuinely still does. Only the `__Mass/Light Offsets__`
sections were removed.
