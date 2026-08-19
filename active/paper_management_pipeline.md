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
