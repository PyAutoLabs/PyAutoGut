- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/246 (auto-closed on merge)
- shipped: 2026-08-21 — PyAutoBrain PR https://github.com/PyAutoLabs/PyAutoBrain/pull/247
  (generator) + PyAutoMind 3566a908 (stamps, cron, epics.md schema) + 2d7f2367 (the
  numba-prompt reconciliation that motivated the drift flag).
- classification: feature (PyAutoBrain + PyAutoMind) — both human-reported dashboard
  problems from 2026-08-21.
- summary: (1) Epic grouping — prompts declare membership via `Epic: <slug>` +
  optional `Phase: N` headers (documented in epics.md; NOT header-hygiene fields);
  members leave Start-here and the work-type dropdowns and render only inside their
  epic's group (resume 📋 first, phase-ordered, start-in-order caution) in an Epics
  section moved to the bottom, md + html. Unregistered slugs group loudly. 23 prompts
  stamped: 14 Source & Cluster arc (phases 1-12 from the ledger; narrative doc rides
  phase 10; ledger itself phase-less) + 9 EP campaign (phases from ep_campaign.md's
  table; two members live OUTSIDE draft/research/graphical_ep — bug/autofit and
  feature/autofit — which is why membership is per-prompt, not per-folder).
  (2) Freshness — dashboard_refresh.yml gains a nightly 03:20 UTC cron, and the
  census flags draft prompts whose body carries a line-anchored `Fix: … PR #N` as
  "Needs lifecycle reconciliation" above Start here.
- diagnosis that shaped it: the "stale dashboard" was NOT render staleness — the
  numba psf_weighted_data bug was fixed AND merged overnight (PyAutoArray#456) but
  the session left the prompt in draft/, so the truthful render advertised a fixed
  bug as top-priority backlog. The drift flag catches that idiom; the cron catches
  what push triggers cannot (Brain-side generator merges, time-dependent renders).
- trap found post-ship (fixed a305a293): pages_dashboard.yml only fires on pushes
  touching dashboard.html, and the self-heal commit uses GITHUB_TOKEN — which never
  triggers other workflows — so the repo copy was fresh while the PAGES site stayed
  stale (the human's 'don't see it yet'). The heal step now dispatches the publish
  explicitly (same class as the Memory queue_actions → knowledge_board redispatch).
- trap fixed in passing: BOTH self-heal steps in dashboard_refresh.yml gated on
  event == push — a scheduled run finding drift would have FAILED rather than
  healed. Now only pull_request errors-without-healing.
- validation: 28 dashboard contract tests (6 new) + full Brain suite 380 passed;
  post-merge self-heal run completed/success on 3566a908 and the live page renders
  both epic groups phase-ordered with members absent from the body sections.
- affected-repos:
  - PyAutoBrain
  - PyAutoMind

## Original prompt

# Mind dashboard: epic grouping + freshness guards

Type: feature
Target: pyautobrain
Repos:
- PyAutoBrain
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Two human-reported dashboard problems (2026-08-21), plan approved in session.

## Original request (verbatim)

> Two issues on the PyAutoMind dashboard, first another issue I thought i did
> last night is there, so maybe we need to be more routine about when it
> updates? Idk if I want it to after every issue but maybe a nighttime build
> or something should of got it? The issue is Numba sparse-operator
> likelihood: first-call garbage / intermittent worker corruption — ....
> Next, I think tasks under an epic are listed in their section as well, but
> to be if something is part of an epic it shouldnt be part of the
> subsections as it should bedone in order rather than accidently doing it
> standalone out of order. I think that being able to see all tasks in an
> epic grouped and sequential (if appropriate). So maybe in the bit with bug,
> feature, research, etc we have clickable dropdowns for each epic at the
> bottom. I would then also move the "Epic" section which listed the epics
> down to be above that, so Epics are grouped together at the bottom.

## Diagnosis

The numba case was NOT render staleness — the render is push-triggered and
current. The overnight session fixed and MERGED the bug (PyAutoArray#456) but
left the prompt in draft/ as `formalised`, so the dashboard truthfully
advertised a fixed bug as top-priority backlog. Reconciled by hand
(Mind 2d7f2367, record `complete/2026/08/numba-first-call-garbage-...`).
Epic membership today is prose only (`epics.md` notes) — the arc's 12 members
scatter across bug/research/refactor/test/feature/docs work-type folders, so
membership must be declared per prompt, not inferred from paths.

## Plan

1. **PyAutoBrain `agents/conductors/intake/_intake.py`** (ships FIRST — the
   Mind refresh renders with Brain main):
   - `parse_header` learns `Epic:` (slug) and optional `Phase:` (int).
   - Census: records carry epic/phase; a **drift leg** flags draft prompts
     whose body carries a line-anchored `Fix:` naming a PR (`PR #N` /
     `pull/N`) — the exact idiom last night's session wrote — as "needs
     lifecycle reconciliation".
   - Both renders (md + html): epic-member prompts are EXCLUDED from the
     Start-here pick lists and the Backlog work-type dropdowns (counts
     adjusted); the `## Epics` section MOVES to the bottom, after the
     work-type dropdowns, and each epic groups its resume 📋 row with a
     nested dropdown of its member prompts in `Phase:` order (filename
     fallback), each row carrying a start-in-order caution; an epic with no
     Mind prompts renders as ledger-driven. Drift flags render near the top.
   - Tests beside the generator updated/added.
2. **PyAutoMind** (direct main, after Brain merges):
   - `dashboard_refresh.yml` gains a nightly `schedule:` cron (the routine
     rebuild the human asked for) alongside push triggers.
   - Stamp `Epic:`/`Phase:` headers on the source-cluster arc prompts still
     in draft/ (ledger `draft/feature/autolens/source_cluster_arc.md`, 12
     listed) and the graphical_ep phase prompts (`draft/research/graphical_ep/`,
     campaign file excluded); `epics.md` schema note documents the header.
