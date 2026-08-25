- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/58
- shipped: 2026-08-25 — PyAutoMemory main 963388a (PR #60), PyAutoMind main a82b96f (PR #320).
  Merged library-first: `arxiv_papers.yml` calls `inbox_actions.py stamp`, so the Memory
  side had to land first or the nightly run would have failed on a subcommand that did
  not exist yet.
- classification: feature (PyAutoMemory + PyAutoMind) — sixth in the paper-management line
  after #35 (structured queue + arXiv ingest), #42 (per-paper board actions), #48
  (claude-action filing), `arxiv-inbox-tier` (#57) and `arxiv-inbox-pat-scope`. Split out
  of that last record, which fixed the filing bug and deliberately left this open.
- summary: the knowledge board rendered an empty arXiv inbox as "nothing waiting — the
  nightly arXiv digest fills this" for two opposite states — arXiv was genuinely quiet, or
  the digest ran and the filing failed so the papers were lost. On 2026-08-25 it was the
  second and nothing on the page said so. `inbox_actions.py` now owns a `last digest:
  <date>` line in `arxiv-inbox.md`, rewritten on every digest run whether or not papers
  arrive, and the board renders it. An empty inbox now says which kind of empty it is.

- the design that matters — **the warning is computed in the reader's browser, not at
  render time.** `knowledge_board.yml` republishes on pushes to `arxiv-inbox.md`, which is
  precisely what stops happening when filing breaks: the published page freezes at its last
  good render. A staleness warning baked in server-side would freeze with it, sit at
  "0 weekdays" forever, and be absent in exactly the failure it exists for. So the split is
  the *date* into the page (a fact, honest even frozen) and the *verdict* into ~10 lines of
  JS against the reader's own clock. A page already stale when rendered warns without JS
  too. Any future board signal that answers "is this surface still being fed?" has the same
  shape and should be read this way.

- one line, not two features: the prompt offered a `last filled:` line and an explicit
  quiet-day marker as separate options. A stamp rewritten on every run is both — dated
  today over an empty inbox it is the marker (absence becomes positive evidence), days old
  it is the freshness signal. Because it is replaced rather than accumulated, the sweep
  never has to age it out, which was the marker option's stated cost.

- threshold: `INBOX_STALE_WEEKDAYS = 2`, beside `INBOX_WINDOW_DAYS`. Not 1: the digest
  fires at a nominal 02:00 UTC and GitHub cron only ever jitters *later*, so a board
  rendered early can see yesterday's stamp with nothing wrong. Weekdays, not days, because
  the digest is Mon–Fri — a Monday board reading Friday's stamp is three calendar days but
  zero missed runs.

- scope call: the prompt said PyAutoMemory only. The PyAutoMind leg was added deliberately
  and is not optional — a stamp that only updates on days papers arrive goes stale on
  exactly the days it exists to prove were quiet. The digest's inbox step lost its
  `count != 0` guard, and the empty-day heartbeat now writes `arxiv_survivors.json` as
  `{"papers": []}` (the same file the Claude step already writes on its own empty day), so
  every path produces one and a *missing* survivors file stays what it always was: a real
  failure, not an empty day.

- traps:
  - **a render-time freshness check on a push-triggered board is self-defeating.** The
    board only re-renders when the thing it is checking succeeds. Stated once here because
    the next such signal will look identical and the mistake is invisible in review — the
    tests pass, the page looks right, and it silently never fires.
  - **a missing stamp must not warn.** `spawn.py` maps `arxiv-inbox.md` to EMPTY, so every
    freshly spawned Memory template has no stamp and has never run a digest. Warning there
    would make every template birth look broken. Absence of evidence, not evidence of
    breakage — `is_stale(None, …)` is False by contract, with a test pinning it.
  - the stamp is deliberately **not** date-first (`last digest: <date>`, not
    `<date> — last digest`) so it can never match `INBOX_LINE_RE` and be read back as a
    paper. Tested both ways.
  - `inbox_actions.py`'s `--date` is a **global** flag before the subcommand
    (`--date 2026-08-25 stamp`), like `--inbox`/`--queue`. Same asymmetry as `intake`'s
    `--apply`; cost one failed invocation here.
  - **you still cannot test `arxiv_papers.yml` from a branch that edits it** — inherited
    from `arxiv-inbox-pat-scope` and still true. Rehearsed instead by extracting the two
    shell blocks verbatim from the workflow with PyYAML and running them against a real
    PyAutoMemory clone, with the `git clone` line swapped for a local copy. That is the
    cheapest honest substitute and worth reusing.
  - main moved twice underneath this task in one session: PyAutoMemory#59 landed the same
    `.claude/` allowlist fix while the branch was in flight (resolved in main's favour,
    leaving the branch's own commit contributing nothing), and a second `active.md` edit
    reddened `dashboard_refresh.yml` because the generated pages were not regenerated with
    it. **Any `active.md` write needs `intake --apply dashboard` in the same commit.**

- side effects, both intended: a quiet day is now a one-line commit to PyAutoMemory rather
  than silence, which re-renders the knowledge board daily; and the sweep runs every
  weekday instead of waiting for the next paper day to evict a lapsed line.

- validation: 92 PyAutoMemory tests (23 new, was 69) + `make validate` green; 197 PyAutoMind
  tests; `lifecycle.py check` OK; YAML parses and every `run:` block passes `bash -n`; both
  PRs green on their final head shas. Beyond CI: the *shipped* JS (extracted from
  `board.py`, not retyped) was cross-checked against the Python weekday arithmetic over 30
  consecutive stamp dates including weekends, no mismatches; and all four digest paths were
  rehearsed against a real checkout — quiet day/same date (no commit), quiet day/new date
  (the heartbeat commit), paper day (paper lands below the stamp), quiet day sweeping
  lapsed papers.
- NOT proven live: the workflow leg cannot be fired from its own branch (above). The
  scheduled 02:00 UTC run on main is the first genuine end-to-end exercise; the steps are
  plain bash with no dependency on `claude-code-action`.
- incidental: PyAutoMemory main was red on `make validate` and `make test` from 498e1a8,
  which committed a tracked `.claude/` without adding it to `ALLOWED_TOP_DIRS`. Fixed twice
  in parallel — #59 and this branch — and reconciled in main's favour.
- affected-repos:
  - PyAutoMemory
  - PyAutoMind

## Original prompt

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
