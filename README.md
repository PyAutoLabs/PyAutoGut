<p align="center">
  <img src="logo.png" alt="PyAutoMind" width="400">
</p>

# PyAutoMind

[![PyAutoScientist GitHub](https://img.shields.io/badge/%F0%9F%94%AD%20PyAutoScientist-GitHub-181717?style=for-the-badge)](https://github.com/PyAutoLabs/PyAutoScientist) [![PyAutoScientist ReadTheDocs](https://img.shields.io/badge/%F0%9F%93%96%20PyAutoScientist-ReadTheDocs-8CA1AF?style=for-the-badge)](https://pyautoscientist.readthedocs.io)

📋 **[Task dashboard → `dashboard.md`](dashboard.md)** — every task the Mind is
holding, on one page: what to pick up now, what is in flight, and the whole
backlog. Reads on a phone; regenerated from this repo, so it is never a
second copy of the truth. On a phone, prefer the
**[one-tap copy version](https://pyautolabs.github.io/PyAutoMind/)** — tap a
task's 📋 and its `/start_dev` command is on your clipboard, ready to paste
into a Claude Code chat.

The Mind of the PyAuto organism: every piece of work in the ecosystem starts
here, as a markdown file describing what you want in plain English. An AI
agent (or a human) picks the file up and turns it into a tracked GitHub
issue, a feature branch, and a merged pull request. No template, no special
syntax — if you can describe the change in a GitHub issue, you can drive the
workflow.

What lives here:

| File / folder | What it is |
|---------------|------------|
| [`dashboard.md`](dashboard.md) | **generated** — every task on one page, to pick from |
| `ideas.md` | raw incubating ideas, no structure required |
| `draft/<work-type>/<target>/*.md` | scoped prompts, **not started** (`feature/`, `bug/`, `docs/`, …) |
| `active/<name>.md` | **issued** prompts — an open issue, in flight |
| `complete/<YYYY>/<MM>/<slug>.md` | **shipped** — the rich completion record IS the ledger (`complete/AGENTS.md`) |
| `active.md`, `planned.md` | the live task ledger: in flight, queued |
| `repos.yaml` | the body map — the single source of repo identity |
| `scripts/` | registry sync + drift checks (`repos_sync.py`, `lifecycle.py`) |

A prompt flows through three file states that mirror the ledger: idea →
`draft/…` → `/start_dev` → GitHub issue + `active/` + `active.md` entry →
worktree development → PR → merge → the dated record
`complete/<YYYY>/<MM>/<slug>.md` (the sole completion ledger; the monolithic
`complete.md` was retired 2026-07-16, issue #81). `scripts/lifecycle.py`
advances the file and drift-checks the invariant. The registry is shared state, so any machine or session can pick up
an in-flight task.

The schemas and conventions — prompt taxonomy, prompt file format, the
`active.md` / completion-record schemas, epic trackers, bootstrap on a new
machine — are in [REFERENCE.md](REFERENCE.md). How agents should operate
this repo is in [AGENTS.md](AGENTS.md).

The organism this repo is the Mind of (Mind, Brain, Heart, Hands, Memory) is
described once in
[PyAutoBrain/ORGANISM.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/ORGANISM.md)
and documented in full at <https://pyautoscientist.readthedocs.io>.
