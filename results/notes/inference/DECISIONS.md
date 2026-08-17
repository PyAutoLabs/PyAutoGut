# Inference programme — decision log

Append-only. One entry per gate decision, plan approval, or scope change.
Each entry: date, decision, evidence references, who decided.

## 2026-08-17 — Programme plan APPROVED (human)

The planning-pass artifact (mirrored as `PROGRAMME.md`) was reviewed and
approved with notes:

1. PositionsLH accumulation bug: "worrying ... so defo check" → verified same
   day and fixed (PyAutoLens#699, PR#700 — pending human merge).
2. BlackJAX NS: "on mge blackjax NS was fastest or comparable so worth a look,
   and it may scale better, so worth rerunning" — Phase 2 stands as designed
   (mainline blackjax ≥1.6, inner-steps ≥2d bias hypothesis pre-registered).
3.–6. State-of-play corrections, phase structure, schema, and critical path
   approved as written.

## 2026-08-17 — CP-1 complete: PositionsLH accumulation fix at PR

- Defect: `AnalysisLens.log_likelihood_penalty_from` returned 2x the LAST
  penalty and discarded earlier entries (verified by direct read + by the
  halved test pins).
- Fix: true sum over `positions_likelihood_list`; 3 test pins corrected
  (imaging single −44097289521.73 → −22048644768.18 = exactly half; imaging
  double-plane → −44140499627.75 = the true sum, distinct from the old
  2x-last value; interferometer −44097289569.23 → −22048644815.85); regression
  test added (analysis penalty == sum of per-object penalties).
- Suite: 538 passed, 0 failed. Science impact: inside-threshold unchanged;
  outside-threshold fence slope halves to the documented 1e8/arcsec;
  multi-plane stacking corrected.
- Consequence for the programme: any historical run that had a positions
  penalty ACTIVE at its recorded likelihood is not comparable to post-fix runs
  (none of the searches-framework benchmarks used positions, so the truth bars
  are unaffected).
