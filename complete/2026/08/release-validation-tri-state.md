# Heart graded an absent rehearsal as RED "release validation FAILED"

Surfaced by `/wake_up` on 2026-08-14. Heart reported **RED score 45** against a
`Release Integrate` run that was entirely green — 661 passed / 0 failed,
`failures: []`, GitHub conclusion `success`, zero non-success jobs.

- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/144 (closed completed)
- pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/145 — MERGED 2026-08-14T18:01:36Z as `a0113dc` (squash, 6 commits)
- repos: PyAutoHeart only

## Root cause

`release_run.py` auto-refreshes the release channel every tick by downloading the
latest `release-integrate` run's `release-stage-report` and calling
`validate.run([td])` on **that directory alone, no merge base**. The workflow
emits `--stage integrate` and uploads a single `stage_report.json`
(`workspace-validation.yml:575,600`), and `to_stage_report()` writes one
top-level `stage` key, so a `rehearse` stage is structurally impossible on this
path. `_Accumulator.release_ready()` required one, so `release_ready` was `false`
**by construction**, and `readiness.py` mapped every `false` onto the RED axis.

Both modules' own docstrings said the opposite: absence is the STALE axis,
failure is the RED axis. Reproduced on clean main before any edit.

## What shipped

`validation_outcome: pass | fail | incomplete` is the severity axis;
`release_ready` is derived from it (`== "pass"`) so a self-contradictory report
cannot be produced. `validate.report_outcome()` is the single normaliser every
consumer reads — readiness, dashboard, the `validate` CLI summary, and the tick
status line — and it reconciles the report's **evidence** before its declared
verdict. `fail` covers any adverse signal: a failed stage, failing/timed-out
counts in `totals` or any `per_project` entry, a non-empty `failures` list, the
producing run's own conclusion (`force_fail`), a malformed discriminator, or one
contradicting the boolean beside it. Reports predating the field fail closed.

`release_run.decide()` re-folds once when the stored report predates the
discriminator, so the RED self-heals; that migration is blocked by any adverse
evidence in the stored report and by a `rehearse` stage the integrate-only
artifact cannot reproduce.

Merged base reports are ordered: fresh stage artifacts subordinate a base in
full (its stages, counts and verdict all skipped — only scalars seed through);
otherwise the newest base by `ts` wins; only an equal or unparseable `ts` lets a
base escalate to adverse, never soften.

## Verification

- **Live, against the real state and the real artifact, no CI re-dispatched:**
  RED 45 `release validation FAILED` → **YELLOW 70**, `red_reasons: []`,
  `stale_reasons: ["release validation incomplete: no rehearsal for current
  source"]`. Confirmed on the canonical dev-box checkout post-merge.
- 452 tests; every guard mutation-verified (reverting each fails 1–4 tests).
- Flows re-checked as unaffected: the manual release-drive ingest, idempotent
  legacy re-ingest, and the M2 rehearsal-only report all still yield `pass` /
  `release_ready: true`.

## Review

Five adversarial Codex rounds (`codex exec --sandbox read-only`), findings
6/4/3/3/5. Every finding was reproduced against the branch before being acted
on. Several were regressions introduced by the *previous* round's fix — most
instructively, deriving one field from the other fixed a false-STALE and created
a false-RED at the same time, because the two fields were still computed
independently.

One finding closed a **pre-existing** fail-open that reaches GREEN on `main`
today: a legacy report stating `release_ready: true` beside a failed stage was
trusted on the strength of the boolean alone.

Human decision 2026-08-14: merge at round 5 rather than continue. Findings were
not converging and the diff had grown to +1577/-69 across 11 files, most of it
hardening paths `main` had always mishandled, well beyond the reported bug.

## Traps worth remembering

- `readiness.compute` reads the **snapshot's embedded copy** of the report
  (`state.py:86` folds `validation_report.json` in at `state.aggregate()` time),
  so re-ingesting alone changes nothing until state is re-aggregated — and
  `readiness.main()` prints the **cached** `release_ready.json` via
  `load_verdict()`, not a live compute.
- "report ts >= run created" does **not** identify a manual ingest; every ingest
  happens after the run it ingests.
- `_classify` needs both `release_ready` and `stages` keys — a payload missing
  one is silently `unknown` and never ingested, which invalidated one of my own
  probes mid-review.
- `(x or {}).items()` guards an **empty** list but not a populated one.

## Original prompt

# Heart grades an absent rehearsal stage as RED "release validation FAILED"

Type: bug
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

Surfaced by `/wake_up` on 2026-08-14. Heart reported **RED score 45**, top blocker
`release validation FAILED` — against a release-integrate run that was entirely green.
The verdict is a grading defect, not a release failure.

## The contradiction

Run [31769743408](https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/31769743408)
(`Release Integrate`, `workflow_dispatch` on `main`, 2026-08-14T04:23:59Z):

