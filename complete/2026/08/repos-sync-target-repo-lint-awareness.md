# repos_sync: ask a target repo's own layout lint before installing .claude/

Shipped 2026-08-25 — PyAutoMind#322, merge commit 06324be2.

`repos_sync.py --write` creates exactly two top-level entries in every
checked-out repo — `.claude/` (session hook + settings) and the `CLAUDE.md`
pointer — and knew nothing about the target beyond "checked out, has an
AGENTS.md". A repo that lints its own layout has no way to know the write is
coming, so the write breaks that repo's CI and the breakage reads as the repo's
fault rather than as the sync script's.

## Why it was filed

PyAutoMemory was the casualty: `498e1a8` landed a tracked `.claude/` that was
not in `ALLOWED_TOP_DIRS`, and both `make validate` and `make test` failed on
arrival. That red was cleared inside the `inbox-board-staleness-signal` task
(PyAutoMemory `05aa803`, a deliberately separate commit). The repair was
downstream and complete, but the *class* stayed open: PyAutoMemory was the only
repo in the body map with a structure lint, so it was the only casualty, and
the next repo to grow one would break the same way on the next `--write`.

Filed as insurance rather than as an outstanding regression — hence the `low`
priority and the fact that nothing was failing when the work started.

## What shipped

The guard reads the target's own allowlist rather than keeping a copy: parse the
repo's layout lint with `ast` (never execute it), pull `ALLOWED_TOP_DIRS` /
`ALLOWED_TOP_FILES`, and skip the repo when the entry is missing from the set
its kind is governed by. The lint stays the single authority, so a repo that
allowlists `.claude` is covered again on the next run with no change on the Mind
side and no per-repo registry to rot.

New public surface in `scripts/repos_sync.py`: `find_structure_lint`,
`string_set_literal`, `structure_lint_allowlists`, `structure_lint_verdict`,
`structure_lint_forbids`, `check_structure_lints`, plus the
`STRUCTURE_LINT_CANDIDATES` / `GENERATED_TOP_LEVEL` / `ALLOWLIST_NAMES`
constants and a thirteenth check leg, `target-repo layout lints`.

## The trap worth remembering: not a key in repos.yaml

The filed prompt argued for declaring `structure_lint:` in `repos.yaml`, on the
grounds that repo identity already lives in the body map. **That is the wrong
move and the implementation deliberately rejected it.** `repos.yaml` is
identity-only by contract — its own header says "Identity only: GitHub home,
category, one-line role. Per-organ POLICY stays with the organ that owns it" —
and a lint declaration is policy, not identity. Adding the key would have put
the first policy crack in the body map to save a convention lookup.

Detection is by convention instead (`STRUCTURE_LINT_CANDIDATES`, currently just
`scripts/validate_structure.py`). That leaves a real, bounded gap: a repo that
lints its layout from some other path is not covered. The gap is documented at
the constant rather than papered over, and extending the tuple is the fix.

## Three judgment calls encoded in the guard

- **Unreadable is not permissive, and not forbidding either.** A computed or
  unparseable allowlist cannot be read without running the lint, so it never
  reads as an all-clear — but it also does not block the write, because "cannot
  tell" is not "forbids" and refusing on a guess would strand the common case.
  It is reported for a human instead.
- **The write side and the drift side must agree.** `check_session_hooks` and
  `check_claude_md_pointers` exempt a repo the writers skip; without that, a
  deliberately-unwritten repo reads as permanent drift on every run. The new
  check leg names it instead, so the skip is loud rather than silent.
- **An entry already on disk gets a different message.** That is the case that
  actually happened: a `--write` from before the guard left it behind, so the
  lint is failing *now*. Skipping the next write does not undo that, and the
  message says so rather than implying a write was declined.

## Verification

Replayed against the real artifact, not just fixtures: PyAutoMemory cloned
read-only and its pre-fix allowlist restored. The guard flagged exactly the two
entries its own lint flags, with the same verdict, and `--write` declined
instead of re-breaking it; against the current allowlist it is silent. 15 new
tests in `tests/test_repos_sync_structure_lint.py`, fictional fixtures only
(`tests/**` is KEEP-copied into the public template).

