# /issue_cleanup — a reusable GitHub issue-tracker reconciliation door

## Original request

> do we have a skill to do a github issue clean up?

Answer: no. `/repo_cleanup` sweeps git debris (branches, refs, stashes, worktrees)
and stops there; `/community` handles *external* issues awaiting a reply;
`/create_issue` and `/update_issue` are single-issue primitives. Nothing owns
"audit the open issues, find the dead ones, close them". The user asked for an
ad-hoc sweep first, then this skill.

## What the ad-hoc sweep established (2026-07-28)

Swept 82 open issues across 18 repos; closed 35 (29 shipped-but-open + 6 obsolete
PyAutoCTI), leaving 47. The reasoning that survived contact is what this skill
must encode — a naive "has a PyAutoMind record → close it" rule was wrong **four**
separate ways, each found by verification rather than by inspection:

1. **Body mentions are not claims.** Grepping record *files* for an issue URL
   over-matches: `complete/2026/05/many-vis-prep-dft.md` mentions `PyAutoArray#326`
   in prose while its own `- issue:` header reads `(CI-triage cluster G, no GitHub
   issue)`. Only the header line is evidence.

2. **The header key carries the meaning — this is the load-bearing rule.**
   Across 800 records: `issue:` (630) means *this record completes that issue*.
   But `followup-issue:`, `follow-up-issue:`, `library-followup-issue:`,
   `parent-issue:`, `upstream-issues-filed:`, `plan:` (13 total) mean the
   **opposite** — the record *spawned* that issue and it is legitimately open.
   Matching loosely on `*issue*:` would close live follow-ups.

3. **Annotations override.** Records annotate deliberate exceptions inline:
   `(open — findings census stays as reference)`, `(STAYS OPEN — real finding +
   resumable fit)`, `(STAYS OPEN for the optional model-parity fit leg)`,
   `(both stay OPEN for parked design work only)`. Any `open` token in the
   annotation means hands off. Note these appear on `plan:` lines too, not just
   `issue:` lines.

4. **A record in `complete/` does not mean the work completed.**
   `ep-hierarchical-scale-collapse.md` carries `Status: issued` — it filed
   `PyAutoFit#1405` and reported two defects on it. The record is complete; the
   *issue* is a live bug. Read the status field, not the directory.

Corroborating detail: `PyAutoReduce#8`'s record already said `(CLOSED)` while
GitHub had it open — closes do silently fail to land, which is part of why the
reconciliation is worth automating.

## Scope

Mirror `/repo_cleanup`'s proven shape: **audit → bucketed dashboard → per-bucket
human confirmation → execute → recap**. Never close without confirmation; never
close a bucket the human did not name.

Buckets, in the order the sweep found useful:

- **A — shipped, closable.** Record claims the issue via a *completing* header
  key, no `open` annotation, and a merged PR confirms it. Require **two
  independent legs** (record header + merged PR). The PR leg needs both paths:
  the GitHub timeline cross-reference, and a PR number named in the record body
  (12 of 29 had only the latter — timeline alone under-reports).
- **B — weak evidence.** Record exists but the evidence fails a leg. Report; do
  not close.
- **C — deliberately open.** Annotation says so. Never touch.
- **D — in flight.** Present in `active.md` / `parked.md`.
- **E — external.** Author is not the maintainer → `/community`, never this door.
- **F — unreconciled.** No record at all. The real backlog. Sub-split by age;
  the ancient tail (2018–2019 PyAutoCTI, 2022 PyAutoHands) needs per-issue
  judgment, not a bulk rule — see below.

## Obsolescence needs a real check, not an age threshold

The 8 oldest issues split on evidence, not on age. The 6 PyAutoCTI ones
(2693–2785 days) named `FrameGeometry`, `CIFrame`, `CIData`, `ci_data_analysis`,
`ci_pattern`, `phase.py`/`pipeline` — a grep of `autocti/` returns **zero** for
every one, so the CTI resurrection removed that surface entirely and they were
closed `not_planned`. `PyAutoHands#16` (test against pre-release deps) and `#17`
(fail the build if RTD docs fail) are the same vintage (~1337 days) but were
**left open** — no `--pre` workflow and no RTD gating exist in
`PyAutoHands/.github/workflows/`, so they are still-valid unimplemented asks.
Age correlates with obsolescence; it does not establish it. The skill must probe
whether the named API/infra still exists.

## Mechanics

- `gh issue close` is broken in this environment. Comment first, then
  `gh api -X PATCH repos/<owner>/<repo>/issues/<n> -f state=closed -f state_reason=<completed|not_planned>`.
- Use `state_reason=completed` for bucket A, `not_planned` for obsolete.
- Every close leaves a comment naming its evidence (record path + PR) so the
  decision is auditable and reversible.
- Skip pull requests: the issues endpoint returns PRs too — filter
  `select(.pull_request == null)`.
- Bot-authored self-refreshing issues (`[url-check]`, `[heart-health]`) should be
  recognised and excluded from staleness ranking.

## Deliverables

1. `PyAutoBrain/skills/issue_cleanup/` — canonical skill body plus a
   `reference.md` for dashboard layout and per-bucket execution, matching how
   `repo_cleanup` is laid out.
2. Wire it into `PyAutoBrain/skills/COMMANDS.md` routing and symlink it into
   `~/.claude/commands` so `/issue_cleanup` resolves.
3. Add an issue-tracker line to the `/wake_up` digest so drift surfaces daily
   rather than at 82-issue depth.

## Notes

- Decision-and-execute door, like `/repo_cleanup` — it reasons and acts on the
  tracker; it does not edit source.
- Worth considering: reconciliation is cheap and read-only, so the audit half
  could run unattended (in `/wake_up`) while every close stays human-gated.
