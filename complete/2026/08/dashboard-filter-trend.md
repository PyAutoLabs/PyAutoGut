- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/46 (auto-closed on merge)
- shipped: 2026-08-21 — PyAutoMemory PR https://github.com/PyAutoLabs/PyAutoMemory/pull/43
  follow-up: PR https://github.com/PyAutoLabs/PyAutoMemory/pull/47 (merge 04bd0478).
- classification: feature (PyAutoMemory) — items 1-3 of the four human-approved
  dashboard follow-ups ("ok do all 4"); item 4 (claude-action filing) is its own task.
- summary: dashboard polish pair. (1) Title filter box — self-contained ES5 JS
  input above the reading queue; live-filters paper rows across sections,
  auto-expands sections and the reading history holding matches, restores the
  collapsed state when cleared. (2) Read trend — pure `_read_trend` helper over
  the `DONE <date>` history against the snapshot `generated` stamp: 7/30-day
  counts in the queue header + an 8-week bar strip (hidden until the first DONE
  paper), one-line mirror in the md render. Badge + README strip byte-identical.
- no-op discovered: item 3 of the approved list (digest arXiv refs) needed NO
  change — PyAutoMind arxiv_papers.yml's append block already emits
  `Title — <arXiv id>` (shipped with Memory#35); the bare-title queue entries
  simply predate it. Verified before editing rather than assumed.
- trap: worktree_remove refused the merged worktree ("Abandoned or unmerged
  work") despite a clean tree and `branch --merged` listing it — its
  merged-detection appears not to recognise this merge shape; verified merged
  + clean, then PYAUTO_WT_FORCE=1.
- affected-repos:
  - PyAutoMemory

## Original prompt

# Memory dashboard: paper filter box, read trend, digest arXiv refs

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
- PyAutoMind
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

Follow-up polish to dashboard-per-paper-actions (#42/PR#43, shipped
2026-08-21). The human approved all three from the ship-summary suggestions
("ok do all 4"; the fourth — claude-action filing — is its own task).

1. **Title filter box** (board.py html render): a small self-contained JS
   `<input>` above the reading queue that live-filters paper rows across all
   sections and auto-expands sections with matches; clearing restores the
   collapsed state. No network, no libraries.
2. **arXiv ids from the digest** (PyAutoMind
   `.github/workflows/arxiv_papers.yml`): the nightly digest's paste-ready
   append-to-queue block writes `Title — <arXiv id>` instead of the bare
   title, so new queue entries link straight to their abstract page (the
   dashboard already parses ` — <ref>`). Mind edit lands direct on main, the
   digest still never commits (same pattern as the original pipeline task).
3. **Papers-per-week trend** (board.py): from the `DONE <date>` history —
   read counts for the last 7/30 days in the Reading queue header plus a tiny
   8-week bar strip, rendered relative to the snapshot's `generated`
   timestamp so it stays pure and testable.

Constraints: board.py stays stdlib-only/local-parse; badge + README strip
byte-identical (cross-board contract); privacy pin titles/counts only;
workflow YAML edits validated before push (claude-action edit trap).
