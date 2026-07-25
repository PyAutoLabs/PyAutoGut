# Normalise CRLF line endings in PyAutoArray (+ add .gitattributes)

Type: maintenance
Target: libraries
Repos:
- @PyAutoArray
Difficulty: easy
Autonomy: full
Priority: low
Status: draft

## Context

PyAutoArray's AGENTS.md mandates Unix LF line endings, but a number of tracked
`.py` files are stored with CRLF in the git blobs. Observed during the
2026-07-24/25 heart-to-green work:

- `autoarray/inversion/mesh/image_mesh/abstract_weighted.py` — CRLF (edited
  matching-CRLF in #404 to keep the diff minimal)
- `autoarray/inversion/inversion/abstract.py` — CRLF
- the de-facto convention across `inversion/mesh/image_mesh/` is CRLF, while
  e.g. `inversion/plot/inversion_plots.py` is LF — the tree is mixed.

Two agents independently flagged this: naive text-mode edits rewrite whole
files (diff noise, review pain), and mixed endings make `.gitattributes`-less
checkouts platform-dependent.

## Task

1. Inventory: `git grep -Il $'\r' -- '*.py'` (and non-py text files) across
   PyAutoArray; consider the sibling libraries too if the same drift exists.
2. Normalise to LF in one dedicated, mechanical commit (no logic changes —
   easy to review with `git diff -w` / `--ignore-cr-at-eol`).
3. Add a `.gitattributes` (`* text=auto eol=lf` or targeted `*.py text eol=lf`)
   so the drift cannot recur.
4. Coordinate timing: land when no long-lived feature branches are open on the
   affected paths (a whole-file ending change conflicts with everything).

## Acceptance

- `git grep -Il $'\r' -- '*.py'` returns nothing in PyAutoArray.
- `.gitattributes` present; a fresh clone on Windows/WSL checks out LF.
- Zero behavioural diff (byte-identical modulo line terminators).
