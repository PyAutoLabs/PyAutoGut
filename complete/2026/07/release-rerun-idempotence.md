## release-rerun-idempotence
- completed: 2026-07-25
- summary: Release re-runs made idempotent (PyAutoHands#198 e662af4, merged): peeled-tag remote check (skip if same commit, loud-fail on mismatch), PyPI --skip-existing + 3-attempt retry, workspace tag step matched; exercised against scratch repos.

## Lifecycle note

Record backfilled 2026-08-06 (draft resolution-banner sweep): the work shipped with a RESOLVED banner written into the draft, but the prompt never advanced out of draft/; retired here dated by resolution day.

## Original prompt (release_rerun_idempotence)

> **RESOLVED 2026-07-25 — implemented as PyAutoHands#198 commit e662af4
> (merged).** Tag step now remote-checks with peeled-tag comparison (skip if
> same commit, loud-fail on mismatch), PyPI uploads gain --skip-existing + a
> 3-attempt retry, and the workspace tag step got the same treatment. Tag shell
> exercised against scratch repos on all three branches. 'Re-run failed jobs'
> on a partial release now completes without tag surgery.

# Make release.yml re-runnable: idempotent Tag step + skip-existing uploads

Type: maintenance
Target: ci
Repos:
- @PyAutoHands
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## Incident (2026-07-25)

The first fully-green scheduled nightly after the heart-to-green push dispatched
the live 2026.7.25.1 release. 23 of 24 jobs succeeded; the PyAutoArray
`release` job's `twine upload` died on a transient `upload.pypi.org` connect
timeout — AFTER its Tag step had pushed the 2026.7.25.1 tag. Result: a
**partial release** (all packages on PyPI at .1 except autoarray), and because
the Build step pins exact sibling versions, `pip install autolens` was broken
for end users.

Recovery exposed the structural gap: **"re-run failed jobs" cannot ever
succeed**, because the frozen Tag step re-runs `git tag -a && git push --tags`
against a tag that already exists → rejected → the job dies before Build/Upload.
Tag deletion was attempted as a workaround and was itself blocked (403 — tag
protection / credential scope), leaving a full re-release at `minor_version=2`
as the only remedy (which worked: 2026.7.25.2 consistent on PyPI).

## Task

Make a failed live release recoverable by re-running its failed jobs:

1. **Tag step idempotence** (`.github/workflows/release.yml`, `release` job):
   if `refs/tags/$VERSION` already exists on the remote **and points at the
   checked-out commit**, skip tagging and proceed; if it exists pointing at a
   *different* commit, fail loudly with a clear message (that is a real
   inconsistency, not a retry).
2. **Upload idempotence**: `twine upload --skip-existing` (PyPI and TestPyPI
   legs), so a re-run that rebuilds already-published artifacts proceeds to the
   not-yet-published ones instead of failing on duplicates.
3. Consider a bounded retry (2-3 attempts, backoff) around the twine upload
   itself — the incident's root cause was a single transient connect timeout.
4. Verify with a rehearsal-mode run plus a deliberately re-run job.

## Acceptance

- "Re-run failed jobs" on a partially-failed live release completes the
  remaining uploads with no manual tag surgery.
- A tag/commit mismatch still fails loudly (no silent re-pointing).
- Nightly driver behaviour unchanged (it dispatches the same workflow).
