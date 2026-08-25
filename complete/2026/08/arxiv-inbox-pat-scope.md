- issue: none — filed and shipped in one session, never routed through `/create_issue`.
- shipped: 2026-08-25 — PyAutoMind main 308d4fa (PR #317). The token half of the fix
  was a GitHub account setting, not a commit, and has no SHA.
- classification: bug (PyAutoMind + PyAutoMemory) — fifth in the paper-management line,
  and the first *regression* in it: it broke the feature #57 shipped the day before
  (`arxiv-inbox-tier`), on that feature's very first live run.
- summary: the nightly arXiv digest's inbox-filing step silently lost every paper it
  filed. `PAT_PYAUTOLABS` had write on the `*-template` repos `spawn_drift.yml` writes,
  not on `PyAutoMemory` itself, so the push 403'd — and the step swallowed it as a
  `::warning::` and exited 0. The run stayed green, Slack posted as normal, and the
  knowledge board read "nothing waiting", indistinguishable from a quiet day. Fixed by
  widening the PAT scope (human) and by making a denied push fail the step (PR #317).

- the failure, exactly: run 32803698132, 2026-08-25 03:03 UTC. Every step green. The
  inbox step's own log:

      inbox: appended:1, swept:0
      [main 3798728] inbox: appended:1, swept:0 (arXiv digest 2026-08-25 (Tue))
      remote: Permission to PyAutoLabs/PyAutoMemory.git denied to Jammy2211.
      fatal: ... The requested URL returned error: 403

  `append` worked, the commit was made, the push was refused three times, the commit
  died with the runner.

- root cause, and why it survived review: #57's record says "PyAutoMind's
  `PAT_PYAUTOLABS` already existed (spawn_drift.yml) — the cross-repo write needed no
  new secret". That checked the secret *existed*; it did not check its *scope* covered
  the new target. The inbox step was the first thing in the org needing
  `Contents: read-and-write` on `PyAutoMemory` itself. Nothing upstream of the push
  hints at it, because the clone succeeds — read is unrestricted on a public repo, so
  a green clone proves nothing about write.

- what the code change does: the step's declared design was already "expected-absent
  preconditions warn and exit 0; a genuinely broken script still fails the step". A
  denied push is the second case and was wired as the first. It now errors and exits 1;
  the missing-survivors and unset-PAT preconditions keep warn-and-exit-0. This does not
  weaken "a cross-repo failure must never cost the morning's post" — the step runs
  AFTER the Slack POST, so failing it cannot touch the digest, it only reddens the run.
  An auth failure also short-circuits the retry loop: that retry is for a concurrent-push
  race against the board and queue-action workflows, and a 403 cannot clear on a rebase.

- traps:
  - **a green clone is not write access.** The 403 lands on the push, several steps
    after the point a reader assumes auth was proven. Any future cross-repo step should
    be read as untested until a push has actually succeeded once.
  - **you cannot test `arxiv_papers.yml` from a branch that edits it.**
    `claude-code-action@v1` refuses to run when the workflow file differs from the
    default branch's copy ("Workflow validation failed") — and then exits **success**.
    The run continues with no `slack_payload.json`, the POST fails on the missing file,
    and every later step including the inbox filing is skipped. Worse, the error printed
    blames an expired `CLAUDE_CODE_OAUTH_TOKEN`, pointing at the wrong cause entirely.
    Cost a wasted dispatch here (run 32846505925); now recorded as a comment at the
    Claude step. Test by merging, or dispatch `main` and read the logs.
  - **the backfill window must be 168h, not 24h.** The lookback is submission-anchored
    (`arxiv_fetch.py` filters on `submittedDate`), so a paper announced today may have
    been submitted days earlier — the PyAutoMind#79 trap, reachable again through the
    recovery path. Both new error messages name 168 so the next reader does not
    re-derive it.
  - **adding a `draft/` file makes `dashboard.md` stale and reddens PR CI.** AGENTS.md
    says to regenerate; the `refresh` check enforces it. Regenerate *after* merging the
    base branch in, or the page is stale again the moment it lands.
  - `intake`'s `--apply` is a **global** flag, before the subcommand
    (`--mind . --apply dashboard`), while `--check` is a subcommand flag
    (`--mind . dashboard --check`). They are not symmetric.

- the backfill: `workflow_dispatch` on main, `lookback_hours=168`
  (run 32847233221) — `appended:2, swept:0`, pushed clean. `arxiv-inbox.md` now holds
  2608.23534 and 2608.18224, both stamped with the run date, so each got a fresh 7-day
  window rather than its original announcement date (`append` always stamps "today").

- validation: 197 PyAutoMind tests green; `lifecycle.py check` OK; `lifecycle.py index
  --check` OK; `intake dashboard --check` current; YAML parses and the changed step
  passes `bash -n`. PR #317 green on both `pull_request` runs.
- NOT proven live: the 403 path cannot be re-triggered now the token works, and the
  branch-testing trap means no branch dispatch can reach that step. Those lines are
  shell-syntax-checked and reasoned, not fired. The step is plain bash with no
  dependency on `claude-code-action`, so the scheduled 02:00 UTC run on main is the
  first genuine end-to-end exercise.
- still open: the board's empty state remains indistinguishable from a broken filing
  run — the very thing the `#papers` empty-day heartbeat exists to prevent, with no
  equivalent on the board. Split out as
  `draft/feature/pyautomemory/inbox_board_staleness_signal.md`.
- affected-repos:
  - PyAutoMind
  - PyAutoMemory

## Original prompt

_As first filed on 2026-08-25 (commit 501b862), before the PAT scope was widened and
the backfill ran. `lifecycle.py record --prompt` folds an `active/` prompt; this task
never entered `active/`, so the draft is folded in by hand._

# arXiv inbox never fills — PAT_PYAUTOLABS cannot write to PyAutoMemory

Type: bug
Target: PyAutoMemory
Repos:
- PyAutoMind
- PyAutoMemory
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-25

The first live run of the arXiv inbox filing step (PyAutoMemory#57, shipped
2026-08-24) failed on its first night. The Slack digest posted normally, the
knowledge board shows "nothing waiting — the nightly arXiv digest fills this",
and the workflow run is **green**.

## What actually happened

PyAutoMind run [32803698132](https://github.com/PyAutoLabs/PyAutoMind/actions/runs/32803698132),
2026-08-25 03:03 UTC. Every step succeeded; the inbox step's own log says:

```
inbox: appended:1, swept:0
[main 3798728] inbox: appended:1, swept:0 (arXiv digest 2026-08-25 (Tue))
 1 file changed, 1 insertion(+)
remote: Permission to PyAutoLabs/PyAutoMemory.git denied to Jammy2211.
fatal: unable to access 'https://github.com/PyAutoLabs/PyAutoMemory.git/': The requested URL returned error: 403
```

`scripts/inbox_actions.py append` worked. The commit was made. The **push** was
denied, three times, and the step exited 0 with a `::warning::`. The commit died
with the runner.

## Root cause

`PAT_PYAUTOLABS` does not grant write on `PyAutoLabs/PyAutoMemory`.

Its only prior consumer is `spawn_drift.yml`, which writes to
`PyAutoMind-template` and `PyAutoMemory-template` — the *generated view* repos,
not the live Memory. The inbox step is the first thing in the org to need
`Contents: read-and-write` on `PyAutoMemory` itself, and the completion record's
"PyAutoMind's `PAT_PYAUTOLABS` already existed (spawn_drift.yml) — the
cross-repo write needed no new secret" checked that the *secret* existed, not
that its *scope* covered the new target. The clone succeeded (read is
unrestricted), so nothing upstream of the push hinted at it.

## Remaining work (human-gated)

1. **Grant the scope.** On the fine-grained PAT behind `PAT_PYAUTOLABS`, add
   `PyAutoLabs/PyAutoMemory` with `Contents: read-and-write`. This is the whole
   fix; nothing in either repo needs to change for filing to start working.
2. **Backfill the lost night.** Today's surviving paper is not recoverable from
   the next scheduled run — the announcement band moves on and never revisits.
   Re-file it with a `workflow_dispatch` of `arxiv_papers.yml` carrying
   `lookback_hours=168`. **Not 24**: the lookback is submission-anchored
   (`arxiv_fetch.py` sorts and filters on `submittedDate`), and a paper
   announced today may have been submitted days earlier — the same trap as
   PyAutoMind#79. `append` dedupes against both the inbox and the reading queue,
   so an over-wide sweep is safe.

## Already fixed on this branch

`arxiv_papers.yml`'s inbox step no longer exits 0 on a failed push. The step's
design intent was already "expected-absent preconditions warn and exit 0; a
genuinely broken script still fails the step" — a 403 is the second case and was
wired as the first. The missing-survivors and unset-PAT preconditions keep their
warn-and-exit-0 behaviour.

The "must never cost the morning's post" constraint is untouched: the step runs
*after* the Slack POST, so failing it cannot cost the digest — it only turns the
run red, which is the signal the failure lacked.

An auth failure now also short-circuits the retry loop instead of burning three
identical attempts. The retry exists for a concurrent-push race against the
board and queue-action workflows; a 403 is not a race and will never clear on a
rebase.

## Follow-up worth filing separately

The board's empty state is indistinguishable from a broken filing run — exactly
the failure mode the `#papers` heartbeat was added to kill ("silence in #papers
always means a broken run, never a genuinely empty one", 2026-07-13). The board
has no equivalent: an inbox that is empty because nothing was filed reads the
same as one that is empty because arXiv was quiet. A "last filled: <date>" line,
or an explicit quiet-day marker written by the digest, would close it. That is a
PyAutoMemory board change and a separate task.
