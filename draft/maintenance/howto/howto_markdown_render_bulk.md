# Shrink HowTo committed markdown/ render bulk

Type: maintenance
Target: howto
Repos:
- HowToLens
- HowToGalaxy
- HowToFit
- PyAutoHands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 4 of the dataset-bulk series. The HowTo repos' dataset problem is solved; their real
committed bulk is `markdown/` — rendered tutorial output (PNGs + captured stdout) that is
**regenerable on demand** by PyAutoHands `generate_markdown.py` (stated in each repo's
`markdown/README.md`). Structurally the exact analogue of the committed-dataset problem.

## Verified facts (2026-07-27 survey)

| Repo | Tracked `markdown/` | Share of tracked tree | Worst blobs |
|---|---|---|---|
| HowToLens | **7.7 MB** (80 PNG, 10 MD) | **79%** | 776 KB / 739 KB / 523 KB PNGs in chapter_1 |
| HowToGalaxy | **3.9 MB** (57 PNG, 6 MD) | ~70% | 661 KB / 362 KB PNGs |
| HowToFit | **2.0 MB** (31 PNG, 7 MD) | ~68% | see stdout dump below |

- **Stdout-dump anomaly:** `HowToFit/markdown/chapter_1_introduction/tutorial_4_why_modeling_is_hard.md`
  is **607 KB / 7,757 lines** of captured non-linear-search log text (no base64), committed
  twice in history (~1.2 MB of pack). `tutorial_3_non_linear_search.md` (59 KB) is the
  same failure smaller. This is a generation-side bug: `generate_markdown.py` should
  truncate/elide captured search output.
- Notebooks are clean (zero output cells in all 82 `.ipynb` across the three repos); no
  committed `output/` anywhere.

## Decision needed (human) before any purge

Are the `markdown/` directories load-bearing — linked from the docs hub / RTD / read by
users browsing GitHub? Options:

1. **Purge** like the datasets (drop from tracking, regenerate on demand) — biggest win
   (~13.4 MB working tree), but kills GitHub-rendered tutorial browsing if anyone uses it.
2. **Compress at generation** — downscale/optimize PNGs and truncate captured stdout in
   `generate_markdown.py`, then regenerate — keeps the rendered pages, roughly halves the
   bulk, and stops future growth.
3. Status quo + stdout-truncation fix only.

The stdout-truncation fix in PyAutoHands is worth doing under every option.

## Out of scope

- History bytes (purged dataset blobs, duplicated 607 KB markdown) — recovering them
  needs a history rewrite, which is forbidden (never rewrite pushed history).
- Loose-object `.git` bloat — one-off `git gc` done 2026-07-27; the recurring gc step
  belongs to `draft/maintenance/pyautobrain/clean_slate_write_site_provenance.md`.
