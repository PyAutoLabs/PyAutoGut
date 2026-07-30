Made the worktree-drift check produce totals a human can act on, killing the
"2 orphan / 2 missing / 66 dirty" noise class.

- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/123 (auto-closed)
- pr: PyAutoHeart#124 (`7d852a78d`) — merged unchanged (tree diff 0); CI green
- fixes (CI/release audit finding E): (1) claims are path-tested directly with
  `~` expansion, wherever they point — an existing `.codex-worktrees/<task>`
  claim no longer reads "missing" forever, and claims outside the wt root are
  tracked, not orphaned; claim parsing accepts only path-shaped values
  (parked.md carries prose like `worktree: none (…)`); (2) the task-dirt scan
  skips the symlinks worktree_create installs, and dirty CANONICAL checkouts
  are deduped by resolved path into a new `canonical_dirty` category — counted
  once, WARN never RED (a user's canonical working state is not task drift;
  this multiplied into the "66 dirty"); (3) parked.md worktrees get a `parked`
  label, excluded from orphans.
- shape: heredoc python → testable `heart/checks/worktree_drift.py` (pure
  scan() + main()); worktree_drift.sh is a thin shim (tick.sh contract kept);
  dashboard renders the new categories; capabilities impl updated.
- live validation: only the genuinely-stale `vacuous-jax-assertions` claim
  surfaced as missing (its worktree really was removed while PRs await merge —
  fix that entry when they land); the concurrent session's real uncommitted
  work attributed correctly; 7 canonical checkouts counted once each.
- suite 328 passed (8 new tests over synthetic git trees).

## Original prompt

# worktree_drift: false "missing", symlink double-counted dirt, parked.md orphans

Type: bug
Target: pyautoheart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Problems (heart/checks/worktree_drift.sh)

1. **False MISSING**: claims are compared against the `$PYAUTO_WT_ROOT` directory
   listing, not tested for existence — any `worktree:` outside
   `~/Code/PyAutoLabs-wt` (e.g. `PyAutoLabs/.codex-worktrees/python-312-floor`,
   which exists) is reported missing forever. Test the claimed path directly.
2. **Symlink double-counting**: the dirty scan iterates every child with a `.git`,
   which includes the *symlinks back to canonical checkouts* that
   `worktree_create` installs. One dirty canonical repo (PyAutoMind, admin_jammy…)
   is counted once per task worktree that links it — the source of noisy totals
   like "66 dirty". Skip symlinked children (`child.is_symlink()`), and report
   canonical-checkout dirt once, as its own category ("canonical dirty"), since a
   user's dirty canonical repo is not task-worktree drift.
3. **Parked orphans**: `parked.md` legitimately holds worktrees not in `active.md`;
   the orphan scan should consult it (or at least label those "parked", not
   orphan).

## Outcome

Drift totals a human can act on: real orphans, really-missing claims, task-branch
dirt, and canonical dirt each separately attributed.
