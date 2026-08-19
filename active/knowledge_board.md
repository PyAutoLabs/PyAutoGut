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
