Committed the human-approved 2026-08-17 inference-methods programme into its
canonical home, `autolens_profiling/results/notes/inference/`, per the
programme's own knowledge rules (no knowledge lives only in chat histories or
artifacts). Documentation only — no runs, no scripts, no source changes.

- **PRs:** autolens_profiling#136 (merged `3be8158` — PROGRAMME.md +
  DECISIONS.md + LITERATURE.md, adapted from the approved artifact, with a
  maintained phase/gate state table and CP-1 marked complete) and
  autolens_profiling#137 (merged `5ce0243` — folded in the laptop session's
  richer content; closed issue #134).
- **Duplicate-work trap:** the task was started twice. A laptop session had
  already opened autolens_profiling#135 (`feature/inference-programme-ledger`,
  registered in active.md) when a mobile/cloud session redid the task on
  `claude/inference-methods-autolens-w86nz9` and merged #136 without checking
  the registry first. The versions were complementary — #136 had the fuller
  PROGRAMME body (995 vs 558 lines), #135 the richer CP-1 evidence
  (test-pin values, 538-test suite, fence-slope-halving science impact,
  truth-bars-unaffected note), the deeper LITERATURE set (~25 refs incl. the
  optimizer-termination section), and the Future follow-ups section. #137
  reconciled them; #135 closed unmerged, nothing lost. Lesson: check
  active.md's PR/status line before re-issuing an in-flight task from another
  device.
- **Leftovers:** laptop worktree `~/Code/PyAutoLabs-wt/inference-programme-ledger`
  and remote branch `feature/inference-programme-ledger` are stale — next
  repo_cleanup pass.
- **What the ledger seeds:** DECISIONS.md carries the plan approval (verbatim
  review notes) + CP-1 completion (PositionsLH accumulation fix,
  PyAutoLens#699/PR#700). Next programme steps per PROGRAMME.md's critical
  path: CP-2 blackjax ≥1.6.2 upgrade + mainline NSS smoke (laptop GPU), then
  CP-3 Prodigy reliability scan; Phase 0 (b)(c)(e) outstanding.

## Original prompt

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
