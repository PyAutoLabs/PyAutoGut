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
