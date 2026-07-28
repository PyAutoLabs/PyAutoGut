- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/174
- library-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/175 (MERGED c97ad7f)
- followup-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/176 (MERGED e74db88 — committed .claude/.codex discovery refresh)
- completed: 2026-07-28
- repos: PyAutoBrain
- notes: Built `/issue_cleanup` (`$issue-cleanup` on Codex), the missing GitHub issue-tracker reconciliation door — the issue-tracker counterpart to `/repo_cleanup`'s git-debris sweep, same audit → bucketed dashboard → per-bucket human confirmation → execute → recap shape. Nothing had owned this: `/repo_cleanup` stops at branches/refs/stashes/worktrees, `/community` handles EXTERNAL users' issues awaiting our reply, `/create_issue` + `/update_issue` are single-issue primitives. Preceded by an ad-hoc sweep that took the trackers **82 open across 18 repos → 47**: closed 29 shipped-but-still-open (two-leg verified) + 6 obsolete 2018–2019 PyAutoCTI (`not_planned`).

  THE LOAD-BEARING RULE: the PyAutoMind record header **KEY** decides closability. `issue:`/`issues:` (636 uses) mean the record COMPLETES that issue; `followup-issue:`/`follow-up-issue:`/`library-followup-issue:`/`parent-issue:`/`upstream-issues-filed:`/`issued:`/`plan:` (13 uses) mean the record SPAWNED it and it is legitimately open. Completing keys are an ALLOWLIST so new spawn-style keys fail closed — a loose `*issue*:` match looks right on a spot-check and silently closes live follow-ups.

  FIVE failure modes of the naive "record references it → close it" rule, each found by verification not inspection. (1) Body mentions ≠ claims — `many-vis-prep-dft.md` discusses PyAutoArray#326 in prose while its own `- issue:` header reads "(CI-triage cluster G, no GitHub issue)". (2) The header key, above. (3) Inline `(open …)`/`(STAYS OPEN …)` annotations override, and appear on `plan:` lines too, not just `issue:`. (4) A record in `complete/` can carry `Status: issued` — it FILED the issue rather than completing it (`ep-hierarchical-scale-collapse.md` → PyAutoFit#1405, a live bug); read the status field, not the directory. (5) A phase-scoped claim ("(Phase 5 item 4)") completes a PIECE not the issue — four records each claim a Phase-5 item of PyAutoBrain#130 and none establishes it is done. Corroborating sixth: PyAutoReduce#8's record already said "(CLOSED)" while GitHub had it open — closes silently fail to land.

  RULES 1 AND 4 WERE CAUGHT BY THE SKILL'S OWN REGRESSION BAR, NOT BY THE SWEEP — which is why the bar ships with the skill rather than being a one-off check. Rule 1 was too loose (matching any `- word:` line re-admits prose, because records use `- notes:` for paragraphs citing issue URLs freely; PyAutoGalaxy#417 is cited ONLY there); Rule 4 did not exist. The bar pins the post-sweep state — 47 open / A=0 / B=1 / C=7 / spawn-held=3 / D=6 / E=8 / F=22 — and names both traps by fixture: PyAutoGalaxy#417 must land in F (or the header allowlist regressed) and PyAutoBrain#130 must land in B (or umbrellas are being closed on partial evidence). 11/11 PASS at b42a831.

  AGE ≠ OBSOLESCENCE. The 8 oldest issues split on evidence, not age: six PyAutoCTI (2693–2785 days) named FrameGeometry/CIFrame/CIData/ci_data_analysis/ci_pattern/phase.py — grep of `autocti/` returns ZERO after the CTI resurrection, so closed `not_planned`; PyAutoHands#16 (pre-release dep testing) and #17 (fail build if RTD fails) are the same ~1337-day vintage but stayed OPEN — no `--pre` workflow and no RTD gating exist, so they are still-valid unimplemented asks. The skill must probe whether the named API/infra still exists.

  MECHANICS: `gh issue close` is broken here — comment, then `gh api -X PATCH … -f state=closed -f state_reason=<completed|not_planned>`. Filter `select(.pull_request == null)` or PRs inflate every count. The PR evidence leg needs BOTH the timeline cross-reference AND a PR named in the record body — 12 of 29 had only the latter, so timeline alone under-reports.

  HARNESS GENERALITY: the skill is the portable half of the cleanup pair — pure `gh` + reading `PyAutoMind/`, no local library checkout — so it runs on Codex and mobile where `/repo_cleanup` cannot. Body uses `$verb` notation with one explicit dual-notation line. `SKILL.md` frontmatter `name:` MUST stay hyphenated (`issue-cleanup`) because Codex takes its skill name from it. PR #176 then fixed pre-existing drift the install uncovered: `--write-project-discovery` had not been re-run since the **community** and **eyes** doors landed, so those two AND `issue_cleanup` were missing from the committed per-repo `.claude`/`.codex` discovery tree — the tree that registers doors in cloud/web sessions, where the user-level `~/.claude`/`~/.codex` symlinks do not travel. Three doors were invisible on web/Codex despite working locally.

  TRAP CONFIRMED: `bin/install.sh` with an UNKNOWN flag falls through to a FULL install (default case), and a full install run from a worktree repoints `~/.claude` at that worktree. `--write-project-discovery` and `--check-project-discovery` short-circuit with `exit 0` before the user-level install, so they are safe from anywhere. Run the plain (no-flag) install only from the canonical checkout.

  ALSO: Brain's Feature Agent scored this large/split-into-phases — OVERRIDDEN to single phase (one skill, one repo, reasoning already settled by the sweep); its "public-API change may ripple downstream" risk is a false positive for a skill body. Claimed PyAutoBrain over a STALE guard-followups worktree claim (all 3 of its PRs had merged 12:53; that task has since cleaned itself up fully).

  LEFT OPEN DELIBERATELY: PyAutoBrain#130 (umbrella, bucket B — needs a human to say whether Phase 5 is done); PyAutoHands#16/#17; the 7 bucket-C annotated issues; the 22-issue bucket-F backlog. An unregistered PyAutoLens worktree on `docs/paper-jax-intro-revision` (2 pushed commits, in no Mind registry) was found living inside this task's worktree root and was NOT removed — it needs its own adjudication.

## Original prompt

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
