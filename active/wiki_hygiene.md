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
