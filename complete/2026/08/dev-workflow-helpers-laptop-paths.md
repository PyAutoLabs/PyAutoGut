Three defects in the dev-workflow helper scripts, one root cause: they resolve
paths under `$HOME/Code/PyAutoLabs`, which no cloud, web or CI session has. All
three were hit in sequence during the PyAutoBrain#224 session on 2026-08-10, and
each silently did the wrong thing rather than complaining.

- issue: PyAutoBrain#225 (closed completed)
- prs: PyAutoBrain#226 MERGED as `9a43f00` (guard + installer tests) ·
  PyAutoMind#178 MERGED as `8bb91f9` (prompt_sync)
- found: while shipping `reconcile-upstream-repo-mode` — see that record.

## 1. `prompt_sync_push` pushed a hardcoded `main`

`scripts/prompt_sync.sh`, the helper `create_issue` step 6 and `start_dev`
step 7 both tell an agent to call.

**The first write-up of this was WRONG and was corrected by measurement.** It
said "pushes Mind straight to `main`". `git push origin main` pushes the local
`main` **ref** — never the commit just made on a feature branch. Measured
against real bare remotes, the old behaviour splits by the state of local `main`:

| local `main` vs remote | what the old script did |
|---|---|
| **equal** — the normal case, a session that branched from it | push is a **no-op**, exits **0**, and the committed work **never leaves the machine**. The caller is told the sync succeeded. |
| **ahead** — unpushed commits on `main` | publishes those to remote `main`, unreviewed, **and still** leaves the branch work local. |

The first row is the common one and the quieter danger: in an ephemeral cloud
container, *"committed, reported synced, never pushed"* is silent loss. The
second is the review bypass. Same root cause; both fixed by pushing `HEAD`.
A detached HEAD is now refused rather than guessed at.

Sub-finding: `prompt_sync_push` had to drop its subshell. With the naive
`( ... ) && _push` shape the documented *"no-op if nothing is staged"* early
return falls through to the push, so a caller with no changes would push anyway.

## 2. `worktree_check_conflict` FAILED OPEN — the important one

`PyAutoBrain/bin/worktree.sh`. `worktree_list_claimed` returned `0` with empty
output when `active.md` could not be resolved under `$PYAUTO_MAIN`, so the guard
could not distinguish *"nothing claims this repo"* from *"I could not read the
registry"* — and answered the former.

`start_dev` step 6 and `start_library` step 1 both document this call and act on
its answer, so any session whose roots are not at the default path got a green
light it never earned, and two sessions could each be told the same repo was
free. This is the guard that serialises parallel agents.

Reproduced: the conflict check for `reconcile-upstream-repo-mode` was recorded
as clean having read nothing. Re-run with `PYAUTO_MAIN` set it worked and gave
the same verdict — but the first answer was worth nothing.

Now split into `worktree_registry_path` so the listing can signal failure in its
exit code; the guard reports `CANNOT VERIFY` with the paths it tried and returns
**3**. `--allow-missing-registry` proceeds unguarded and says so, never by
default. Exits `0`/`1` unchanged.

**`test_missing_active_md_yields_no_claims` asserted exactly the fail-open
behaviour** — it was pinning the defect. Rewritten to the corrected contract
with the reason in its docstring.

**Not a contradiction of the sibling policy:** `worktree_claim_is_stale` in the
same file is documented *"fail-open by design"*. It resolves `active.md` itself
and never calls `worktree_list_claimed`, so it is untouched. Both functions fail
toward **safety** — for staleness the safe answer is "don't remove", for
conflicts it is "don't start".

## 3. `test_skill_install.py` failed locally, passed in CI

**The first diagnosis was WRONG and was corrected before implementation.** It
blamed `install.sh` taking its `web-github` branch. The real cause: `PYAUTO_ROOT`
defaults to `bin/../..`, the repo's grandparent, so the installer looks for
`<grandparent>/PyAutoBrain/skills`. That resolves only when the checkout is
*named* `PyAutoBrain` and sits one level under the root — true on a laptop, and
true in GitHub Actions by coincidence (`/home/runner/work/PyAutoBrain/PyAutoBrain`),
but false for a clone at `pyautobrain`. The Brain skills were never scanned, so
`intake` was never installed and the asserted `SKIP intake (Codex skill` line
never printed. The environment line is a symptom of the same path resolution,
not the cause.

Fixed by pinning `PYAUTO_ROOT` at a fixture root whose `PyAutoBrain/` symlinks to
the checkout — the pattern the already-passing sibling test used. Does not narrow
coverage: PyAutoBrain CI only ever had PyAutoBrain's own skills on disk.

Consequence of the defect: Heart is unreachable from a cloud session, so
`ship_library` falls back to `pytest -x` and treats any failure as RED. These two
failures made that gate spuriously RED on #224 and cost a human acknowledgement
to override.

## Verification

- PyAutoBrain `main` after merge: **339 passed**, nothing ignored — green in a
  cloud session for the first time, which retires the false-RED ship gate.
- PyAutoMind: **134 passed** (127 + 7 new).
- Both fixes proven to FAIL against their pre-fix code, per the repo's "a check
  that cannot fail is decoration" principle: **5 of the 7** Mind tests fail
  against `origin/main`'s script; the guard was exercised across all five paths
  (missing registry → 3, `--allow-missing-registry` → 0 loud, claimed → 1, free
  → 0, same task resuming → 0).
- The Mind tests drive the real script against throwaway repos with **real bare
  remotes**, because only that shows *which ref actually moved*. Grepping the
  source for the string would pass on a script that still pushed the wrong
  branch by another route.
- Most striking pre-fix failure: from a **detached HEAD**, the old script pushed
  `main -> main`.

## Method note worth keeping

Two of the three write-ups above were wrong on first pass and were corrected by
*measuring the old code* rather than reading it. Both errors were the same shape:
a plausible cause that explained the symptom, adopted without running the
counter-experiment. For shell/git helpers, build the throwaway repo and look at
which ref moved.

Also: `python3 scripts/lifecycle.py check | tail -2` **discards the check's exit
status** — the shell sees `tail`'s. A DRIFT verdict was missed that way and a
chained commit ran anyway. Never pipe a drift check into `tail` in an `&&` chain.

## Original prompt

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

**Corrected 2026-08-10 after measuring the old script against real bare
remotes.** The first write-up of this defect said it "pushes Mind straight to
`main`". That is only half of it, and not the half that fires most often.
`git push origin main` pushes the local `main` *ref* — never the commit just
made on a feature branch. So the old behaviour splits by the state of local
`main`:

| local `main` vs remote | what the old script did |
|---|---|
| **equal** (the normal case — session branched from it) | push is a **no-op**, exits **0**, and the committed work **never leaves the machine**. The caller is told the sync succeeded. |
| **ahead** (unpushed commits on `main`) | publishes those commits to remote `main` — unreviewed work bypassing review — **and still** leaves the branch work local. |

The first row is the common one and the quieter danger: in an ephemeral cloud
container, "committed, reported synced, never pushed" is silent loss. The second
row is the review-bypass. Both are the same root cause and both are fixed by
pushing `HEAD`.

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

- `prompt_sync_push` on a non-`main` branch pushes **that branch** — so the
  committed work actually reaches the remote — and never advances `main` as a
  side effect. Both halves covered by their own test, since they are separate
  failures of the same bug.
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
