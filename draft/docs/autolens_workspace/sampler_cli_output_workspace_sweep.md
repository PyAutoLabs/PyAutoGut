# Phase 2 — drop the hand-written quick-update sentence from the workspace scripts

Follow-up to **PyAutoFit#1434 / PR#1436**, which moved the on-the-fly update
cadence message into the library. Do not start until #1436 has merged.

## Problem

23 workspace scripts print this block before `search.fit(...)`:

```python
print(
    """
    The non-linear search has begun running.

    This Jupyter notebook cell with progress once the search has completed - this could take a few minutes!

    On-the-fly updates every iterations_per_quick_update are printed to the notebook.
    """
)
```

The last line printed the literal name of the config knob. As of PyAutoFit#1436
the library logs the real cadence itself at search start
(`AbstractSearch.quick_update_message`, logged in `fit()`), so this sentence is
now both wrong *and* duplicated — and the library's version is the one that
states the actual number.

## Task

In each of the 23 `.py` scripts:

1. Delete the `On-the-fly updates every iterations_per_quick_update ...` line
   from the `print()` block. The library now emits this.
2. While in the same block, fix the typo present in several copies:
   "This Jupyter notebook cell **with** progress" → "**will** progress".
   (Some copies already say "will"; some use an em-dash rather than a hyphen —
   leave those punctuation differences alone, only fix the verb.)

Then regenerate the 23 `.ipynb` and 14 `.md` counterparts.

## Repos and counts

| Repo | scripts |
|------|---------|
| `autolens_workspace` | 14+ |
| `autogalaxy_workspace` | 3+ |
| `HowToLens` | 1 |

Find them all with:

```bash
grep -rln "On-the-fly updates every iterations_per_quick_update" --include=*.py .
```

Representative paths:

- `autolens_workspace/scripts/imaging/start_here.py:343`
- `autogalaxy_workspace/scripts/interferometer/start_here.py:327`
- `HowToLens/scripts/chapter_2_lens_modeling/tutorial_1_non_linear_search.py:416`

## Gotchas

- Regeneration: `generate.py` needs the repo as CWD and the **project key**
  (`autolens`, not `al`); the wrong CWD prints "0 scripts" and regenerates
  nothing. Verify by diffing the regenerated `.ipynb`/`.md` and confirming the
  sentence is gone from all three file types.
- `autolens_workspace` has historically carried several concurrent worktree
  claims — hand-check `active.md` and `~/Code/PyAutoLabs-wt/` before claiming it,
  and pre-merge `origin/main` before opening the PR.
- Prove completeness by re-running the grep above and getting **zero** hits
  across `.py`, `.ipynb` and `.md`.

## Verification

- `grep -rc "On-the-fly updates every iterations_per_quick_update" .` returns
  nothing in any file type.
- One regenerated notebook opens and its markdown cell reads correctly.
- A real fit from one edited script still prints the intro block, and the
  cadence line now comes from the library log instead.
