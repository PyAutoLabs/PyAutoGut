# Phase 2 straggler: single AI Assistant section in the workspace start_here.py scripts

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Original request (verbatim)

> PyAutoGalaxy and PyAutoLens start_here.py has old Three ways to learn AI +
> multiple AI split we fixed in other docs.

## Intent

The `assistant-first-docs` task (PyAutoLens#645, completed 2026-07-24) unified
the library READMEs, Read the Docs pages and both workspace READMEs around a
single **AI Assistant** route and removed the `Three Ways to Learn` structure.
It missed one surface: the **root `start_here.py`** of each workspace — the
flagship onboarding script a new user actually runs.

Bring those two scripts onto the same framing as the already-shipped README /
RTD wording.

## Scope

**`autolens_workspace/start_here.py`** — replace the `__Three Ways To Learn
PyAutoLens__` section (currently lines 353-372) in its entirety. It carries the
retired three-way split: `1. Manual Navigation`, `2. AI Chat Assistant` (ChatGPT
/ Claude in the browser), `3. Fully Agentic AI` (Claude Code / Codex). Replace
with one `__PyAutoLens AI Assistant__` section mirroring the canonical wording
already live in `autolens_workspace/README.md:17-19`,
`PyAutoLens/README.md` and `PyAutoLens/docs/overview/overview_{1,2}*.md`:
conversation agents (e.g. ChatGPT) and coding agents (e.g. Claude Code, Codex),
pointing at `autolens_assistant` for the full scope.

**`autogalaxy_workspace/start_here.py`** — has **no** AI section at all (it was
never given one; it also has no `__Where To Next__` header). Add the equivalent
`__PyAutoGalaxy AI Assistant__` section, mirroring
`autogalaxy_workspace/README.md:15-17`, placed between `__Wrap Up__` and
`__What Data Type?__`.

Both scripts must keep the transition sentence into the navigation questions
that follow, reframed as **human-readable documentation** rather than
"manual navigation" (the phase-1 framing). Everything else in both scripts —
Colab links, `Still Unsure?`, `HowTo*` pointers, `Features` — is untouched.

## The autogalaxy_assistant URL

`https://github.com/PyAutoLabs/autogalaxy_assistant` returns **404** — the repo
does not exist yet. This is a deliberate, already-recorded decision: the
`assistant-first-docs` completion record states "The future PyAutoGalaxy
assistant URL is intentionally allowed to return 404 until its repository is
created", and the link already ships in `autogalaxy_workspace/README.md` and
the PyAutoGalaxy RTD pages. Human decision 2026-07-29: **keep the same URL** in
`start_here.py` for consistency. Neither workspace runs a `url_check` workflow,
so no CI gate is involved.

## Relationship to the existing phase-2 draft

`draft/docs/workspaces/unify_ai_assistant_workspace_readmes.md` ("Phase 2: Make
workspace READMEs assistant-first") is **already satisfied** — the
`assistant-first-docs` record lists autolens_workspace#329 and
autogalaxy_workspace#155 as merged workspace PRs, and both READMEs carry the
unified section today. That draft should be retired rather than run; this
prompt covers the one surface it left behind.

## Acceptance

- No occurrence of `Three Ways To Learn`, `Manual Navigation`, `AI Chat
  Assistant` or `Fully Agentic AI` remains in either workspace (`.py`, `.ipynb`
  or `markdown/`).
- Both root `start_here.py` files carry one `__<Library> AI Assistant__`
  section whose wording matches the shipped README/RTD text.
- `start_here.ipynb` and `markdown/start_here.md` regenerated in both repos.
- Smoke suite green in both workspaces; `scripts/check_sizes.sh` clean.
