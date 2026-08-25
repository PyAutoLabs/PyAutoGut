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

## Resolved 2026-08-25

1. **Scope granted.** `PAT_PYAUTOLABS` now carries write on
   `PyAutoLabs/PyAutoMemory`. No code change was needed for filing to work.
2. **Backfill done.** `workflow_dispatch` of `arxiv_papers.yml` on `main` with
   `lookback_hours=168`
   ([run 32847233221](https://github.com/PyAutoLabs/PyAutoMind/actions/runs/32847233221))
   filed `appended:2, swept:0` and pushed clean. PyAutoMemory `arxiv-inbox.md`
   now holds:

   ```
   2026-08-25 — Strong Lensing Cosmology with Population-level Calibrated Neural Ratio Estimation — 2608.23534
   2026-08-25 — Mapping the Information Geometry of an Unresolved Dark Matter Population using a Differentiable Strong Lensing Simulator — 2608.18224
   ```

   168, not 24: the lookback is submission-anchored (`arxiv_fetch.py` sorts and
   filters on `submittedDate`), so a paper announced today may have been
   submitted days earlier — the PyAutoMind#79 trap. `append` dedupes against
   both the inbox and the reading queue, so an over-wide sweep is safe, and it
   stamps every backfilled line with *today's* date, giving each a fresh 7-day
   window rather than its original announcement date.

## Trap: you cannot test this workflow from a branch that edits it

The first backfill attempt was dispatched from this branch so the new
fail-loudly path would be exercised. It cannot be. `claude-code-action@v1`
refuses to run when the workflow file differs from the default branch's copy:

```
Skipping action due to workflow validation: Workflow validation failed. The
workflow file must exist and have identical content to the version on the
repository's default branch.
```

The action then **exits `success`**, so the run continues with no
`slack_payload.json`, the POST step fails on the missing file, and every later
step — the inbox filing included — is skipped. Consequence for anyone editing
`arxiv_papers.yml`: a branch dispatch exercises the fetch and the band self-test
and nothing past them, and its failure says "the Claude summarise step failed to
write it (check for an expired CLAUDE_CODE_OAUTH_TOKEN)", which points at the
wrong cause entirely. Test workflow-file changes by merging them, or dispatch
`main` and read the step logs.

Consequence for this change specifically: the 403 path it fixes cannot be
re-triggered now that the token works, so the new branch is shell-syntax-checked
and reasoned, not live-fired. The step it touches is plain bash with no
dependency on `claude-code-action`, so a merge to `main` is what proves it.

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
