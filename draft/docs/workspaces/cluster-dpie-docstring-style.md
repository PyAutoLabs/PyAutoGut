# Cluster package: dPIE-only scaling galaxies + comment-to-docstring style sweep

Type: docs
Target: workspaces
Repos:
- @autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: medium
Status: draft

Note: Brain Feature Agent scored large(7)/split-into-phases — repo-count proxy
overestimate; overridden to a single phase (one repo, one package, prose-only
edits + one script restructure). Override recorded here per workflow.

## Original request (verbatim)

> We have previous had chats about making cluster examples use dPIE like
> lenstool, including the link to the bcg to reduce parameters. Can you check
> one last time weve matched lens tool, update all the cluster package to use
> dPIE and write it all in the correct style, so dont have long comments like
> this: [example of long `#` block above the main-lens model in
> cluster/modeling.py] but if you are going to describe something put it in a
> docstring. I know models often have comments abvove them which are short, but
> these are literally describing stuff so should use the docstring style. By
> the end I want all of cluster to only use dPIE for scaling galaxies.

## Pre-work verification (done in-session, 2026-07-30)

- Lenstool match re-verified: `autolens_workspace_test/scripts/cluster/
  lenstool_parity.py` run fresh — all 6 legs pass (b0 = 6·648000·(σ/c)²·D_LS/D_S,
  emass→epot, √(3/2) sigma convention, Lenstool reference deflections).
  No library change needed.
- Full survey of `scripts/cluster/**` completed: every runnable script's
  scaling tier is already dPIE; the one Isothermal scaling tier left is
  Section 2 of `mass_parameterizations_pyautolens.py`.

## Scope (all in `autolens_workspace/scripts/cluster/`)

1. **dPIE-only scaling galaxies** — restructure
   `mass_parameterizations_pyautolens.py`: the standard PyAutoLens mapping
   (Section 2) keeps NFW halo + Isothermal main/extra galaxies but its scaling
   tier becomes the truncated dPIE (`dPIEMassB0Sph`, b0 anchored to the BCG's
   `einstein_radius`, zero free parameters) currently shown in Section 3;
   merge/reframe Section 3 accordingly and update the header tables/prose.
2. **Comment→docstring sweep** — convert multi-line descriptive `#` blocks to
   docstring cells, keep short 1–2 line component labels:
   modeling.py (345–348, 352–357, 371–375, 386–408); start_here.py (157–160,
   308–310, 314–319, 333–335, 346–353 — dedupe vs the docstring cell at
   264–274); mass_parameterizations.py (88–91); likelihood_function.py
   (151–156, 707–709); csv_api.py (190–193, 384–385); lenstool/modeling.py
   (151–153, 347–350); lenstool/data.py (273–280, 333–335);
   lenstool/parameterization_mapping.py (134–135, 201–203).
3. **Stale-fact fixes found during the survey**:
   - cluster/README.md: drop nonexistent `data_preparation` + `features`
     entries; list csv_api, likelihood_function, both mass_parameterizations,
     and the lenstool/ subfolder.
   - lenstool/README.md: add the missing `parameterization_mapping.py` row.
   - start_here.py: "10 scaling-tier members" at lines 39/220 → 188 (a2744);
     "22-D model" at 419 → N=20; "100x100 starting grid" at 243 → 120x120.
   - likelihood_function.py: stale `_pair_closest_no_repeat` references at
     684 and 759–760 → `_pair_hungarian` / Hungarian pairing.
4. Regenerate notebooks, run `scripts/check_sizes.sh`, smoke tests.

Out of scope: `scripts/group/**` (Einstein-radius-space scaling relation is a
deliberately different regime, cross-referenced from cluster), library repos
(no change needed), `*_workspace_test` (parity script already green).
