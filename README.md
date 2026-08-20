<p align="center">
  <img src="logo.png" alt="PyAutoGut" width="400">
</p>

# PyAutoGut

[![PyAutoScientist GitHub](https://img.shields.io/badge/%F0%9F%A7%AB%20PyAutoScientist-GitHub-181717?style=flat-square)](https://github.com/PyAutoLabs/PyAutoScientist) [![PyAutoScientist ReadTheDocs](https://img.shields.io/badge/%F0%9F%93%96%20PyAutoScientist-ReadTheDocs-8CA1AF?style=flat-square)](https://pyautoscientist.readthedocs.io)

**PyAutoGut is the Gut of the PyAutoScientist** — the organ of elimination.
It owns the full lifecycle of *condemned self-material*: the stale branches,
`git stash` entries, dead code and retired tests that a hygiene sweep is
95%-but-not-100% sure is trash. The Gut holds each item recoverably through a
transit window, then performs the final deletion itself.

## How PyAutoGut works

1. **Condemn.** The Brain's hygiene conductor (`/hygiene`) decides an item is
   spent and files it in the manifest — the
   [`condemned.md`](https://github.com/PyAutoLabs/PyAutoMind/blob/main/condemned.md)
   ledger in the Mind (symmetric to `parked.md`: parked will resume,
   condemned awaits elimination).
2. **Transit.** Fragile forms (unmerged branches, stashes) are first
   materialised as real commits and pushed here as **durable git refs** under
   `refs/heads/archive/condemned/<name>` — this repo is the *attic remote*.
   Until its `sweep-after` date, recovery is just a checkout.
3. **Void.** A batch sweep (`/repo_cleanup` safety gates against the
   manifest) eliminates items past their transit window — the Gut deletes;
   the entry leaves the ledger.

The split mirrors Heart ↔ vitals: the conductor reasons and drives, the organ
holds and voids. There is no dashboard here by design — the Gut's ledger *is*
the Mind's `condemned.md`, one click above.

Full rationale and boundaries:
[`pyautogut-organ-decision`](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/07/pyautogut-organ-decision.md).
Operating guidance for agents: [`AGENTS.md`](AGENTS.md). The organism this
repo is the Gut of is described once in
[PyAutoBrain/ORGANISM.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/ORGANISM.md)
and documented in full at <https://pyautoscientist.readthedocs.io>.
