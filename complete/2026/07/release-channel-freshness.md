The release channel's verdict now self-refreshes on the dev box — the last chronic
STALE ("release validation stale: source moved since rehearsal") is structural no more.

- issue: PyAutoHeart#128 (auto-closed) · pr: PyAutoHeart#129 (`b58aa35bb`), merged unchanged
- heart/checks/release_run.py mirrors test_run's cached-artifact pattern: latest
  release-integrate.yml run via gh, release-stage-report fetched once per run id,
  folded through the existing heart.validate.run() ingest (stage reports embed their
  own commit_shas/testpypi_version). decide() pure/no-network; gh callables only in
  the tick entrypoint. Rules (each test-pinned): in-progress never ingests; cached id
  never re-downloads; a fresher local ingest is never regressed; unparseable ts fails
  toward refresh; a FAILED rehearsal ingests too (release_ready=false is evidence →
  accurate 'release validation FAILED (stage integrate)' RED, self-clearing next
  green night). Wired into tick.sh. Live proof: the real failed rehearsal artifact
  ingested to release_ready=False and readiness computed exactly that RED. Suite 337.

## Original prompt

# Dev-box freshness for the release channel (self-refreshing validation_report)

Type: feature
Target: pyautoheart
Repos:
- PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Problem

The dev box's `validation_report.json` only updates on a *local*
`pyauto-heart validate --ingest` (the manual release flow). The nightly's own
ingest goes into an ephemeral CI state dir, so after every library merge the
dev box shows `release validation stale: source moved since rehearsal (…)`
until someone manually ingests — a near-permanent, unexplained STALE between
releases even though a fresh rehearsal ran (or failed, with evidence) last
night on the `release-integrate.yml` channel.

## Scope

Extend the cached-artifact pattern shipped in `test_run.py` (PyAutoHeart#120)
to the release channel: a tick-budget check that reads the latest
`release-integrate.yml` run (conclusion + run id via `gh run list`, artifact
`release-stage-report` fetched once per run id) and ingests/refreshes the
`validation_report` sidecar from it — so the staleness reason self-heals after
each nightly and a failed rehearsal shows as an accurate
`release validation FAILED (stage integrate)` on the dev box too.

Constraints: keep `run()`-style no-network library contracts (fetch only at
the tick entrypoint, cached per run id); never let a cloud stage report
*regress* a fresher local ingest (compare timestamps/run ids); tier semantics
unchanged. Optionally annotate the stale-by-sha reason with its remedy cadence
("refreshes with the nightly rehearsal").

## Provenance

Split out of the CI/release audit series task 4
(`nightly_ingest_stage3_artifacts_on_failure.md`, PyAutoBrain#184), whose
original "ingest on failure in the nightly" framing turned out to be dead code
— the durable dev-box refresh belongs in Heart, not the nightly driver.
