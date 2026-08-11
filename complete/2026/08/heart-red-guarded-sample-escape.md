## heart-red-guarded-sample-escape
- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/567
- completed: 2026-08-11
- library-prs: https://github.com/PyAutoLabs/PyAutoFit/pull/1466, https://github.com/PyAutoLabs/PyAutoFit/pull/1468, https://github.com/PyAutoLabs/PyAutoFit/pull/1470
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/484
- merge-commits: PyAutoFit `b499d436` (#1466), `08f73c31` (#1468), `566ee117` (#1470); autolens_workspace `2841252` (#484).
- summary: Closed the escape path that kept release validation RED after
  profile-validation-resample-recovery shipped. The library guard was always
  correct — it rejects an unphysical `ell_comps` — but three separate paths in
  PyAutoFit still reconstructed or re-served a sample the guard had already
  rejected: the guarded sample lifecycle (#1466), stale factor-graph subsample
  instances surviving a model rebind (#1468), and stored sample/instance pairs
  that did not expose which entries were valid (#1470). The workspace side
  (#484) stopped the aggregator results guide from rebuilding profiles out of
  invalid historical samples. Together these took PyAutoHeart's release
  integrate run from red to green.
- validation: four `Release Integrate` dispatches on PyAutoHeart `main`
  (head `b7634e2c`) bracket the arc, and the failing surface shrinks
  monotonically as each fix lands:
  - run 31456732688 (03:52Z) FAILED — 4 script packages: autofit/cookbooks,
    autolens/multi_dataset, autogalaxy/multi_dataset, autolens/guides.
  - run 31517075410 (17:20Z, after #1466 at 16:46Z) FAILED — 5 script
    packages: autofit/cookbooks, autolens/multi_dataset,
    autogalaxy/multi_dataset, autolens/weak, autolens/cluster.
  - run 31525583134 (18:59Z, after #1468 at 17:46Z) FAILED — 1 script package:
    autolens/guides.
  - run 31534325304 (20:42Z, after #1470 at 19:52Z and #484 at 19:59Z)
    **SUCCESS** — 53 jobs, 52 green, `integrate / run_notebooks` skipped by
    design. Artifacts written: `release-stage-report`,
    `workspace-validation-report`, `verify-install-release`.
- evidence-basis: the run-to-run mapping above is from the Actions **job**
  outcomes and PR merge timestamps, not from reading job logs — per-script
  causation for each individual PR was not independently proven. The last leg
  is the firmest: the 18:59Z run's only failure was `autolens/guides`, #484
  touches exactly `scripts/guides/results/aggregator/samples.py` and its
  notebook, and the next dispatch was green.
- OPEN TAIL — the green evidence was never ingested, so Heart still
  under-reports: run 31534325304 finished 21:50Z and its `release-stage-report`
  artifact is unconsumed. Heart's last committed dashboard (05:51Z, before the
  green run) reads **STALE score 65** with `no release validation for current
  source` among the evidence gaps. Until someone runs
  `gh run download 31534325304 -R PyAutoLabs/PyAutoHeart -n release-stage-report -D <dir>`
  then `pyauto-brain release validate --ingest <dir>`, the organism claims less
  health than it has. This is the STALE tier working correctly — an evidence
  gap, not a fault.
- trap (cost this record a step): Actions artifact downloads are **laptop-only**.
  The cloud/web session egress policy 403s the CONNECT to
  `productionresultssa14.blob.core.windows.net`, so the artifact cannot be
  fetched from a cloud session even though the GitHub API happily returns a
  signed download URL. This is the same `artifacts-are-laptop-only` trap
  recorded under release-drive-2026-08-07; it is a property of the session
  surface, not of the run.
- issue-state: PyAutoGalaxy#567 is still **open (reopened)**. Its last comment
  (2026-08-11T02:51Z) points at PR #1463 and predates all four PRs above. The
  issue is now satisfied on the evidence of run 31534325304, but it was left
  open — close it only alongside the ingest, so the close and the GREEN verdict
  land together.
- provenance: this record was written after the fact, from GitHub state, by a
  cloud session reconstructing an interrupted Codex session's work. The Codex
  session merged all four PRs and dispatched the green run, then ran out of
  credits before writing any Mind bookkeeping. No code was changed to produce
  this record.

## Original prompt

# Heart-red recovery: the guarded-sample escape paths

Type: bug
Target: PyAutoFit
Repos:
- PyAutoFit
- autolens_workspace
Difficulty: medium
Autonomy: human-required
Priority: urgent

## Original request (verbatim)

> Can we target making heart red

(The parent request for the whole arc; this record covers the follow-up leg
opened when PyAutoGalaxy#567 was reopened on 2026-08-11T00:22Z.)

## Problem

profile-validation-resample-recovery shipped a correct constructor guard, but
post-merge release validation (run 31441556729) still reported 660 passed /
1 failed: `autolens_workspace/scripts/imaging/features/extra_galaxies/slam.py`
rejecting `ell_comps=(-0.9257683911051445, -0.5502774378326348)`, magnitude
1.0769644249264025. The reopened issue named the open question: is the escape
in PyAutoFit's post-likelihood/quick-update reconstruction, or does it need a
narrower workspace prior?

## Outcome

It was the reconstruction, in three places, plus one workspace guide that
rebuilt profiles from invalid historical samples. No prior was narrowed.
