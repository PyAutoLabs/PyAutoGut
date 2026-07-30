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
