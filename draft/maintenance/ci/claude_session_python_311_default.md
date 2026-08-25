# Claude web/mobile session containers default to Python 3.11 — below the organism's own floor

Type: maintenance
Target: PyAutoLabs org (all repositories) — Claude Code web/mobile session containers
Repos:
- (org-level) PyAutoLabs — every repo that gets a Claude Code web/mobile session
- @PyAutoMind
- @PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-25

Every Claude Code web/mobile session runs on **Python 3.11**, one minor version
below the floor the organism set for itself in the Python 3.12 floor campaign
and below every CI leg the org runs. A session-start hook landed in PyAutoMind
(`ae0a440`) and PyAutoBrain (`3a1b230`) on 2026-08-25 that puts a 3.12 venv
first on `PATH` for those two repos; this task is the rest of it — the other
35 repos in `repos.yaml`, and the container-level tooling the `PATH` shim does
not reach.

## What was measured (mobile session container, 2026-08-25)

Interpreters present: `/usr/bin/python3.10`, `3.11.15`, `3.12.3`, `3.13`.
What the session actually used:

| Surface | Resolves to | Notes |
|---------|-------------|-------|
| `python3`, `python` | `/usr/local/bin/python3 -> /usr/bin/python3.11` | symlinks baked into the image |
| `pip`, `pip3` | `/usr/bin/pip`, shebang `#!/usr/bin/python3` | installs land in 3.11 |
| `python3 -m venv` | 3.11.15 venvs | every ad-hoc venv inherited the wrong floor |
| `pytest` | `/root/.local/bin/pytest`, uv tool on `/usr/bin/python3.11` | pytest 9.0.2 |
| `black` / `ruff` / `mypy` / `pyright` / `flake8` / `poetry` | uv tools, all on `/usr/bin/python3.11` | `flake8 --version` reports `CPython 3.11.15` |

`PATH` order is the reason: `/usr/local/bin` (slot 10) precedes `/usr/bin`
(slot 12), and the image's 3.11 symlinks sit in the former.

**The image's own switch tool does not work.** `/usr/local/bin/use-python 3.12`
flips the `update-alternatives` links under `/usr/bin` and prints
`Switched to Python 3.12`, immediately followed by its own verification line
reading `Python 3.11.15` — because `/usr/local/bin/python{,3}` still shadow the
alternatives it just changed. Measured directly:

    $ use-python 3.12
    update-alternatives: using /usr/bin/python3.12 to provide /usr/bin/python3 (python3) in manual mode
    Switched to Python 3.12
    Python 3.11.15                     # <- its own check, already wrong
    $ /usr/bin/python3 -V              # the alternatives link did move
    Python 3.12.3
    $ python3 -V                       # what a session actually gets
    Python 3.11.15

So any fix has to either repoint `/usr/local/bin/python{,3}` or prepend
something ahead of them — which is what the shipped hook does.

## What it broke, concretely

`pytest` was a uv tool env with **no PyYAML**, so the PyAutoBrain suite could
not even be collected: `agents/faculties/sizing/_sizing.py` reads the body map
at import time and died on `import yaml`. A single test file measured
`1 failed, 22 passed`; the full suite was unrunnable. Under the hook's 3.12
venv the same suites are `494 passed` (Brain) and `187 passed` (Mind).

Nothing else in the org runs 3.11: Mind `spawn_drift.yml` 3.12,
`firewall_gate.yml` 3.13, Brain `tests.yml` 3.12 + 3.13, `nightly-release.yml`
3.12. The session container was the only 3.11 surface, and it is the surface
that authors the changes those legs then gate.

## What already shipped (and its limits)

`.claude/hooks/session-start.sh` + `.claude/settings.json` in PyAutoMind and
PyAutoBrain: remote-only (`CLAUDE_CODE_REMOTE`), builds one 3.12 venv per
container (`$HOME/.pyauto/session-py312`, `uv venv --seed`, `pytest` + `PyYAML`
— exactly what `tests.yml` installs) and exports `PATH` through
`$CLAUDE_ENV_FILE`. Idempotent, ~1s warm, non-blocking if no 3.12 exists.

It does **not** cover:

- the other 35 repos in `repos.yaml` — a session on PyAutoFit, PyAutoLens, any
  workspace or assistant repo is still 3.11;
- the uv tool set (`black`, `ruff`, `mypy`, `pyright`, `flake8`, `poetry`)
  — `pytest` is shadowed by the venv, the rest still run on 3.11, so `mypy` and
  `pyright` type-check against 3.11 semantics;
- anything with a literal `#!/usr/bin/python3` shebang (`pip`, `yq`, `conan`);
- the library repos' real dependency sets — `pytest` + `PyYAML` is the whole
  dependency set for the two organ repos, not for anything that imports numpy
  or JAX.

## The task

1. **Decide the mechanism before copying anything.** Three candidates, in
   order of preference: (a) an environment-level setup script / environment
   variable on the Claude Code web environment itself, which would fix every
   repo once and needs no per-repo file; (b) one canonical hook in PyAutoMind
   generated into each repo and drift-checked by `scripts/repos_sync.py`, the
   way the organ tables already are; (c) a hand-copied file per repo — 37 copies
   to keep in sync, the option to avoid. Check whether (a) exists before
   committing to (b).
2. **Cover the tools, not just the interpreter.** Rebuild the uv tool set on
   3.12 (`uv tool install --python 3.12 --force <tool>`), or decide per tool
   that its interpreter is irrelevant and pin `target-version` /
   `python_version` instead. `mypy` and `pyright` are the ones where the
   interpreter changes the answer.
3. **Size the library repos separately.** A hook for PyAutoFit / PyAutoArray /
   PyAutoGalaxy / PyAutoLens / the workspaces has to install the package and
   its dependencies, not two pure-Python packages. Expect a real install cost
   and decide there whether async mode (`{"async": true}`) is worth the race it
   introduces.
4. **Consider repointing `/usr/local/bin/python{,3}`** to 3.12 in the hook
   (the container runs as root) instead of only prepending a venv. It is the
   one change that also fixes the `#!/usr/bin/python3` shebang scripts; the
   cost is mutating the image rather than the session's `PATH`. Weigh, decide,
   record the reason.

## Acceptance

- [ ] `python3 -V`, `python -V`, `pip -V` and `pytest --version` all report
      3.12 in a fresh web/mobile session on **every** repo that gets one.
- [ ] The mechanism has one source of truth and a drift check, or is
      environment-level and needs neither.
- [ ] Each repo's own test command runs green in a fresh session, on the same
      interpreter its CI uses.
- [ ] `mypy` / `pyright` / `ruff` / `black` either run on 3.12 or carry an
      explicit pin, with the choice recorded.
- [ ] 3.13 stays reachable (`/usr/bin/python3.13`) for the two-version checks.

## Adjacent finding (not this task)

The web container's checkout of PyAutoMind has a local `main` with an
*unrelated history* to `origin/main` (`git merge-base` empty; ahead 55, behind
183), so `git checkout main && git merge` fails outright and pushes have to go
`branch:main`. Same family as `draft/maintenance/ci/run_smoke_copy_drift.md`
and the earlier stale-local-main rescue; worth its own prompt if it recurs.