| Evidence | Value |
|---|---|
| GitHub run conclusion | `success` — zero non-success jobs |
| `validation_report.json` totals | 661 passed / 0 failed / 0 timeout |
| `failures` | `[]` |
| `stages` | `{integrate: pass}` |
| `release_ready` | **`false`** |
| Heart verdict | **RED**, `red_reasons: ["release validation FAILED"]` |

Per-project counts are clean across all six projects (autofit 26p, autofit_test 44p,
autogalaxy 125p, autogalaxy_test 44p, autolens 325p, autolens_test 97p — 0 failed each).

## Root cause: an undocumented second condition on `release_ready`

`heart/checks/release_run.py` auto-refreshes the release channel on every tick. On
`action == "ingest"` it downloads the latest `release-integrate` run's
`release-stage-report` into a temp dir and calls `validate.run([td])` — **that directory
alone, no merge base** (`heart/checks/release_run.py:152-153`).

`_Accumulator.release_ready()` (`heart/validate.py:323-335`) returns true only if:

1. no stage has `status == "fail"`, **and**
2. an explicit `release_ready` was merged in from a base report, **or**
   `stages["rehearse"].status == "pass"`.

An integrate-only stage report carries `stages: {integrate: pass}` and nothing else.
It can never satisfy (2). So **this path yields `release_ready: false` by construction**,
no matter how green the run was.

`readiness.py:461-468` then reads `ready is False` as the RED axis and emits
`release validation FAILED`.

## Why the grading, not the ingest, is the defect

The mandatory-`rehearse` condition contradicts this module's own documented contract,
in two places:

- `heart/validate.py:38` — `"release_ready": true,  # top-level pass/fail axis (no stage failed)`
- `heart/validate.py:63-70` — *"`release_ready` is the **pass/fail** axis only: it is
  `false` if any ran stage failed. Release fidelity and freshness … are judged separately
  by the readiness gate … Keeping the axes separate is what lets an M2 rehearsal-only
  report be faithfully `release_ready` yet still gate YELLOW."*

`readiness.py:452-458` states the same intent from the other side: *"Absent/stale/
source-not-matching → YELLOW ('no release rehearsal for current source'); **failing → RED**.
Pass/fail (`release_ready`) is the RED axis; fidelity+freshness … is the YELLOW axis."*

Both files agree: **absence of a rehearsal is a YELLOW/STALE evidence gap, and RED is
reserved for an actual failure.** The implementation conflates the two. The tell is
already in the RED message itself — `readiness.py:466` appends `(stage ...)` only
`if failed_stages else ""`, i.e. the author anticipated reaching RED with *no failed
stage* and shipped it anyway.

## Cross-review (Codex, read-only) — the first plan was REJECTED

A `codex exec --sandbox read-only` cross-review upheld the root cause above and
rejected the original readiness-only fix. Every load-bearing finding was then
re-verified against the code before being accepted:

1. **The proposed `failed_stages`-empty test is unsafe.** "No stage says `fail`" is
   not a sound proxy for "nothing failed":
   - `_norm_status` is called at `validate.py:243`, inside `add_stage` **only**.
     `add_report` copies stage entries verbatim (`validate.py:308-310`), so a merged
     full report carrying `status: "failure"` never normalises to exactly `"fail"`.
   - `_norm_status` maps **unknown → `"skip"`** (`validate.py:120-129`), so any
     unrecognised status token silently becomes `skip`, never `fail`.
   - `release_ready()` never consults `totals` or `failures` at all.

   The original change would therefore have downgraded genuine failures RED → STALE.
2. **That downgrade is not cosmetic.** `AUTONOMY.md:162-168` — the autonomous
   dev-ship gate's leg 4 passes on **GREEN or STALE**. Misgrading a real failure as
   STALE would let autonomous ships through a gate that should have blocked them.
   (Releases are unaffected — they require exact GREEN.)
3. **The proposed reason wording breaks Health Agent routing.** `health.sh:176`
   matches `release validation|validation report`. `"no release rehearsal for current
   source"` matches neither → falls through to `unknown` → recommends a bare
   `pyauto-heart tick`, which hits the `cached` branch and changes nothing. The
   replacement string **must** contain the literal `release validation`.
4. **`to_dict()` drops `stale_reasons`.** `dashboard.py:793-812` — the machine surface
   the Health Agent and mobile consume emits `red_reasons` and `yellow_reasons` but
   **not** `stale_reasons`. Moving the explanation to the stale axis without fixing
   this makes it vanish from those surfaces.

Also corrected: `test_ingest_nothing_is_not_ready` (`tests/test_validate.py:177-180`)
proves *"not ready without rehearsal"* is deliberate — it does **not** prove that every
`false` means failure. The original plan anchored on the wrong implication.

## Fix options considered

