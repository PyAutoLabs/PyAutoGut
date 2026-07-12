# PyAutoGut

**The Gut organ of the PyAuto organism.** It owns the full lifecycle of
*condemned self-material* — the stale branches, `git stash` entries, dead code
and retired tests that a hygiene / `repo_cleanup` sweep is 95%-but-not-100% sure
is trash.

The gut's defining function is **elimination**: PyAutoGut performs the final
deletion itself. Between condemnation and deletion it holds each item as a
**durable, recoverable git ref** through a *transit window* — an item is
reabsorbed (recovered) right up until the sweep that voids it.

- **Payload** — durable git refs under `refs/archive/condemned/<name>` (this
  repo is the *attic remote*), never lossy markdown copies.
- **Catalog** — the `condemned.md` manifest in **PyAutoMind** (symmetric to
  `parked.md`): the index; the refs here are the payload.
- **Driver** — the **Brain hygiene conductor** decides what to condemn and when
  to sweep; PyAutoGut holds and voids. Same split as Heart ↔ vitals: the organ
  does the work, the conductor reasons.

Full rationale and boundaries: `PyAutoMind/research/pyautobrain/pyautogut_organ_decision.md`.
Operating guidance for agents: [`AGENTS.md`](AGENTS.md).
