Made a failed nightly Stage 3 page with the failing scripts named, ending the
open-the-run-and-dig triage loop.

- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/184 (auto-closed)
- pr: PyAutoBrain#185 (`6ce4e7c71`) — merged unchanged (nightly.sh tree diff 0)
- change: `dispatch_and_await` best-effort-downloads the requested artifact on
  a FAILED run too (the report artifacts upload `if: always()`); the Stage 3
  failure page appends counts + top-3 `project script` pairs from
  `stage_report.json`. Verified against the real failed run 30516167217:
  `2 failed, 1 timeout: autogalaxy interferometer/start_here.py, autolens
  group/start_here.py, autolens interferometer/start_here.py`.
- SCOPE CORRECTION (the important learning): the prompt's original "ingest on
  failure in the nightly" was DEAD CODE — the nightly's HEART_STATE_DIR is an
  ephemeral CI dir (`$WORK/heart-state`) and the run exits right after paging;
  the nightly's ingest NEVER fed the dev-box verdict. The dev box's
  `validation_report` only refreshes on a local `validate --ingest`, which is
  why "release validation stale: source moved since rehearsal" is chronic. The
  durable fix (tick-side cached-artifact refresh from the release-integrate.yml
  channel, mirroring test_run's #120 pattern) is filed as
  `draft/feature/pyautoheart/release_channel_dev_box_freshness.md`.

## Original prompt

# Nightly driver: ingest Stage 3 artifacts even when the run fails

Type: bug
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: high
Status: draft

## Problem

`agents/conductors/release/nightly.sh` step 4b exits (`exit 2`) when the Stage 3
release-integrate run fails — **before** `pyauto-heart validate --ingest` (step 4c).
The ingested `validation_report` therefore freezes at the last green rehearsal, and
readiness shows the unhelpful `release validation stale: source moved since
rehearsal (…)` instead of the accurate, actionable
`release validation FAILED (stage integrate)` naming the failing scripts.
Observed 2026-07-26→30: 4 failed nights all froze the report at 2026-07-29 17:53.

## Scope

1. On Stage 3 failure, still attempt the artifact download
   (`workspace-validation-report`, `release-stage-report` — they upload with
   `if: always()`) and ingest what exists before paging and exiting. A failed
   rehearsal is evidence, not an evidence gap: RED "FAILED (stage integrate)" is
   the correct verdict and it self-clears on the next green night.
2. Keep the page message, but include the failing script names from the downloaded
   report when available (one line, top N).
3. Optionally annotate the stale-by-sha reason in `heart/readiness.py` with its
   remedy cadence — e.g. `…(refreshes with the nightly rehearsal)` — so the
   near-permanent between-release staleness reads as expected, not alarming.
   (Do not change tier semantics; phrasing only.)

## Evidence

- `nightly.sh:354-367` (exit before ingest at 382), `dispatch_and_await` return 2
  skips its optional download step.
