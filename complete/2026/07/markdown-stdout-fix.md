## markdown-stdout-fix
- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/200
- completed: 2026-07-27
- library-pr: https://github.com/PyAutoLabs/PyAutoHands/pull/201
- workspace-pr: https://github.com/PyAutoLabs/HowToFit/pull/34
- summary: Leg 4 of the dataset-bulk series, human-decided scope after the load-bearing investigation killed the purge premise (markdown/ churn nil — 2 PNG re-commits ever; untracking reclaims ~0 clone bytes since blobs stay in history; renders are the ONLY no-install figure view because committed notebooks are output-stripped; retro-compression ADDS packed bytes). Shipped: generate_markdown.py now merges each cell's consecutive stream outputs before cleaning (samplers emit each progress update as its own one-line stream output, so the 40-line cap never fired), collapses NNNNit progress runs to their final state tolerating nbconvert's blank-line paragraph interleave (a naive consecutive-line collapse matched ZERO of the 2,480 committed spam lines), and optimizes newly extracted PNGs (256-colour quantize, 35-43% of originals, forward-only — committed images untouched; next full autolens_workspace re-render ~56→~20 MB). Post-hoc repair via the same module function: HowToFit tutorial_4 607 KB/7,758 lines → 62 KB/1,476 lines (was over GitHub's 512 KB render threshold and displayed raw with no images; now renders with all 10 figures), tutorial_3 58→52 KB (5 figures intact). 7 new unit tests; suite 234 passed. Shipped under the 2026-07-27 heart-ack. Merged 2026-07-27: Hands aee90f899, HowToFit da8863a6a.

## Original prompt

# Markdown generator: per-cell stdout truncation + PNG optimization; repair tutorial_4

Type: maintenance
Target: hands
Repos:
- PyAutoHands
- HowToFit
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 4 of the dataset-bulk series, rescoped 2026-07-27 by human decision after the
load-bearing investigation (supersedes the purge-vs-compress framing of
`howto_markdown_render_bulk.md`). **Do not purge, do not retro-compress**: `markdown/`
churn is nil (2 PNG re-commits ever, workspace-wide), untracking reclaims ~0 clone bytes
(blobs stay in history; rewrites forbidden), and the renders are the ONLY place tutorial
figures are visible without running the stack (committed notebooks are output-stripped —
the READMEs' "images render inline" is only true via `markdown/`). Retro-compression
ADDS packed bytes. Decision: fix the generator forward-only and repair the one broken page.

## The defect

`HowToFit/markdown/chapter_1_introduction/tutorial_4_why_modeling_is_hard.md` is
608 KB / 7,757 lines, 71% dynesty progress spam (2,480 separate `NNNNit [...]` lines).
At 608 KB it exceeds GitHub's 512 KB markdown-render threshold — the page likely shows
raw source with no images, defeating its purpose. Root cause: `generate_markdown.py`
`_clean_stream_text` (lines 149–167) truncates **per stream-output object**
(`clean_notebook_outputs`, 175–182); dynesty/tqdm emit each progress line as its own
object, so every object is 1 line and the 40-line cap never fires.
`tutorial_3_non_linear_search.md` (59 KB) is the same failure smaller.

## Scope

1. **PyAutoHands `generate_markdown.py`:**
   - Truncate the *concatenated per-cell* stream output (head 10 / tail 20 semantics
     preserved), not each object; collapse `^\s*\d+it \[` progress runs to their last
     state.
   - Add a forward-only PNG optimization pass after `nbconvert --to markdown`
     (256-colour quantize + optimize; measured 35–43% of original size). Applies to new
     renders only — existing committed PNGs stay untouched (retro-commit is net-negative).
   - Unit tests for the stream-cleaning transform (pure function).
2. **HowToFit:** apply the same transform post-hoc to the committed `tutorial_4` (and
   `tutorial_3`) markdown — 608 KB → ~170 KB, back under the render threshold, zero
   re-execution — verify image refs intact.

## Out of scope

- Any purge/untrack of `markdown/` (decision: keep).
- Re-rendering (HowToFit search tutorials cost 90–120 min runs).
- autolens/autogalaxy/autofit workspace `markdown/` — they benefit automatically at
  their next re-render via the generator change.
