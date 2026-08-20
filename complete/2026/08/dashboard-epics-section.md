## dashboard-epics-section
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/251
- completed: 2026-08-20
- workspace-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/242 · https://github.com/PyAutoLabs/PyAutoMind/pull/252
- summary: New root registry epics.md (active.md-style schema; fields title/ledger/
  status/notes) lists the three live epics — JAX profiling (ledger
  autolens_profiling/results/notes/inference/PROGRAMME.md), cluster strong lensing
  (draft/feature/autolens/source_cluster_arc.md), EP campaign
  (draft/research/graphical_ep/ep_campaign.md). The dashboard renders an Epics
  section under In flight; each 📋 copies a resume PROCEDURE (read the ledger +
  DECISIONS/RESULTS siblings, cross-check epics.md/active.md and open issues/PRs,
  continue from the next logical step via /start_dev) — deliberately no phase
  snapshot baked in, so the button never goes stale. Every html section now also
  links its markdown source ("markdown version": active.md/epics.md/parked.md/
  planned.md/draft tree). spawn.py gained the epics.md EMPTY rule and the spawned
  dashboard.md title was un-staled ("PyAutoMind task dashboard" → "PyAutoMind
  Dashboard"). Absent epics.md → no section (spawn-safe). Counts table untouched
  (router contract).

## Original prompt

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
