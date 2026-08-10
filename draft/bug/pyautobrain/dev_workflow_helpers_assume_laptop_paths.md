# The dev-workflow helpers assume a laptop checkout and misbehave without it — one of them fails open

Type: bug
Target: PyAutoBrain
Repos:
- PyAutoBrain
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: planned

Three defects, one root cause: the dev-workflow helper scripts resolve paths
under `$HOME/Code/PyAutoLabs`, which does not exist in a cloud, web or CI
session. All three were hit in a single session on 2026-08-10 while shipping
PyAutoBrain#224, and each one silently did the wrong thing rather than
complaining.

`Priority: high` because #2 is a **safety** defect, not an inconvenience: a
guard that returns "all clear" when it cannot read its input is worse than no
guard, because the workflow documents it and skills act on its answer.

## 1. `prompt_sync_push` hardcodes `git push origin main`

`@PyAutoMind/scripts/prompt_sync.sh` — the helper every Mind-writing skill is
told to call:

```bash
prompt_sync_push() {
  ...
  git commit -m "$subject" && \
  git push origin main )
}
```

`create_issue` step 6 and `start_dev` step 7 both instruct the agent to call it.
A branch-scoped session — a cloud session with a designated branch, or any
PR-based flow — that follows the documented steps verbatim pushes Mind straight
to `main`, bypassing review entirely. In the 2026-08-10 session this was caught
only because the branch requirement was read carefully and the helper inspected
before use; the documented path would have violated it.

Fix: push the current branch (`git push -u origin HEAD`), or refuse with a clear
error when the checkout is not on `main`. Do not leave this to operator
vigilance — that is the same reasoning that motivated the `pre_build` staging
fix (PyAutoHands#233).

## 2. `worktree_check_conflict` FAILS OPEN — the important one

`@PyAutoBrain/bin/worktree.sh` — `worktree_list_claimed` reads `active.md` under
`$PYAUTO_MAIN` (default `$HOME/Code/PyAutoLabs`):

```bash
if [[ ! -f "$active" ]]; then
  return 0
fi
```

No file → returns 0 → `worktree_check_conflict` reports **no conflict**. So in
any environment where the roots are not at the default path, the guard cannot
distinguish "nothing claims this repo" from "I could not read the registry", and
answers the former.

Reproduced 2026-08-10: `worktree_check_conflict reconcile-upstream-repo-mode
PyAutoBrain PyAutoMind` returned 0 and was recorded as a clean conflict check.
Re-run with `PYAUTO_MAIN=/workspace` it actually worked and returned the same
verdict — but the first answer was worth nothing, and if a conflict HAD existed
the session would have started conflicting work with a green light.

This is the guard that serialises two agents wanting the same repo. Two sessions
claiming one repo is exactly the class of collision the worktree flow exists to
prevent.

Fix: fail closed. If the registry cannot be resolved, return non-zero with a
message naming the path it tried, so the caller stops rather than proceeds. A
`--allow-missing-registry` escape hatch is acceptable only if it must be passed
explicitly.

## 3. `test_skill_install.py` fails locally but passes in CI

`@PyAutoBrain/tests/test_skill_install.py` — two tests assert on installer output
that only appears on the local-dev path:

```python
assert "SKIP intake (Codex skill" in result.stdout
```

`@PyAutoBrain/bin/install.sh` already knows the difference — it prints
`Environment: local-dev (PyAuto repos detected)` or `Environment: web-github /
ci-only (clone roots on demand)` — and on the web-github path it skips the
skill-symlink work these tests assert on. So they fail in any cloud session and
pass in real CI.

Consequence, observed: PyAutoHeart is unreachable from a cloud session, so
`ship_library` falls back to `pytest -x` as the ship gate and treats any failure
as RED. These two failures made that gate spuriously RED on PyAutoBrain#224 and
cost a human acknowledgement to override. CI on that PR then went green on both
legs, confirming the diff was never implicated.

Fix: skip (not fail) when the installer reports the web-github path. The tests
are asserting local-dev behaviour and should say so.

## The unifying point

`install.sh` already detects and prints its execution environment, and
`WORKFLOW.md` already names the environments (`local-dev`, `web-github`,
`ci-only`). The helpers should consult that same notion and either adapt or fail
closed. None of the three should silently do the wrong thing.

## Acceptance

- `prompt_sync_push` on a non-`main` branch pushes that branch, or refuses;
  it never pushes to `main` from a branch-scoped checkout. Covered by a test.
- `worktree_check_conflict` returns **non-zero** when it cannot resolve
  `active.md`, naming the path it tried. Covered by a test that points
  `$PYAUTO_MAIN` at an empty dir. The "registry present, no claim" case still
  returns 0, so the existing behaviour is unchanged where it worked.
- `test_skill_install.py` passes on both paths — skipping, with a reason, when
  the installer reports web-github; still asserting fully on local-dev.
- `pytest tests/` is green in a cloud session, so the `ship_library` fallback
  gate stops producing false REDs.

<!-- filed 2026-08-10 from the PyAutoBrain#224 session, where all three were hit
     in sequence: (1) caught before it fired, (2) recorded a vacuous clean
     conflict check that had to be corrected, (3) made the ship gate RED. -->
