- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/autocti_assistant/issues/24
- prs:
  - https://github.com/PyAutoLabs/autocti_assistant/pull/23 (merged)
- summary: |
    `wiki-currency` had been red on `autocti_assistant` main independently of any
    PR, so every PR against the repo opened already-red. Identified the failing
    sub-check, established it was baseline staleness rather than a stale doc
    claim, regenerated the baseline, and fixed two defects that had made the
    check undiagnosable.

## Which sub-check failed, and how it was found

The workflow redirects every check into `drift-report.md`, so the job log never
names the failure. The drift-report artifact is served from a blob host this
session's network policy blocks (`CONNECT tunnel failed, response 403`), so the
run was **reproduced locally** instead: the CTI stack built exactly as the
workflow builds it (autonerves/autoarray/autofit 2026.8.17.1 from source `main`,
autocti 2024.11.13.2, arcticpy 2.6 compiled from sdist).

Exactly one of the five fails:

| check | result |
|---|---|
| `--check-version` | FAIL — API DRIFT vs baseline (generated 2026-07-23) |
| `--scope all` | pass — 31/31 cited symbols resolve, 0 missing |
| `--lint-idioms` | pass — 51 files, no defunct idioms |
| `--check-provenance` | pass — 8 pages, 0 errors, 9 warnings |
| `--check-citations` | pass — 29 citations, 0 missing paths |

## Staleness, not a stale claim — and how that was proved

The prompt warned against regenerating the baseline to paper over a genuine
divergence, so this was checked rather than assumed. Worktrees were created at
the baseline's own commits (PyAutoFit `daa4e39`, PyAutoArray `85c57eb`, both
2026-07-23), the libraries installed from them, and the public symbol sets
diffed against today's `main`:

```
autoarray  120 -> 121   + InterpolatorDelaunayNN, validate
                        - TransformerNUFFTPyNUFFT
autofit    149 -> 159   + AbstractClipper, AbstractScaler, ApproxUpdater,
                          ClipperNone, ClipperPriorBox, DynamicUpdater,
                          FactorUpdater, NSS, ScalerNone, ScalerPriorWidth,
                          SimplerUpdater
                        - database
```

Two symbols were **removed**, so the drift was not blindly additive. But neither
is cited: `TransformerNUFFTPyNUFFT` appears nowhere in `wiki/`, `skills/` or
`modes/`, and the `database` matches are prose about the workspace's
`advanced/database/` script directory, not the `autofit.database` symbol (no
`af.database` / `from autofit import database` anywhere). `--scope all` agrees:
*"All cited symbols resolve cleanly. No drift detected."* And `autonerves`,
`autocti` and `autocti.plot` hashes were byte-identical — the surfaces this
assistant documents had not moved at all.

Baseline regenerated; all five checks then pass locally, and `wiki-currency`
came back green in CI on the PR.

## Trap: the report was lying about what it installed

The drift report printed `stack_version: latest released` whenever the input was
empty. That is **false** on the native PR/dispatch path — the install step
builds the stack from the `sources/` `main` clones, and the workflow's own
comment explains why (the CTI release train is not wired, so PyPI would grade
the modern docs against a pre-resurrection wheel).

This mislabel is what sent the filing prompt's diagnosis to the wrong
hypothesis: it reasoned "the workflow audits against latest released, so it rots
on a clock" and pointed at release timing. The real clock is the **libraries'
`main` branches**, which move far faster than releases. Both input descriptions
and the report header now state what is actually installed.

The report also recorded **no source refs at all**, so a red run could not be
diagnosed after the fact. The clone step now writes each source tree's short SHA
into the report header.

## Recommended against pinning to a released stack version

The prompt asked whether pinning would stop the check rotting on timing alone.
It should not be done: autocti's PyPI release is the pre-resurrection
`2024.11.13.2`, so pinning would grade today's docs against an API predating the
work they describe — vacuously green, which is worse than noisily red.

## Open follow-up (deliberately not taken)

`--check-version` gates on a hash of the **entire** public surface of autoarray
and autofit, almost none of which this assistant documents. This red was 12
additions and 2 removals, none touching a cited symbol — so the new baseline
will rot the same way within weeks, on any `main` merge that exports a new name.
Meanwhile `--scope all` already answers the question that matters and is immune
to that noise.

Worth deciding: gate `--check-version` on **removals** only (additions
informational), or accept that `--scope all` subsumes it as a gate. That changes
what the check means, so it was left as a proposal under the task's `supervised`
autonomy rather than made unilaterally. Recorded on autocti_assistant#24.

## Unblocked

autocti_assistant#21 had been held unmerged at `/prm` because of this red.

## Original prompt

# wiki-currency is red on autocti_assistant main — API baseline has drifted

Type: bug
Target: autocti_assistant
Repos:
- @autocti_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

The `wiki-currency` workflow fails on `autocti_assistant` **main**, independently
of any open PR. Every PR against the repo therefore opens already-red, which
trains reviewers to ignore the check.

## Evidence it is main, not a PR

Found while shipping `testmode-assertion-note-removal` (autocti_workspace#24).
PR autocti_assistant#21 — a four-line prose deletion — showed `wiki-currency`
red. Dispatched the same workflow on `main` at `960fdd1c`
(run 32762029277): **also failed**, same job, same step, same
`##[error]wiki-currency drift detected` line.

The drift-report artifact sizes settle it: 964 bytes on the PR
(run 32761217701) vs 961 bytes on main. The report header carries
`- assistant_ref: \`<ref>\``, and `refs/pull/21/merge` (18 chars) minus
`refs/heads/main` (15 chars) is exactly the 3-byte delta — so every drift
*finding* in the two reports is byte-identical. The PR contributes nothing.

## Likely cause

`.github/workflows/wiki-currency.yml` audits against
`stack_version: latest released`, so the check is time-dependent: a new
PyAutoCTI/PyAutoFit/PyAutoArray release can turn it red with no commit to this
repo. `wiki/core/api_audit_baseline.json` was last regenerated 2026-07-19
(commit `2bb0766b`, the PyAutoConf→PyAutoNerves sweep) against
`autonerves/autoarray/autofit 2026.7.9.1` + `autocti 2024.11.13.2`. Releases
since then — including PyAutoFit's, which now contains 438f56fac — are the
prime suspect. That 2026-07-19 run is also the **only** green `wiki-currency`
run main has ever had.

## Work

1. Read the failing sub-check from the `wiki-drift-report` artifact — the
   workflow redirects each check's output into `drift-report.md`
   (`>> "$REPORT" 2>&1`), so the job log never names which of the five failed
   (`--check-version`, `--scope all`, `--lint-idioms`, `--check-provenance`,
   `--check-citations`). Download the artifact; do not try to infer it from the
   log.
2. If it is baseline drift, regenerate with
   `python autoassistant/audit_skill_apis.py --write-baseline` against the same
   stack the workflow builds, and commit the new
   `wiki/core/api_audit_baseline.json`. Note this needs `arcticpy` (C++ sdist,
   `libgsl-dev` + toolchain), so it is not doable from a plain web session.
3. If it is a real doc/API divergence, fix the skills prose instead — do not
   regenerate the baseline to paper over a genuine stale claim.
4. Consider whether pinning the audit to a released stack version, rather than
   `latest released`, would stop the check going red on release timing alone —
   a check that rots on a clock trains people to ignore it.

## Blocks

autocti_assistant#21 (docs: remove the resolved TEST_MODE artifact sentence)
was held unmerged at /prm because of this red. It is a clean doc-truth fix with
`clone-boundary` green; it should merge once this is resolved, or be merged
deliberately over a known-bad base.
