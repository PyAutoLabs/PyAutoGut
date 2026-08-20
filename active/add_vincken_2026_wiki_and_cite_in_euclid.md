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
