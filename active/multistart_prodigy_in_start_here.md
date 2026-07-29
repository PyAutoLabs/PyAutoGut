# start_here.py: MultiStartProdigy as the default search across dataset types

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Original request (verbatim)

> Use MultiStartProdigy in start here examples of all dataset types, with
> description of posterior and say modeling.py gives full posterior. In
> modeling.py mention MultiStartProdigy and its use in start_here.py in like 2
> or 3 lines in the Search Docstring but dont include any code. Do this on
> autogalaxy and lens workspaces.

## Intent

Make the flagship `start_here.py` entry-point of every dataset type run the fast
`af.MultiStartProdigy` MAP optimizer instead of `af.Nautilus`, so a new user's
first fit finishes quickly. The prose must be explicit that a multi-start
gradient optimizer returns a **single best-fit (MAP) model with no posterior and
no parameter errors**, and must point at the folder's `modeling.py` as the
example that runs `Nautilus` and yields the full posterior.

`modeling.py` keeps `Nautilus` and keeps its code unchanged — it only gains 2-3
lines of prose in its `__Search__` (or `__Search + Analysis__`) docstring
mentioning `MultiStartProdigy` and its use in `start_here.py`. **No code is
added to `modeling.py`.**

## Scope — 13 dataset-type cells, 10 converted

All 10 convertible cells are parametric (MGE / Sersic, no `Pixelization`), so
they need no `resurrect=True`, no kernel-regularization choice and no extended
`n_steps` — the settings that the pixelized campaign found load-bearing do not
apply here.

Convert to `af.MultiStartProdigy` (replacing the `af.Nautilus` block outright —
no commented-out Nautilus left behind):

- autolens_workspace: `imaging`, `interferometer`, `multi`, `multi_galaxy`, `group`
- autogalaxy_workspace: `imaging`, `interferometer`, `multi`, `multi_galaxy`, `cluster`

## Blocked cells — keep Nautilus, explain the gap (human decision, 2026-07-29)

Three autolens cells cannot run a gradient search today. They **keep
`af.Nautilus`** and instead gain 2-3 lines of prose noting that
`MultiStartProdigy` is the fast MAP default in the other dataset types but is
not yet available for this data type, with the reason:

- `point_source` (`AnalysisPoint`) — point-source JAX gradients do not exist
  yet. Enabling work is
  `draft/feature/autolens/point_source_chi_squared_paper_variants_phase_5_jax_gradients.md`,
  whose stated goal is "so gradient searches (`af.MultiStartProdigy` /
  Adam-family) work on point-source fits". Still blocked on phase 2 merge.
- `cluster` — also `AnalysisPoint` (7 source systems over a `FactorGraphModel`),
  same blocker. Note it additionally ends on
  `aplt.corner_anesthetic(samples=result_list[0].samples)`, a posterior corner
  plot a MAP optimizer could not feed.
- `weak` (`AnalysisWeak`) — pinned to `use_jax=False` by an in-script comment
  citing PyAutoLens#614 ("Weak-lensing visualization crashes on JAX path:
  fit.shear_yx lacks .grid"), confirmed OPEN on 2026-07-29. A gradient search
  requires `use_jax=True`.

Do not write `af.MultiStartProdigy` into these three — it would ship three
broken entry-point scripts.

## Reference prose

`autolens_workspace/scripts/guides/modeling/searches.py` (the
`__MultiStartProdigy (JAX multi-start gradient optimizers)__` section) is the
canonical long-form description — GIGA-Lens multi-start provenance
(arXiv:2202.07663), Prodigy's learning-rate-free rule (arXiv:2306.06101), and
the "returns a single best-fit model, not a posterior with errors, so Nautilus
remains the default when uncertainties are required" framing. `start_here.py`
prose should be a short version of this, not a duplicate of it.

## Acceptance

- 10 `start_here.py` files run `af.MultiStartProdigy`; posterior caveat +
  pointer to `modeling.py` present in each.
- 13 `modeling.py` files carry the 2-3 line `MultiStartProdigy` mention in their
  Search docstring, and **no** new code.
- 3 blocked `start_here.py` files carry the "not yet available here" note and
  still run `af.Nautilus`.
- Smoke suite green in both workspaces; notebooks regenerated.
- `scripts/check_sizes.sh` clean (bulk-edit guard).
