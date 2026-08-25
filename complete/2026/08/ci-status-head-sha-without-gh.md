- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/178
- completed: 2026-08-25
- library-pr: PyAutoHeart#180 (merged a570d0a -> main)
- what shipped: `ci_head_sha` in `heart/checks/ci_status.sh` — the `main` HEAD sha now falls back to an anonymous `git ls-remote` when `gh` cannot supply it. `gh` stays first (unchanged dev-box behaviour, and the only source that can read a private repo); the fallback needs neither authentication nor a session repo attachment, so it works exactly where `gh` cannot.
- why: a cloud `/health` run cleared all three named evidence gaps and readiness still reported STALE on six reasons, every one of them caused by `gh` being absent from the session container. This half clears the one blocking the release gate — `release validation source unconfirmed (current HEADs unknown)`.
- the insight that made it small: `gh` is only **transport**. The judgment already lives in `ci_status.py`, which reads a REST-shaped `{"workflow_runs": [...]}` payload plus a `--head-sha` argument. Nothing needed reimplementing.
- why it works standalone: `build_sidecar` writes `head_sha` unconditionally (`ci_status.py:274`), independent of the runs fetch error — so the CI row keeps reading `unavailable` until the conclusions half lands, but the release gate can already confirm `commit_shas`.
- bounded on purpose: this runs inside the <30s tick. `GIT_TERMINAL_PROMPT=0` stops a private repo blocking on a credential prompt; `timeout` caps a stalled connection.
- portability trap found in review, not in CI: `timeout` is coreutils. macOS has it only as `gtimeout`, and only with coreutils installed. Resolved once at source time to `timeout`/`gtimeout`; where neither exists the fallback is **skipped** rather than run unbounded — a stalled `ls-remote` inside the tick is a worse failure than the empty sha that is already today's answer.
- validation: 635 tests pass (8 new for `ci_head_sha`, stubbing `gh`/`git` on PATH per the `test_verify_install_script.py` precedent). End-to-end in a gh-less container: 25 repos scanned in 3.3s, all five release-gate libraries resolving their real shas, and the source-unconfirmed reason gone from readiness.
- CI caught a real defect, not a flake: the new test defaulted its repo argument to a real owner/name, which the tenant-firewall check correctly rejected for an unlisted organ file. Genericised rather than allowlisted — the allowlist's own comment says never to grow it casually, and `gh`/`git` are both stubbed in that test so a real repo string bought nothing.
- trap for later: a shallow `--depth 1` clone sets `remote.origin.fetch` to `main` only, so a pushed feature branch gets no remote-tracking ref and `@{u}` fails — which reads as "unpushed" to tooling even when the remote branch exists. Widen the refspec before trusting an ahead/behind count in a cloud session.

## Original prompt

# Read ci_status HEAD shas without gh, via git ls-remote

Type: feature
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

# Read ci_status HEAD shas without gh, via git ls-remote

Type: feature
Target: PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: normal

## Problem

`heart/checks/ci_status.sh` reads each repo's `main` HEAD sha with
`gh api repos/<owner>/<name>/commits/main --jq .sha`. On a mobile/cloud session
`gh` is not installed, so the sha comes back empty. Readiness then cannot
confirm an ingested release-validation report against the live HEADs and reports
`release validation source unconfirmed (current HEADs unknown)`.

Observed 2026-08-25 in a cloud session: all three named evidence gaps were
cleared, yet readiness stayed STALE on this reason alone.

## Change

Read the sha with `git ls-remote <url> refs/heads/main` instead of `gh`, either
as the primary source or as the fallback when `gh` is absent.

This needs no authentication and no session repo attachment — it works on public
repos over the plain git lane. Verified in a cloud session for all five
release-gate libraries, including one whose `add_repo` attachment was refused
outright.

Keep it cheap: `ls-remote` with an explicit ref pattern is a single ref read, no
clone, and it slots into the existing `check_one_repo_ci` parallel fan-out, so
the `<30s` tick budget is unaffected. Preserve the current graceful degradation —
an empty sha on failure, never a fabricated one.

Scope is the sha only. The CI *conclusions* half still needs the Actions API and
is a separate task.

## Acceptance

- With `gh` absent, `pyauto-heart tick` records a real `head_sha` for each polled
  repo and readiness no longer emits `release validation source unconfirmed
  (current HEADs unknown)`.
- The tick stays inside its `<30s` budget.
- A failed `ls-remote` still yields an empty sha, not a wrong one.

<!-- formalised by the Intake (Conception) Agent on 2026-08-25 from file:/tmp/claude-0/-home-user/1e0c2b0b-8607-5d9d-8871-ab7a769bb699/scratchpad/p1_lsremote.md -->
