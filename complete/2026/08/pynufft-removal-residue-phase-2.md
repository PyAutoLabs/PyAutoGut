Shipped 2026-08-23 across three repos (issue @autogalaxy_workspace#224):
@autogalaxy_workspace#225, @autogalaxy_assistant#19, @autolens_assistant#115.

Phase 2 of 3. Prose only — zero executable references (the one live reference
was phase 1). @autogalaxy_workspace is the direct sibling of the repo fixed by
@autolens_workspace#497 and was simply never swept.

## What changed

- **@autogalaxy_workspace** — 5 scripts (`interferometer/{start_here,simulator}.py`,
  `interferometer/features/linear_light_profiles/modeling.py`,
  `guides/using_jax.py`, root `start_here.py`), notebooks regenerated via
  `generate.py autogalaxy`. **CI fully green.**
- **@autogalaxy_assistant** — 2 skills + 5 wiki pages; 5 pages re-stamped with
  `--write-provenance --page` (scoped, so no unrelated pin moved).
- **@autolens_assistant** — 5 wiki pages + `chat_pack/05_wiki_api_reference.md`
  regenerated (chat_pack is GENERATED; an initial hand-edit was reverted).

Extras tables were corrected against the real `pyproject.toml`, not merely
de-pynufft'd: PyAutoGalaxy's `optional` is `autogalaxy[jax]`, `numba`,
`zeus-mcmc`, `getdist`. **`nufftax` was never in it either** (it lives in
PyAutoArray's `optional`), so the docs now say to install it explicitly rather
than implying the extra provides it.

Also fixed a stale claim that `TransformerNUFFT` "is not JAX-traceable" and that
nufftax was "a research path" — autolens_workspace had said the opposite since
#497, so the two workspaces actively contradicted each other.

## Two generator traps, both caught

1. **`markdown/` is NOT `notebooks/`.** `generate.py` regenerates notebooks
   cheaply; `markdown/` has a SEPARATE generator (`generate_markdown.py`) that
   **executes curated scripts for real**, and whose documented policy is
   "manual / at-release, only when a curated script changes — never
   per-commit". Deliberately not run. **Three curated pages (`start_here`,
   `interferometer/start_here`, `interferometer/simulator`) still contain the
   stale text** until the next release regeneration.
2. **The chat-bundle version stamp rolls BACKWARDS off a stale local install.**
   Regenerating rewrote `chat_pack/01_api_surface.md` and `llms-chat.txt` from
   `2026.8.23.1` to `2026.8.17.1`, because the source checkouts on this machine
   declare `__version__ = 2026.8.17.1`. Committing that would have advertised an
   OLDER API surface than what was already recorded. Both files were reverted,
   keeping only the wiki-derived page — and **CI confirmed the call**:
   `chat_bundle: OK - artifacts current`. Local `--check` failure was the stale
   install, nothing else.

## Merged over a PRE-EXISTING red — the useful part

Both assistant PRs merged with `wiki-currency` RED. Establishing whose fault it
was is the transferable bit: run the same check on untouched `main`.

- Symbol audit `--scope all`: `main` reports **missing/broken: 2** in both
  repos; the PR branches report **1**. The PRs REDUCE it by exactly the
  `TransformerNUFFTPyNUFFT` reference removed. The survivor is
  `al.mesh.RectangularAdaptImage`, absent from the installed stack (suggestions:
  `RectangularRTUAdaptImage`, `RectangularBilinearAdaptImage`).
- `autogalaxy_assistant` additionally fails `--check-citations` on
  `wiki/core/operations/sandbox.md` citing
  `PyAutoGalaxy:autogalaxy/plot/plot_utils.py`, which no longer exists. That
  file is untouched by the PR.

**Both assistant repos still have a red `wiki-currency` on `main`.** Filed
2026-08-23 as `draft/bug/assistants/wiki_currency_red_on_main.md` (see the
addendum at the end of this record).

Heart was also RED (`release validation FAILED`, unrelated). Both reds were
explicitly human-authorized before merge.

## Trap worth generalising

A "shipped" marker on a parent task is not evidence its downstream is clean. The
pynufft removal was marked shipped and its library tier genuinely was — but its
workspace tier named two repos and missed five more, including one hard break.
When a task deletes a public symbol, grep the symbol across **every** repo and
split executable references from historical prose before believing it is done.

## Addendum 2026-08-23 — the unfiled findings are now filed

Written when phase 3 was issued (@PyAutoHands#258). The three findings this
record listed as "Found while shipping, NOT filed anywhere" now have prompts,
so nothing depends on re-reading this record:

1. Assistants' red `wiki-currency` on `main` →
   `draft/bug/assistants/wiki_currency_red_on_main.md`
2. @autolens_workspace_developer datasets that do not reproduce →
   `draft/bug/autolens_workspace_developer/committed_datasets_do_not_reproduce.md`
3. @autolens_workspace_developer having no test CI → already covered by
   `draft/maintenance/autolens_workspace_developer/stale_api_rot_audit.md`;
   no new prompt filed.

The deferred @autogalaxy_workspace `markdown/` regeneration (three curated
pages still carrying the pynufft prose) is filed as
`draft/docs/autogalaxy_workspace/markdown_regeneration_pynufft_prose.md`.

## Original prompt

# Phase 2: retire pynufft prose from autogalaxy_workspace and both assistants

Type: maintenance
Target: workspaces
Repos:
- @autogalaxy_workspace
- @autogalaxy_assistant
- @autolens_assistant
Difficulty: low-medium
Autonomy: supervised
Priority: normal
Status: issued
Filed: 2026-08-23
Issued: 2026-08-23

Phase 2 of 3. Parent: `pynufft_removal_downstream_residue.md`. Independent of
phases 1 and 3.

All prose — **zero executable references** here (the one live reference is
phase 1's). These docs advertise `TransformerNUFFTPyNUFFT`, deleted by
@PyAutoArray#475, as an available "non-JAX fallback". Users following them hit
an `AttributeError`.

## Reference wording

Mirror what @autolens_workspace#497 already landed — see
`autolens_workspace/scripts/interferometer/start_here.py:36-39,47-64`, which
frames `TransformerNUFFT`/nufftax as the NUFFT and `TransformerDFT` as the
exact, pure-numpy `O(N_vis x N_pix)` fallback. Do not invent new phrasing.

## @autogalaxy_workspace — 26 hits, three surfaces

The direct sibling of the repo that was fixed, and the reason this was missed.

**Edit `scripts/**` only.** `notebooks/**` and `markdown/**` are **generated**:

- `scripts/interferometer/start_here.py`
- `scripts/interferometer/simulator.py`
- `scripts/interferometer/features/linear_light_profiles/modeling.py`
- `scripts/guides/using_jax.py`
- `scripts/../start_here.py` (workspace root)

Regenerate notebooks from the workspace root:

```bash
PYTHONPATH=../PyAutoHands/autohands python3 ../PyAutoHands/autohands/generate.py autogalaxy
```

`markdown/` is generated by a **separate** tool
(`PyAutoHands/autohands/generate_markdown.py`) — regenerate it too, and check
its project key and CWD requirements before running.

`scripts/check_sizes.sh` flags any changed script that shrank >50% against
`HEAD`. Per this repo's own bulk-edit rule: never whole-file write without
having read the entire current file.

## @autogalaxy_assistant — 8 hits

- `skills/ag_build_interferometer_model.md:278`
- `skills/ag_setup_environment.md:107`
- `wiki/core/api/datasets.md:184`
- `wiki/core/concepts/interferometer_theory.md:123`
- `wiki/core/operations/installation.md:103,118` — the `optional` table still
  lists `pynufft` as an extra

Wiki **body** edits require `--write-provenance`.

## @autolens_assistant — 2 live hits

- `chat_pack/05_wiki_api_reference.md:178`
- `wiki/core/api/analysis_objects.md:72`

Both still say the legacy backend "is still available". `paper/` in this repo is
**out of scope** (see below).

## Do NOT touch

`paper/` directories in any repo — published JOSS records of what the software
used at time of publication. `remove_pynufft_legacy_transformer.md` made this
call explicitly.

## Acceptance

- No repo above advertises `TransformerNUFFTPyNUFFT` as available.
- Installation tables no longer list `pynufft` under `optional`.
- `notebooks/` and `markdown/` regenerated from `scripts/`, committed alongside,
  and consistent with them — not hand-edited.
- `git diff --stat` confirms no `paper/` file changed.
