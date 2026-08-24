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
