- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/32 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoMemory PR https://github.com/PyAutoLabs/PyAutoMemory/pull/33
  (squash `839ab10`... squashed on main); board LIVE at https://pyautolabs.github.io/PyAutoMemory/
  ("166 pages · 40% cited" badge + README strip auto-committed).
- classification: feature (PyAutoMemory) — fifth repo of the readability arc. Delivered
  BOTH halves of the rescoped research prompt ("dashboard-style surfaces for papers and
  wiki contents?"): the investigation write-up (census in the plan) AND the approved
  surface, with the human's direction that this board is the working management tool
  ("will prob become my paper management github repo resource type thing").
- investigation verdict (the research prompt's deliverable): raw papers/reading page NOT
  worth it (1,099-entry bib, 78% uncited, junk legacy keys; plain-text queue without
  links/state); a MANAGEMENT-FIRST contents-level board IS — the wikis' own [[wikilink]]
  navigation is dead on GitHub, and the real state (166 pages: 77 stub / 69 drafted /
  0 reviewed; 254/643 paper sections with resolved canonical keys; 230 queued papers in
  8 sections) is exactly a set of work queues.
- summary: scripts/board.py — stdlib-only, fully LOCAL parse (no APIs) + pure render
  (md / md-brief / html / badge / json). Work queues first, each with a one-tap 📋
  paste-ready Claude prompt executing the repo's documented workflow: file the next
  paper from a reading-queue section (bibliography/README "Adding a paper"), resolve
  TODO canonical keys per wiki, upgrade a stub per the schema; per-wiki contents cards
  with maturity bars + `/memory <domain>` recall chips. Contents-level privacy pinned
  by test (titles/counts only, never claim text). knowledge_board.yml publishes Pages +
  badge + the README memory:begin/end strip — NOTHING committed (validate_structure
  bans .html and gates an exhaustive root allowlist; the Heart render-in-CI shape).
  `make board` renders locally. README gained the badge/board paragraph/strip/boundary
  line; index.md's drifted 2026-05-22 off-repo folder archaeology → 3-line provenance
  note; AGENTS.md's "never reference in public repos" reworded as a SCOPE rule (it
  contradicted the CC BY 4.0 licence — the repo is public, my stale memory said
  private); 8 schema-invalid `status: draft` pages (methods/) → drafted;
  bibliography/README archaeology trimmed; AI_POLICY/CONTRIBUTING → .github/ with the
  validator allowlist + spawn MEMORY_RULES/spec/fixture lockstep (dead
  `bibliography/*.py` rule retired; knowledge_board.yml gets an explicit DROP —
  fail-closed held; scripts/board.py itself SHIPS to templates via scripts/* KEEP, so
  it hardcodes nothing: identity from git remote, wikis from the tree).
- validation: make validate + 18 Memory tests (8 new); PyAutoMind spawn suite 154/154
  after lockstep (the privacy fixture's invented bibliography/tool.py had to go — the
  EMPTY fallback on .py is an unmatched-class failure by design); live render
  cross-checked the census numbers; page/badge/strip verified live; the user's
  uncommitted reading-queue.md hand edit left untouched throughout (explicit-path
  commits only).
- key traps:
  - validate_structure.py BANS .html repo-wide and allowlists root files exhaustively —
    Memory dashboards must render in CI and commit nothing.
  - Removing a spawn KEEP glob can silently reroute fixture files into EMPTY, and
    EMPTY on an extension without a header comment is an unmatched-class SystemExit —
    check the privacy fixtures when touching MEMORY_RULES.
  - The board script travels into spawned templates (scripts/* KEEP) — it must derive
    ALL identity (repo, owner, wiki names, bib filenames) from the checkout.
- follow-up drafts: bug/pyautobrain/memory_surfaces_stale_names (the memory faculty
  never reads index.md/reading-queue/bibliography; retired *_wiki names pinned in Brain
  policy/tests/skills), maintenance/pyautomemory/wiki_hygiene (67 PDF-path frontmatter
  pages — human decision; path-shaped links; bib junk keys; unused alias subsystem),
  feature/pyautomemory/paper_management_pipeline (structured queue + arXiv-digest
  ingest — the named growth path).
- affected-repos:
  - PyAutoMemory

## Original prompt

# PyAutoMemory knowledge board — manage the papers and wikis, one tap at a time

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Rescoped 2026-08-19 from the research prompt "Explore: dashboard-style surfaces for
papers and wiki contents?" — the investigation ran (census in the plan/completion
record) and the human approved the recommended surface plus a management-first
direction:

> its fine for PyAutoMemory for me my paper and wikis and whatnot, its an illustrative
> example, and i want to use this dashboard to manage all that as effectly as possible.
> this will prob become my paper management github repo resource type thing

Original intake text (verbatim):

> Exploratory research, deliberately unscoped: the one-tap dashboard pattern (generated
> markdown page plus an HTML twin on GitHub Pages) now exists for @PyAutoMind tasks.
> Investigate whether the organism's scientific material would benefit from the same
> treatment — papers the project cites or produces, and wiki contents — for example a
> browsable reading/citation surface, or wiki pages rendered somewhere phone-friendly
> with copy-for-Claude hooks into /memory recall. … The deliverable is an investigation
> write-up, not an implementation … recommending nothing is a valid outcome.

Investigation verdict (2026-08-19): a raw papers/reading page is NOT worth it yet
(1,099-entry bib with 78% uncited; a plain-text queue with no links/state); a
**management-first knowledge board** IS: 167 wiki pages (statuses 77 stub / 61 drafted /
8 schema-invalid draft / 0 reviewed), 643 paper sections of which only 254 carry a
resolved canonical key (389 TODO), 8 reading-queue sections — all of it renders as WORK
QUEUES with one-tap 📋 paste-ready Claude prompts (read the next paper in a section per
bibliography/README's workflow; resolve TODO keys per wiki; upgrade stubs; /memory
recall chips). Contents-level only: titles and counts, never claim text. Pages html +
badge + README strip, rendered in CI and never committed (validate_structure bans .html
and gates an exhaustive root allowlist).

Also in scope: AI_POLICY/CONTRIBUTING → .github/ (paired validator + spawn-contract
edits), the 8 `status: draft` → `drafted` fixes, index.md's drifted 2026-05-22 status
archaeology trimmed, bibliography/README archaeology trimmed, dead
`bibliography/*.py` spawn rule removed, and the AGENTS.md "never reference in public
repos" rule reworded as a scope rule (the repo is public and CC BY 4.0 — the old wording
contradicted the licence).

Follow-ups filed separately: Brain memory-faculty blind spots + retired `*_wiki` name
pins; wiki hygiene (PDF-path frontmatter, path-shaped links, bib junk keys); the
paper-management pipeline (structured reading queue + arXiv-digest ingest) — the growth
path the human named.
