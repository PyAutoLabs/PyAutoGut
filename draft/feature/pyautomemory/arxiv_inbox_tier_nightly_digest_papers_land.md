# arXiv inbox tier: nightly digest papers land in PyAutoMemory with a 7-day window

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

## Original request (verbatim, 2026-08-24)

> is there a way to make it so these are automatically on pyautomemory maybe
> with a one week window where they appear and I can choose to add them to the
> to read list there or do the other options already on the to read list like
> intake to wiki?

Asked immediately after the 2026-08-24 #papers digest, whose two papers were
filed into `reading-queue.md` by hand from the Slack paste-block (PyAutoMemory
`claude/strong-lensing-papers-2026-6cpv0a`, commit 2a5919f).

## Goal

Replace the Slack "📥 Queue these" paste-block hand-off with an **inbox tier**
that sits in front of the reading queue: the nightly digest's surviving papers
appear on the PyAutoMemory knowledge board automatically, each with the same
one-tap actions the reading queue already has, and lapse after a week if not
acted on. Nothing reaches `reading-queue.md` without a human tap — the ingest
gate moves from "paste into a session" to "tap on the board", it does not
disappear.

## What already exists (reuse, do not rebuild)

- `PyAutoMemory/scripts/board.py` parses `reading-queue.md` into sections and
  papers and renders each with three prefilled-issue actions (📥 `queue-intake`,
  📑 `queue-cite`, ✅ `queue-read`) — the per-paper actions task, Memory #42/PR#43.
- `queue_actions.yml` already commits `reading-queue.md` on `main` with the plain
  `GITHUB_TOKEN` and explicitly redispatches `knowledge_board.yml` (GITHUB_TOKEN
  pushes never retrigger `on: push`).
- `queue_filing.yml` already drives claude-code-action to add the canonical bib
  entry + `wiki/<domain>/sources/` stub and open the filing PR — Memory #48/PR#49.
- `PyAutoMind` already holds a `PAT_PYAUTOLABS` secret (`spawn_drift.yml` uses
  it), so the digest can write cross-repo into PyAutoMemory with no new
  credential. The plain `GITHUB_TOKEN` cannot.

## Design

1. **New `PyAutoMemory/arxiv-inbox.md`.** One line per suggested paper,
   `<announce-date> — <title> — <arXiv id>`; the date is the expiry anchor.
   Document the format in-file as `reading-queue.md` does.
2. **New step in `PyAutoMind/.github/workflows/arxiv_papers.yml`**, after the
   Claude summarise step: append the surviving papers to that file via
   `PAT_PYAUTOLABS`. The list already exists — it is exactly what the paste-block
   emits today. Retire the paste-block section and point the digest at the board.
3. **Board inbox panel** above the reading queue: "arXiv inbox — N waiting", each
   paper with days-left and four actions — ➕ add to reading queue, 📥 intake,
   📑 cite, ✖️ dismiss.
4. **➕ / ✖️ are new labels** handled by `queue_actions.yml` in the same shape as
   ✅: move the line into the right `reading-queue.md` section, or drop it.
5. **📥 / 📑 already work**, but `queue_filing.yml` DONE-marks a *reading-queue*
   line; an inbox paper has none, so it must append-then-DONE (or skip that leg).
6. **The 7-day sweep** runs in the nightly job: drop inbox lines older than the
   window. Git history holds anything swept, so nothing is truly lost.

Because the digest is strong-lensing-only, every paper routes to
`## Strong Lensing` — no classification step is needed. Keep it that way; a
multi-section inbox is a later problem if the digest ever widens.

## Decisions the human should confirm at start_dev

- **This deliberately reverses a shipped constraint.** `paper-management-pipeline`
  (Memory #35) built the digest so it *never commits* — ingest was human-gated by
  the paste step. Record the reversal as intentional, in the completion record,
  so it does not read as drift later.
- **Lapse semantics.** Memory's "never delete, `DONE`-prefix instead" rule is
  about *reading history*; an un-acted suggestion is not history. Recommend a
  silent (git-recoverable) drop; a `## Lapsed` section is the conservative
  alternative.
- Window length is 7 days by the request; make it one constant, not a literal
  scattered across the workflow and the board.

## Traps carried forward from the sibling tasks

- `arxiv-inbox.md` is a new **root** file: add it to `ALLOWED_TOP_FILES` in
  `scripts/validate_structure.py` or `make validate` rejects the repo.
- `spawn_spec.md` has no `.github/**` catch-all — any new/changed Memory workflow
  needs an explicit `spawn.py` decision (the siblings both chose DROP).
- The PyAutoLabs org has "Allow GitHub Actions to create and approve pull
  requests" OFF, so an Actions-opened PR silently no-ops; direct commits to
  `main` with `GITHUB_TOKEN` are what the existing queue workflows do.
- `queue_actions.yml`'s author-association gate (OWNER/MEMBER/COLLABORATOR) is
  load-bearing on a public repo — the new labels need the same gate.

## Lineage

Fourth in the paper-management line: Memory #35 (structured queue + arXiv
ingest), #42 (per-paper board actions), #48 (claude-action filing of
intake/cite issues), this.

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from file:/tmp/claude-0/-home-user/09bebd08-3d0d-5ba1-8380-10185d92c0ca/scratchpad/inbox_idea.md -->