- **A — readiness-only grading tweak. REJECTED** by the cross-review, see finding 1.
- **B — merge the existing `validation_report.json` as an ingest base. REJECTED.**
  `_explicit_ready` is honoured from a merged base (`validate.py:320-321, 332-333`), so
  a *stale passing rehearsal from a previous release* would mark a *new* integrate-only
  ingest as release-ready. That launders old evidence onto new source — strictly worse
  than the current false RED. Codex independently reached the same rejection.
- **C — have the auto-ingest also fetch the M1 rehearsal artifact.** Most faithful, but
  the rehearsal lives in a different repo/workflow (PyAutoHands `release.yml`), and
  Heart is deliberately credential-free (`validate.py:30-32`). Parked, not scoped.
- **D — explicit tri-state discriminator. CHOSEN** (human decision, 2026-08-14).

## Chosen design (D)

One boolean cannot carry both "a stage failed" and "the evidence is incomplete".
Make the two states explicit, and **fail closed** on anything ambiguous.

- `heart/validate.py` — emit `validation_outcome: "pass" | "fail" | "incomplete"`
  alongside the existing `release_ready` (kept unchanged, for compatibility):
  - `fail` if any stage status is `fail` **or** `totals.failed > 0` **or**
    `totals.timeout > 0` **or** `failures` is non-empty;
  - `incomplete` if not `fail`, and no `rehearse` stage passed, and no explicit
    `release_ready` was merged in;
  - `pass` otherwise (equivalent to today's `release_ready is True`).
  Also apply `_norm_status` in `add_report` so merged full reports normalise their
  stage statuses the way stage artifacts already do.
- `heart/readiness.py` — read `validation_outcome` when present:
  - `fail` → RED, existing wording and `hit("validation_failed")` (penalty 40);
  - `incomplete` → STALE, wording that **contains "release validation"** (e.g.
    `release validation incomplete: no rehearsal for current source`),
    `hit("validation_absent")` (penalty 15);
  - **discriminator absent** (legacy report) and `release_ready is False` → **RED**,
    unchanged. Fail closed.
- `heart/dashboard.py` — render `incomplete` as WARN rather than the current FAIL row
  (`dashboard.py:566`), and add `stale_reasons` to `to_dict()` (finding 4).
- `heart/checks/release_run.py` — print the outcome rather than labelling every
  non-true `release_ready` as `FAILED`.
- Docs that currently equate `false` with failure: `validate.py` schema comment and
  prose, `readiness.py` module contract and gate comment, `release_run.py` prose,
  `docs/release_validation.md`, `health_agent/capabilities.yaml`.

## Paired signal

`nightly-release` reported **blocked at gate — no release made** (11h before the sweep).
Same fact from the other side: the nightly cannot clear a gate this path can never open.

## Do not

- Do **not** re-dispatch the release to "clear" the RED. The publish path is not at
  fault; a re-dispatch costs ~70 minutes of CI and reproduces the identical verdict.
- Do **not** `--force` past it. The RED is spurious, but forcing hides the defect
  instead of fixing it.

## Acceptance

- A green integrate-only ingest no longer produces `red`; it produces a STALE reason
  whose text contains `release validation`, so `health.sh:176` routes it to the
  `validate` capability rather than `unknown`.
- A genuinely failing stage still produces RED `release validation FAILED (stage ...)`.
  `tests/test_readiness.py::test_validation_failed_is_red` must pass **unmodified** —
  it is the control.
- **Fail-closed cases stay RED.** Regression tests for each adverse signal the old
  proxy would have missed: `totals.failed > 0`; `totals.timeout > 0`; non-empty
  `failures`; a stage status synonym (`"failure"`) arriving via `add_report`; and a
  legacy report with `release_ready: false` and no `validation_outcome`.
- `stale_reasons` is present in `dashboard.to_dict()`, and the dashboard validation
  row is WARN (not FAIL) for `incomplete` while the header verdict is stale.
- `validate.py`'s schema docstring and the implementation agree afterwards, and no
  remaining doc in the list above equates `release_ready: false` with failure.
- Re-run `pyauto-brain health assess` afterwards: the live channel must re-grade off
  the already-ingested run 31769743408 **without re-dispatching any CI**.

## Original request (verbatim)

> can we fix this: Heart reads RED, score 45 — but the top blocker is misgraded, not a
> real failure. […] Root cause: heart/checks/release_run.py:152 auto-ingests the latest
> release-integrate run's stage report alone (validate.run([td]), no merge base).
> heart/validate.py:323-335 requires stages["rehearse"].status == "pass" unless an
> explicit release_ready is merged in. An integrate-only artifact can never carry a
> rehearse stage — so this path yields release_ready: false by construction, and
> readiness.py maps that to RED rather than a STALE evidence gap. […] The fix belongs in
> Heart (ingest the rehearsal artifact too, or grade a missing rehearse as STALE).
