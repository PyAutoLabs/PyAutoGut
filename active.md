# Active Tasks

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- prompt: active/16_transformed_message_factor_gradient_unpack.md
- status: HOLD — do not start dev. Fix-or-delete hangs off the PyAutoFit#1498 logpdf-contract
  decision (parked #1500 design bundle); dead code (zero production callers), crashes on first
  call if ever exercised.
- external: community PR https://github.com/PyAutoLabs/PyAutoFit/pull/1502 (@trexfr-ops) targets
  this exact unpack — review via /community before any local work; the #1498 adjudication decides
  whether the method should exist at all.
- registered: 2026-08-19 by the wake_up session — the issuing session (claude/autofit-priors-messages-audit-ylvenv)
  filed the prompt + issue but not this entry, tripping Lifecycle Drift on main.
- repos-none-claimed: this entry claims NO repos — one line deliberately, not 2-space bullets.

## hands-hygiene-leftovers
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/249
- session: claude --resume 08f77ea2-bf3a-42f4-a427-e01da3a4ce2d
- status: library-dev
- worktree: ~/Code/PyAutoLabs-wt/hands-hygiene-leftovers
- prompt: active/hands_hygiene_leftovers.md
- scope-note: the prompt's third bullet (~30 stale PyAutoHands remote branches, incl.
  origin/master, origin/release) is deliberately OUT of this task's PR — run it as a
  separate /repo_cleanup sweep so a destructive branch delete never rides a code diff.
- repos:
  - PyAutoHands: feature/hands-hygiene-leftovers

## small-datasets-regime-stamp
- issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/153 (issued 2026-08-22, pre-existing — start_dev did NOT create it)
- session: cloud web-github session, branch claude/small-datasets-regime-stamp-s3i9o7
- status: library-dev — PLAN PRESENTED, awaiting human approval before any code edit
  (prompt is Autonomy: supervised and this run has no --auto, so checkpoint 1 holds)
- prompt: active/small_datasets_regime_stamp_at_writer_funnel.md
- worktree: n/a — web-github environment; clones at /home/user/pyautonerves, /home/user/pyautoarray
- FINDING, corrected after deep research (an earlier note in this entry overstated the
  interferometer part and understated the rest — this supersedes it):
  the issue's premise "every FITS write funnels through `output_to_fits`" is false, but not
  where it first appeared. The interferometer SIMULATOR does use `output_to_fits`
  (`autolens_workspace/scripts/interferometer/simulator.py:166` passes `data_path=`, the
  separate-file arm), so the issue's proposed stamp point would have caught the motivating
  case. The real hole is elsewhere and much larger: **14 production sites in PyAutoGalaxy
  and PyAutoLens call `hdu_list.writeto(...)` directly** and never import `write_hdu_list`
  at all, plus 4 more hand their HDUList to PyAutoFit's `paths.save_fits`
  (`autofit/non_linear/paths/directory.py:131`, verified to `writeto` the list as-is).
  All of them build via `hdu_list_for_output_from`. So neither `output_to_fits` NOR
  `write_hdu_list` is the funnel — `hdu_list_for_output_from` is, and the shipped change
  stamps BOTH it and `write_hdu_list`. Stamping only `output_to_fits` would have missed
  16 of 18 library write sites.
- SCOPE CORRECTION to the issue text: point-source datasets are NOT JSON-only — they write a
  top-level `data.fits` and ARE covered by the stamp. Only weak-lensing `simple` is genuinely
  FITS-free. Read side covers ~228 of 253 `should_simulate` call sites in autolens_workspace;
  the ~23 misses (datacube `channel_XXX/`, multi_dataset `{waveband}_data.fits`, sample
  `dataset_N/`, weak lensing) all fail SAFE to keep. Widening the match is deliberately left
  as its own change — every trap in autolens_workspace_test#260 was a widened match.
- risk surface is SMALLER than the prompt feared: no md5/sha256/golden-file pins over FITS in
  either repo; header round-trip readers index specific keys by name (never `**kwargs`), so
  an extra card cannot poison mask/geometry reconstruction; and the card is byte-size neutral
  (a FITS header block holds 36 cards, a real dataset header carries ~10), so the byte-size
  diagnostics from the predecessor task still hold.
- CORRECTION (an earlier version of this entry got this wrong): the two committed FITS
  fixtures that the suites rewrite —
  `PyAutoArray test_autoarray/structures/arrays/files/array/output_test/array.fits` and
  `PyAutoNerves test_autonerves/files/array_out.fits` — are dirtied BY THE STAMP, not
  pre-existing. The first check was invalid because the stamped autonerves was still on
  PYTHONPATH while only autoarray was reverted; with BOTH repos on clean main the trees stay
  clean. They are test write targets, so the refreshed bytes are committed (5cea0c8, e582e52);
  leaving them stale would hand every contributor a dirty tree after testing. Sizes unchanged
  at 5760 B.
- HYGIENE follow-ups, genuinely pre-existing and OUT of this diff: `autogalaxy/util/plot_utils.py`
  and `autogalaxy/plot/plot_utils.py` are byte-identical duplicate modules; and every
  `header_dict` card on disk carries the literal comment text `['']` because
  `fitsable.hdu_list_for_output_from` passes `[""]` as the comment.
- DATA-LOSS BUG FOUND BY ADVERSARIAL REVIEW AND FIXED (757238a). The completeness critic
  asked the question no research lane did: *is the proposition the stamp records the same
  proposition `should_simulate` acts on?* It is not. The stamp records "the env var was set
  in the writing process"; `should_simulate` read it as "this data is capped, therefore
  disposable". The library already makes those diverge — `Kernel2D.from_gaussian` passes
  `respect_small_datasets=False` (`convolver.py:729`), `Interferometer.from_fits` never caps,
  and any user converting real data in a shell exporting `PYAUTO_SMALL_DATASETS=1` (the
  documented harness default) stamps `T` on full-resolution data.
  REPRODUCED: a 300x300 image written under the cap, read in a full run, was DELETED — and
  the pre-stamp shape heuristic had explicitly refused to delete it. So the first cut was a
  strict WEAKENING of the safety property PyAutoArray#471 established, not a residual risk.
  FIX: a destructive `T` must be corroborated by the data. Every capped 2D image is rewritten
  to exactly (16,16), so `T` on an image larger than the cap in BOTH axes is a contradiction,
  resolved toward keep. Both axes, never either — interferometer `data.fits` is
  (n_visibilities, 2), 108384x2 for committed sdp81, so an "either axis" test would refuse to
  delete the one family the stamp exists for. Verified lossless against the real committed
  files: (16,16) and (108384,2) still delete; 151x151, 209x209, 300x300 now kept.
- FOLLOW-UP noted, out of scope: the capped branch (`PYAUTO_SMALL_DATASETS=1`) still rmtrees
  unconditionally and ignores the stamp it now has, so every smoke run re-simulates every
  dataset even when the stamp already says T. Pre-existing; `if stamp is not True:` is now a
  cheap fix.
- repos:
  - PyAutoNerves: claude/small-datasets-regime-stamp-s3i9o7 (39014b6, 553327f, e582e52)
  - PyAutoArray: claude/small-datasets-regime-stamp-s3i9o7 (601ffbd, 5cea0c8, e45a604, 757238a)
