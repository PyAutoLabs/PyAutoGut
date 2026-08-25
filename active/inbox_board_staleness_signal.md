# The knowledge board's empty inbox should distinguish quiet from broken

Type: feature
Target: PyAutoMemory
Repos:
- PyAutoMemory
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-25
Issued: 2026-08-25

Split out of `complete/2026/08/arxiv-inbox-pat-scope.md`, which fixed the filing
bug but deliberately left this open.

## The gap

The board renders an empty arXiv inbox as:

    arXiv inbox (suggested overnight — un-acted papers lapse after 7 days)
    nothing waiting — the nightly arXiv digest fills this.

That line is shown for two completely different states:

- arXiv genuinely announced no strong-lensing papers; or
- the digest ran and the filing failed, so papers were lost.

On 2026-08-25 it was the second, and nothing on the page said so. The reader has
no way to tell without opening GitHub Actions.

## Why this is a known-solved problem here

`arxiv_papers.yml` already fixed the identical ambiguity on the Slack side. From
its header comment (user, 2026-07-13):

> Empty days STILL post a short "no new strong-lensing papers today" heartbeat —
> so silence in #papers always means a broken run, never a genuinely empty one.

The board has no equivalent. The digest's own invariant stops at Slack and does
not reach the surface the paper-management feature actually asks the human to
use.

## Task

Give the inbox a freshness signal so an empty board is readable. Options, in
rough order of cost:

- **`last filled:` line** — the board renders the date of the most recent
  successful `append`/`sweep`. An empty inbox dated today is quiet; one dated
  four days ago is suspect. Cheapest, no new state if it can be derived from
  `arxiv-inbox.md`'s git history or a marker the digest writes.
- **Explicit quiet-day marker** — the digest writes a dated "no papers" line on
  genuinely empty days, exactly mirroring the Slack heartbeat. Makes absence
  *positive* evidence, at the cost of a line the sweep must then age out.
- **Freshness warning** — the board flags an inbox with no write in N weekdays.
  Strongest signal, needs a threshold nobody has tuned yet.

Prefer whichever needs no new state file. Note that `scripts/inbox_actions.py`
is the single owner of the line format, the window and every transition — a
marker line must go through it, not through `board.py` or a workflow's shell.

## Note on the sibling failure mode

PR PyAutoMind#317 made the *workflow* fail loudly when the push is denied, so a
future filing failure reddens the run. This task covers the other half: the
board should be honest even when nobody is reading CI.
