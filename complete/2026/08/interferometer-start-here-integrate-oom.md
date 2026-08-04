# interferometer/start_here.py OOM'd release-integrate — MultiStartProdigy 48-start vmap allocated ~86 GB

Issue: PyAutoLabs/autolens_workspace#449 (CLOSED 2026-07-31T23:15:15Z)

A **corrective** task, not a planned one: it was opened straight off a PyAutoHeart
RED leg, so it has no `draft/` prompt and never had an `active/` prompt file.

## What was wrong

Heart went RED with `release validation FAILED (stage integrate)`. Cause:
`scripts/interferometer/start_here.py` ran `MultiStartProdigy` with 48 starts as a
single **unbatched `vmap`**, which asks for ~86 GB in one allocation and OOMs the
integrate runner. The regression entered at **d5c9802d (2026-07-29)** — *after* the
then-current release — so no published wheel was affected; it was main-only breakage
that only the release pipeline exercised.

The RED was human-authorized as a corrective live in session `5b29e469` and the
authorization recorded on #449.

## What shipped (both merged 2026-07-31 ~23:15Z)

| Repo | PR | Merged | Change |
|---|---|---|---|
| autolens_workspace | [#450](https://github.com/PyAutoLabs/autolens_workspace/pull/450) | 2026-07-31T23:15:14Z (`5318cdf4`) | `batch_size=4` on the 48-start MultiStartProdigy — 2 files, +2/−0 |
| PyAutoHeart | [#132](https://github.com/PyAutoLabs/PyAutoHeart/pull/132) | 2026-07-31T23:15:18Z (`f278d0d1`) | derive the release-channel repo slug from the checkout origin (tenant firewall) — 1 file, +22/−1 |

Fix verified before merge by a **control-vs-patched run under the release-profile
env** — control OOMs, patched completes. Both branches
(`feature/interferometer-start-here-batch-size`,
`feature/release-run-repo-slug-firewall`) are gone from origin; no worktree remains.

## Why this task stayed open nine days after its code merged

The code merged 2026-07-31. What remained was the **manual release-validation leg** —
the RED does not clear on merge, only when a release-integrate run re-executes the
script and passes.

The leg then failed twice for a reason that had nothing to do with this fix:

- Stage 3 run **30672739606**, dispatched 2026-07-31T23:23Z, is the run `active.md`
  recorded as "in progress". It did not stay in progress — it **FAILED** at
  2026-08-01T00:29:52Z. The entry was never advanced, so for three days the ledger
  showed an in-flight run that had already failed.
- That failure, and its repeat in 30686136529, was
  **`graphical/hierarchical.py` 76s → 1800s TIMEOUT** — the Nautilus fork-`Pool(1)`
  deadlock, a *separate* defect that became its own task
  ([[nautilus-1core-serial-pool]], PyAutoFit#1442/#1443). The interferometer script
  itself was never implicated in either failure.

So this task's last leg was blocked behind an unrelated bug, and could only clear
once that bug shipped.

## What discharged it (2026-08-04)

**Release Integrate run 30901054267** (2026-08-04T10:32) — **51 success / 2 skipped /
0 failure**, including `integrate / verify_install_release`. In job 91965262992
(`run_scripts (3.12, autolens, interferometer)`) the log reads:

```
scripts/interferometer/start_here.py ...   PASS (173.5s)
```

That is the exact script that OOM'd, passing under the release profile. The release
**2026.8.4.1** then published to PyPI at **2026-08-04T11:43:29Z** (unyanked).

Verified at close-out, not assumed: the green run was read job-by-job and the PASS
line grepped from the job log rather than inferred from the run's `success`
conclusion.

## Traps worth keeping

- **An `active.md` "in progress" run id is a claim with a timestamp, not a state.**
  30672739606 was recorded in-flight and had failed 66 minutes later; nothing
  re-read it for three days. Re-poll a recorded run id before reasoning from it.
- **A corrective's own merge does not clear its RED.** The leg that opened the task
  is what closes it, and that leg can be held hostage by an unrelated defect. Track
  the *leg*, not the PR.
- The publishing release run **30905602064** carries one failure —
  `wiki_currency_check / wiki-currency` on **autolens_assistant** at
  `stack_version 2026.8.4.1`. All five `release_test_pypi` jobs succeeded and the
  publish completed; this is a post-publish assistant-baseline drift of the same
  class as the autogalaxy_assistant DEBT 1 cleared by `autogalaxy_assistant#11`.
  **Not this task's** — recorded here only because it was found while proving the
  release landed, and it is not yet tracked anywhere else.

## Original prompt

None — corrective filed directly from the Heart RED onto autolens_workspace#449.
