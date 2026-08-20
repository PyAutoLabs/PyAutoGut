**Shipped 2026-08-20.** PyAutoMemory#39 → PR PyAutoLabs/PyAutoMemory#41 (squash `c6f88e79`).

## Summary

Added a deliberately **generic placeholder** for `Vincken 2026` — *Euclid Collaboration: Vincken et al.*, the Euclid DR1 strong lens finding network comparison — so the key is citable before the paper is public.

| File | Change |
|------|--------|
| `bibliography/pyautomemory.bib` | `@unpublished{Vincken2026}` — author/year/topic, TODOs for arXiv ID, DOI, author list |
| `wiki/lensing/sources/lens-finding.md` | Source stub beside the Q1 Discovery Engine A/B/C entries, before `## See also` |
| `wiki/lensing/log.md` | Dated entry + retroactive `Shajib2025dolphin` line |

`make validate` (citations + structure) and `make test` (17) both pass; CI `validate` green.

## The prompt's premises were wrong — three of them

1. **`arxiv.org/abs/2503.22657` is NOT Vincken.** It is Shajib et al. 2025, *"dolphin: A fully automated forward modeling pipeline powered by artificial intelligence for galaxy-scale strong lenses"*. The Intake agent named the prompt from the `(Vincken 2026)` inside the target sentence and assumed the URL matched it. **Trap: verify an arXiv ID against the actual abstract before building a task around it.**
2. **dolphin was already in the repo.** `Shajib2025dolphin` + a full stub in `sources/lens-modeling-methods.md` landed in the #34/#36 wiki-hygiene pass. Only the `log.md` line was missing. **Trap: a "add paper X" prompt written months earlier may already be satisfied — grep the bibliography by arXiv ID first.**
3. **Vincken 2026 is real but unpublished** — DR1 is unreleased; the only copy is the private EC draft at `euclid_assistant/knowledge/sources/paper_sources/vincken_dr1/blank.tex:98`. Hence a placeholder, not an entry.

## Key decision: generic, not verbatim

PyAutoMemory is a **public** repo and the source is an unpublished Euclid Consortium draft, so the entry records author/year/topic only — no draft-verbatim title, no author list. Human chose this at plan approval over recording the real title/subtitle. Follows `bibliography/README.md`: *"If metadata or support is uncertain, add a TODO rather than guessing."*

## Validator constraints worth remembering

`scripts/validate_literature_citations.py` shapes the stub's formatting:

- `SOURCE_SECTION` (line 20) stops at `## See also` — a section placed **after** it is invisible to validation. Insert before.
- `CANONICAL_KEY` (line 17) requires `**Canonical BibTeX key:** \`Key\`` on its own line, no trailing text.
- A `**Supports:**` block **without** a key line fails `collect_claim_entries_without_keys`.
- `BIBTEX_ENTRY` (line 13) accepts any `@type`, so `@unpublished` validates fine.

## Incident: Mind commit swept onto a concurrent session's branch

A peer session checked the shared `PyAutoMind` checkout out onto `refactor/undo-community-file-declutter` **seven seconds** before `prompt_sync_push` ran. Because that helper does `git add -A`, the one-line `active.md` claim was committed onto **their** branch bundled with their uncommitted rename work (`.github/AI_POLICY.md`, `.github/CONTRIBUTING.md`, `scripts/spawn.py`, two spawn tests) and pushed as `b591c46e`.

Recovery: re-applied the claim to `main` through a detached temp worktree without touching their checkout. Two peer sessions had independently pushed restore commits (`70392131`, `5d270cc6`); all three merged idempotently and `main` ended with exactly one claim line. `b591c46e` remains on their branch under the wrong commit message — pushed, so not rewritten.

**Lesson:** the branch reading taken at the `start_dev` step-4 survey is worthless by push time. Re-check `git branch --show-current` in the same command as the commit, or bypass `prompt_sync_push` and use targeted `git add`.

## Still owed

1. **Refresh `Vincken2026`** with verified title, arXiv ID, DOI and author list once the paper is public, and replace the placeholder `**Supports:**` bullet with real claims.
2. **Deferred, never in scope here:** the `\citep{}` edit into *"the preprocessing required to scale them was only recently automated (Vincken 2026),"*. No file under PyAutoLabs contains that sentence — the Euclid manuscript's `.tex` lives outside the workspace. `euclid_assistant/` holds only other people's papers as a style-linting corpus; `euclid_strong_lens_modeling_pipeline/` has no `.tex` at all.

## Original prompt

## add-vincken-2026-wiki-and-cite-in-euclid

Type: docs
Target: workspaces
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

Add the Vincken 2026 paper to PyAutoPaper properly, including the lensing wiki / bibliography entry, and cite it in the Euclid paper alongside the sentence:

`the preprocessing required to scale them was only recently automated (Vincken 2026),`

Paper URL:

`https://arxiv.org/abs/2503.22657`

Original request verbatim:

> can you add this paper to PyAutoPaper properly (e.g. including the wiki) and cite it with Vincken at scale them was only recently automated
> (Vincken 2026), https://arxiv.org/abs/2503.22657

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->

## Scope correction (2026-08-20, start_dev investigation)

Three premises above did not hold; the task was rescoped at plan approval.

1. **The URL is not Vincken.** `https://arxiv.org/abs/2503.22657` is Shajib et
   al. 2025, *"dolphin: A fully automated forward modeling pipeline powered by
   artificial intelligence for galaxy-scale strong lenses"*.
2. **That paper is already in PyAutoMemory** (formerly PyAutoPaper) — added in
   the #34/#36 wiki-hygiene pass, not under this prompt:
   `bibliography/pyautomemory.bib` → `@misc{Shajib2025dolphin}`;
   `wiki/lensing/sources/lens-modeling-methods.md` → full source stub.
   Only a `wiki/lensing/log.md` line was missing.
3. **"Vincken 2026" is real but unpublished** — *Euclid Collaboration: Vincken
   et al., "Euclid Data Release 1 (DR1): Learning machine learning …"*. DR1 is
   unreleased and the draft is a private EC source tree, so there is no
   authoritative public record to cite.

**Delivered:** a generic, public-safe placeholder entry `Vincken2026`
(bibliography + `wiki/lensing/sources/lens-finding.md` stub + `log.md` entry),
to be replaced with verified metadata once the paper reaches arXiv.

**Deferred — not done here:** the `\citep{}` edit into the sentence "the
preprocessing required to scale them was only recently automated (Vincken
2026)". No file under `PyAutoLabs` contains that sentence; the Euclid paper's
`.tex` lives outside this workspace. Reopen when the paper source is reachable.
