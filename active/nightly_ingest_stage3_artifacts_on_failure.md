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