## Process traps hit on the way

1. **Staged-then-regenerated.** Resolving the `main` merge, the two generated
   dashboards were staged from `origin/main` to clear the conflict and only
   regenerated afterwards. `git commit --no-edit` commits the *index*, so the
   merge captured main's 140-prompt render and left the regenerated 141-prompt
   copy unstaged — a dashboard omitting the row for the very prompt the branch
   files. Dashboard Refresh went red on that head and green on the fix
   (`395886b4`). Regenerate *before* staging, or re-stage after regenerating.
2. **Shallow clone fakes a diverged `main`.** The web-session checkout is
   shallow, so the stale local `main` ref reported "ahead 55, behind 200"
   against a remote that genuinely contained the work. `merge-base
   --is-ancestor` on the *branch tip* is the reliable merge proof; the local
   `main` ref is not evidence of anything.

## Task shape

Filed and implemented in one session, straight from `draft/` — no GitHub issue
and no `active.md` entry, so there was nothing to close or release at
close-out. Both commits (the prompt, then the implementation) landed in
PyAutoMind#322 together. Web session: no worktree, and the egress proxy refuses
ref deletions, so branch cleanup is left to `/repo_cleanup`.

## Original prompt

# repos_sync.py installs .claude/ into every repo without knowing whether the target lints its own structure

Type: maintenance
Target: pyautomind
Repos:
- PyAutoMind
Difficulty: small
Autonomy: supervised
Priority: low
Status: formalised
Filed: 2026-08-25

`scripts/repos_sync.py --write` writes generated files into *every* checked-out
repo in `repos.yaml`:

- `write_session_hooks()` — `.claude/hooks/session-start.sh` (verbatim copy of
  `policy/session_start_hook.sh`, chmod 755) plus a `.claude/settings.json`
  that registers it.
- `write_claude_md_pointers()` — the canonical `CLAUDE.md` `@AGENTS.md` pointer.

Neither writer knows anything about the target repo beyond "is it checked out,
and does it have an `AGENTS.md`". In particular, **it does not know whether the
target repo enforces its own structure lint** — a check that asserts which
top-level paths are allowed to exist. Dropping `.claude/` into such a repo
breaks that repo's CI, in a way that looks like the repo's fault rather than
the sync script's.

## Why this is worth tracking

PyAutoMemory was the only repo in the body map carrying a structure lint, so it
was the only casualty and the break was fixed there. The *class* of break is
still open: the next repo that grows a structure lint gets silently broken the
next time anyone runs `repos_sync.py --write`, with no signal from the sync
script that it just wrote a path the target considers illegal.

This is latent, not currently failing. It is filed as insurance against a
recurrence, not as an outstanding regression.

## Shape of the fix

Options, roughly in increasing order of effort:

1. **Declare it in `repos.yaml`.** Give each repo an optional
   `structure_lint:` key naming the lint (or just a boolean). The writers skip —
   or warn loudly about — repos that declare one, so the human is told to extend
   the lint's allowlist before the sync lands.
2. **Detect it.** Have `repos_sync.py` look for the repo's own structure check
   (a known script path / CI job name) and refuse to write `.claude/` into a
   repo whose lint does not already permit it.
3. **Post-write verification.** After `--write`, run each touched repo's own
   fast checks and report any that the sync just broke. Most thorough, most
   expensive, and hardest to keep fast.

(1) is probably the right size: it makes the coupling explicit in the body map,
which is where repo identity already lives, and it costs one key per repo.

Whichever is chosen, the drift-check side (`check_session_hooks()`,
`check_claude_md_pointers()`) has to agree with the write side, or a
lint-exempt repo will show as permanent drift.

## Definition of done

- A repo that lints its own top-level structure is either skipped by the
  `.claude/` writers or flagged before the write, not broken by it.
- The corresponding `check_*` functions do not report the exempted repo as
  drift.
- `python3 scripts/repos_sync.py` (check mode) is clean across the workspace.
