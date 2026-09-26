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
holds and voids.

## The board, and the void button

**[PyAutoGut Dashboard](https://pyautolabs.github.io/PyAutoGut/)** — a clear
overview of everything in the Gut: every ref under
`refs/heads/archive/condemned/` read against the Mind's `condemned.md`, in
buckets — **due** (past `sweep-after`), **in transit** (days left), **held**
(undated, kept until a human asks), **orphan refs** (no ledger entry),
**dangling entries** (ref missing), refs **held on another repo**,
**history-only** entries (`archive-ref: n/a`) and the **recently voided**.
Rendered by [`scripts/board.py`](scripts/board.py) and published daily and
after every void by [`gut_board.yml`](.github/workflows/gut_board.yml), with a
`state.json` feed for the organism cockpit.

**Void permanently** on a row opens a prefilled issue titled
`void: <name>`; *submitting it is the yes*. [`void.yml`](.github/workflows/void.yml)
then deletes that ref, comments the repo and pre-delete SHA, closes the issue
and re-renders the board. **Void all due** does the same for every due row
(`void: all-due`). The button reaches refs **held on another repo** too (an
entry whose `archive-ref` says `… on <Repo> origin`): refs in the Gut are
deleted with this repo's own token, refs on a sibling repo with the org PAT
`secrets.PAT_PYAUTOLABS` — the token Brain's `branch_archive.yml` already
pushes cross-repo with. The PAT is sent as an HTTP header from an empty scratch
repo (never in a URL or a log line, and masked). Without the PAT, or when the PAT
cannot reach a repo (a repo born after the PAT was minted may be missing from
its repository list), that ref is reported per row in the closing comment —
which names the repo — and left in place, and the issue stays open. The contract:

- only owners, members and collaborators can void — anyone else's issue is
  closed untouched;
- names must sit inside the archive namespace (no `..`, no `main`, no globs);
- **held** (undated) entries — in the Gut or on a sibling repo — are never
  one-tap voidable and never in `all-due`; void them in a session with
  `bin/pyauto-gut void <name> --yes`;
- refs without a ledger entry are voided one at a time, never in bulk;
- voiding removes the bytes; the ledger row stays in `condemned.md` until a
  session retires it (the board lists it with a copy-for-Claude payload),
  because the workflow cannot edit the Mind.

Full rationale and boundaries:
[`pyautogut-organ-decision`](https://github.com/PyAutoLabs/PyAutoMind/blob/main/complete/2026/07/pyautogut-organ-decision.md).
Operating guidance for agents: [`AGENTS.md`](AGENTS.md). The organism this
repo is the Gut of is described once in
[PyAutoBrain/ORGANISM.md](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/ORGANISM.md)
and documented in full at <https://pyautoscientist.readthedocs.io>.
