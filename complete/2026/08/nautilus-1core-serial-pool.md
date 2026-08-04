## nautilus-1core-serial-pool
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1442
- completed: 2026-08-04 (shipped 2026-08-01; closed out 2026-08-04)
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1443 (MERGED 2026-08-01T19:12:47Z, merge commit 5bf32dab)
- summary: corrective for the Heart RED "release validation FAILED (stage
  integrate)" — `graphical/hierarchical.py` went from 76s to a 1800s TIMEOUT in
  runs 30672739606 + 30686136529. Cause: e6279c53f (#1439) always built a fork
  `Pool(1)` for Nautilus, bypassing nautilus's own `pool ∈ [None, 1] → serial`
  guard; the forked worker then deadlocked inside XLA compile under the
  release-profile JAX settings. Fix: `pool=None` at `number_of_cores=1`, fork
  pool retained for >1.
- evidence at ship: regression test `test__single_core_builds_no_pool` red on
  main / green on the branch; `test_autofit/non_linear/` 411 passed, 1 skipped;
  py-spy stacks (main blocked in `nautilus pool.map → wait`, forked worker stuck
  in `jnp.array → … → backend_compile_and_load`) posted on #1442;
  control-vs-patched under the release-profile env — control hangs, patched
  completes exit 0 in ~2 min.
- verification in production CI (checked 2026-08-04, the close-out pass): the
  latest successful Release Integrate (run 30901054267, 2026-08-04T10:32) shows
  `scripts/graphical/hierarchical.py ... PASS (6.8s)` — the exact script that was
  timing out at 1800s. Heart `readiness --json` now returns `red_reasons: []`;
  the "release validation FAILED (stage integrate)" reason is gone. Post-merge
  integrate failures on 08-01/08-03/08-04 exist but are unrelated legs
  (`verify_install_release`, `run_scripts autolens point_source`, `run_scripts
  autolens multi_galaxy`), NOT hierarchical.py.
- heart: shipped under the human-authorized corrective-PR exception for Heart RED
  — authorization was the 2026-08-01 session instruction quoted verbatim on #1442
  ("do a release, fine if any blockers need sorting…"), given at launch for any
  blockers rather than after the RED surfaced; noted on the issue and the
  autonomy log row.
- still open (explicitly not claimed by this task): `delaunay.py` intermittent
  TIMEOUT — pre-existing, crosses SHA windows, unrelated to the fork-pool fix.
- close-out note: the fix shipped 2026-08-01 and #1442 auto-closed at merge
  (2026-08-01T19:12:49Z), but the `active.md` entry was never advanced — its
  status line still read "PR OPEN … awaiting CI" and its `repos:` line still
  claimed PyAutoFit, which fired the worktree conflict guard against
  test-mode-samples-info-hook-contract (#1448) on 2026-08-04. Claim released and
  this record written in that same pass.
