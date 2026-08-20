# Mind dashboard — "Epics" section under In flight with one-tap resume prompts

Difficulty: easy
Autonomy: supervised

## Original request (verbatim)

> We have 3 epics planned and active in PYAutoMind, JAX profiling, cluster
> strong lensing and EP. Could we have an "Epics" tab on the PyAutoMind
> dashboard under In Flight, with an appropriate claude prompt explaining how
> to work out where the epic is and conitnue it. Its cumbersome to have to
> find the right issue that pairs to where an epic is rther than just
> contonue it from the next logical point automaticall

## Scope

- New @PyAutoMind root registry `epics.md` (same `## slug` + `- key: value`
  schema as active.md) listing the three live epics with their canonical
  ledgers: JAX profiling → `autolens_profiling/results/notes/inference/PROGRAMME.md`;
  cluster strong lensing → `draft/feature/autolens/source_cluster_arc.md`;
  EP → `draft/research/graphical_ep/ep_campaign.md`.
- @PyAutoBrain `_intake.py`: census parses `epics.md` (absent → no section);
  dashboard.md + dashboard.html render an "Epics" section directly under
  In flight; each epic row gets a 📋 prompt that tells Claude to read the
  ledger (+ sibling DECISIONS/RESULTS files), cross-check active.md and open
  issues/PRs, work out the last completed phase, and continue from the next
  logical step via the normal workflow — no hunting for the paired issue.
- Mind `scripts/spawn.py`: add `("epics.md", "EMPTY")` so template spawns
  don't fail on an unmatched root file; registry list docs updated.
- Counts table untouched (organism-router contract). Brain merges before the
  Mind regen PR (dashboard_refresh renders with Brain main).
