- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/34 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoMemory PR https://github.com/PyAutoLabs/PyAutoMemory/pull/36
- classification: maintenance (PyAutoMemory) — second knowledge-board follow-up (#32).
  Human decisions honoured: PDF provenance KEPT via a new frontmatter `archive:` field;
  the never-used alias subsystem RETIRED.
- summary: 59 pages had off-repo .pdf paths in frontmatter sources: (the only
  stub→archive mapping) — moved to `archive:`, defined in wiki/CLAUDE.md as read-only
  import provenance (the no-PDF-paths rule stays strict otherwise).
  bibkey_aliases.yaml (zero aliases ever) deleted with its validator/test/README legs.
  27 path-shaped [[../…]] wikilinks normalized to slugs; the smbh schema example now
  teaches the slug-only rule instead of contradicting it. 33 uncited junk-keyed bib
  entries deleted (11 SN designations incl. a non-astronomy import artifact, 1 ADS
  bibcode, 21 colon keys) — 1,099 → 1,066 entries, citation metadata valid.
- PROCESS FAULT (disclosed on PR #36): this squash accidentally swept the dev-box's
  uncommitted reading-queue.md hand tidy via a `git add -A` — the edit was meant to
  land attributed in #35. Nothing lost; lesson re-learned: explicit-path staging ONLY
  when a working tree carries someone's uncommitted edits.
- affected-repos:
  - PyAutoMemory

## Original prompt

# Wiki hygiene: PDF-path frontmatter, path-shaped links, bib junk keys

Type: maintenance
Target: pyautomemory
Repos:
- PyAutoMemory
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Found by the 2026-08-19 knowledge-board census (#32). Needs per-item human
decisions, not a blind sweep:

- 67 pages carry off-repo PDF paths in frontmatter `sources:` lists (235
  `.pdf` strings) against wiki/CLAUDE.md's "never record local PDF paths" —
  but they are the only provenance pointer to the archival library. Decide:
  keep as declared archival provenance (amend the schema) or purge.
- 19 `[[link]]` targets are path-shaped (`[[../lensing/...]]`) against the
  slug-only rule at wiki/CLAUDE.md:58-61 — normalize.
- Bib junk keys from the legacy import: 11 SN-designation keys (2001er...),
  ADS-bibcode keys, colon keys — rename or retire (they are uncited).
- The alias subsystem (bibkey_aliases.yaml) is documented at length but has
  zero aliases and has never been used — retire the docs+validation leg, or
  keep deliberately.
