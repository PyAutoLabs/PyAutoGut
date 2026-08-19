<p align="center">
  <img src="logo.png" alt="PyAutoGut" width="400">
</p>

# PyAutoGut

[![PyAutoScientist GitHub](https://img.shields.io/badge/%F0%9F%A7%AB%20PyAutoScientist-GitHub-181717?style=flat-square)](https://github.com/PyAutoLabs/PyAutoScientist) [![PyAutoScientist ReadTheDocs](https://img.shields.io/badge/%F0%9F%93%96%20PyAutoScientist-ReadTheDocs-8CA1AF?style=flat-square)](https://pyautoscientist.readthedocs.io)

**The Gut organ of the PyAuto organism.** It owns the full lifecycle of
*condemned self-material* — the stale branches, `git stash` entries, dead code
and retired tests that a hygiene / `repo_cleanup` sweep is 95%-but-not-100% sure
is trash.

The gut's defining function is **elimination**: PyAutoGut performs the final
deletion itself. Between condemnation and deletion it holds each item as a
**durable, recoverable git ref** through a *transit window* — an item is
reabsorbed (recovered) right up until the sweep that voids it.

- **Payload** — durable git refs under `refs/heads/archive/condemned/<name>`
  (this repo is the *attic remote*), never lossy markdown copies. It is a branch
  prefix, not a custom `refs/archive/*` namespace — GitHub only accepts pushes to
  `refs/heads/*` and `refs/tags/*`.
- **Catalog** — the `condemned.md` manifest in **PyAutoMind** (symmetric to
  `parked.md`): the index; the refs here are the payload.
- **Driver** — the **Brain hygiene conductor** decides what to condemn and when
  to sweep; PyAutoGut holds and voids. Same split as Heart ↔ vitals: the organ
  does the work, the conductor reasons.

Full rationale and boundaries: `PyAutoMind/complete/2026/07/pyautogut-organ-decision.md`.
Operating guidance for agents: [`AGENTS.md`](AGENTS.md).
