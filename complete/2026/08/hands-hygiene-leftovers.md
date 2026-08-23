Two in-scope bullets from the 2026-08-19 release-board census (#239), plus a defect the
merge itself exposed.

**Shipped:**
- PyAutoHands#254 (squash `ce51277`) — expired ANNOUNCEMENT banner (dead since 2026-07-24)
  deleted from `generate_release_notes.py`; all seven unregistered modules resolved in
  `bin/autohands`.
- PyAutoHands#255 (squash `5ca3e70`) — follow-on fix, see below.

**Better than the prompt asked.** The prompt wanted a per-module decision and a complete
`bin/autohands help`. The branch also ENFORCES it (`tests/test_autohands_registry.py`):
every executable module is a subcommand or a listed `INTERNAL_MODULES` entry with a reason;
neither list may name a module that no longer exists; every subcommand has a description,
command and help; the lists are disjoint. AGENTS.md now points at `help` instead of
re-listing verbs. The registry cannot silently drift back out of date, which is how it got
here.

**The defect the merge exposed (#255).** Registering `check_dataset_allowlist` as a CLI verb
made it crash from a workspace root: `ModuleNotFoundError: No module named 'autohands'`.
Neither PR was wrong alone — #253 (this arc's guard) added
`from autohands.env_config import ...`, #254 made the module reachable from the dispatcher.
`bin/autohands` (`_python_in_autohands`) runs these tools as SCRIPTS with `autohands/` itself
on PYTHONPATH, so siblings are flat top-level modules; pytest imports the module
package-qualified. Supporting one form breaks the other. `_env_config()` now tries flat
first, falls back to package.

**The quieter half, worth remembering.** `_releasing_tokens` wrapped its import in
`except Exception` and returned a hardcoded `{full_datasets, real_output}` fallback, so under
the CLI it swallowed the ImportError and never consulted `ENV_DECLARATION_TOKENS` — a SILENT
DEGRADATION that still produced a green run. It gave the right answer only because those are
today's releasing tokens; the point of deriving from the map was that a future token would
protect scripts with no edit, and the CLI would have kept using the stale pair. A broad
`except` around an import converted a hard failure into a wrong-but-green one.

Found by running the newly-registered verb rather than assuming registration made it work.

**Verified:** suite 375 passed; the CLI verb runs clean from a workspace root AND still
reports the originating defect (exact file, line, resolved path) when that workspace is
reverted to its pre-fix state; tenant-firewall gate OK; confirmed working from `main`
post-merge.

**Still open — deliberately out of scope:** the census's third bullet, ~30 stale PyAutoHands
remote branches including `origin/master` and `origin/release`. Run as a separate
`/repo_cleanup` sweep so a destructive branch delete never rides a code diff.

Picked up from a dormant session (transcript last written 2026-08-20 15:42); the code had
been complete and unshipped for two days. Rebased onto 90f108f before opening.

## Original prompt

# Hands hygiene: expired announcement dead code, unregistered modules

Type: maintenance
Target: pyautohands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised

Found by the 2026-08-19 release-board census (#239):

- @PyAutoHands/autohands/generate_release_notes.py:23-46 carries an
  ANNOUNCEMENT banner mechanism that expired 2026-07-24 — now dead code.
  Delete it (delete the trap, don't document it).
- Several modules exist but are not registered in the `bin/autohands`
  dispatcher (navigator.py, check_navigator.py, regenerate_navigator.py,
  generate_markdown.py, validate_env_profiles.py, check_search_memory.py,
  check_dataset_allowlist.py). AGENTS.md prose was fixed (#239) to call them
  workflow-invoked modules; decide per module whether it should become a CLI
  verb or stay internal, and make `bin/autohands help` the complete registry.
- ~30 stale remote branches (incl. `origin/master`, `origin/release`,
  near-duplicate feature names) — sweep via /repo_cleanup.
