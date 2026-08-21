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
