# Commit the inference-methods programme plan + knowledge ledger into autolens_profiling

Type: docs
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: high
Status: draft

The 2026-08-17 inference-methods planning pass (human-approved same day, with
notes) produced a full phased R&D programme: state of play, phases 0-13 with
decision gates A-F, benchmark/result schema v2, method-card knowledge structure,
source-change list, risk register, critical path, and a hypothetical decision
tree. Human review notes: (1) PositionsLH bug — verified, fix shipped as
PyAutoLens#699/PR#700; (2) BlackJAX NS "was fastest or comparable on MGE and may
scale better — worth rerunning" (Phase 2 stands); (3-6) approved as planned.

Per the programme's own knowledge rules, the canonical copy must live in
autolens_profiling, not in chat history or an artifact.

Task: create `results/notes/inference/` containing:

- `PROGRAMME.md` — the full plan (markdown adaptation of the approved artifact),
  maintained as phases execute.
- `DECISIONS.md` — append-only gate log, seeded with the 2026-08-17 plan
  approval + review notes and the CP-1 completion (PositionsLH fix PR).
- `LITERATURE.md` — the external references gathered during planning (blackjax
  1.6 nested sampling merge, NSS paper, GIGA-Lens/Herculens, NUTS diagnostics,
  informed-start SMC, MCLMC/MAMS, Pathfinder, proximal smoothing), one lesson
  line each.

No profiling runs, no scripts, no source changes — documentation only. Keep
`ruff check .` / `ruff format --check .` green (no .py files added) and do not
touch the auto-generated README tables.
