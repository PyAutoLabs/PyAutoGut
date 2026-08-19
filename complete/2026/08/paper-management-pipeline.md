- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/35 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoMemory PR https://github.com/PyAutoLabs/PyAutoMemory/pull/37
  + PyAutoMind main f7a76330 (the arXiv digest edit); board refresh verified live.
- classification: feature (PyAutoMemory + PyAutoMind) — third knowledge-board follow-up;
  the growth path the human named at #32 ("my paper management github repo resource").
- summary: reading-queue.md restructured — real `## ` section headers (the bare
  'Label:' form was one colon-terminated paper title away from misparsing; three such
  titles existed), format documented in-file, and read papers are never deleted: a
  `DONE <YYYY-MM-DD> — ` prefix keeps them as the reading history. scripts/board.py
  parses the headers and counts DONE separately (per-section "N waiting · M read");
  its file-the-next-paper 📋 prompt now ends at marking DONE. index.md documents the
  format. The Mind's nightly arXiv Slack digest now ends with a paste-ready one-tap
  block appending the surviving papers to '## Strong Lensing' — human-gated ingest;
  the digest itself still never commits (workflow YAML validated — the claude-action
  edit trap respected).
- affected-repos:
  - PyAutoMemory

## Original prompt

# Paper management pipeline: structured reading queue + arXiv ingest

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The growth path the human named at the knowledge-board review (#32): "this
will prob become my paper management github repo resource type thing."

- Structure @PyAutoMemory/reading-queue.md: real markdown headers per section,
  one line per paper with an optional arXiv link/ID, and a read/consumed
  convention (e.g. `# DONE <date>` prefixes like the Mind queue) instead of
  destructive deletes — so the knowledge board can show real reading state and
  history. NOTE: the file currently carries an uncommitted hand edit on the
  dev box — land that first.
- Ingest the arXiv digest: @PyAutoMind/.github/workflows/arxiv_papers.yml
  currently fetches + summarises to Slack fire-and-forget; PyAutoMemory never
  sees it. Add an opt-in path that appends selected digest entries to the
  matching reading-queue section (human-gated or one-tap from Slack/board).
- The board (scripts/board.py) then grows read/unread counts and
  papers-per-week trends.
