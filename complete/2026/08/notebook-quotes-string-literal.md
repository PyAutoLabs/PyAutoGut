`add_notebook_quotes` decided what was a narrative docstring with a line-prefix
test, so a triple-quoted string literal **assigned in code** defeated it: the
opener is indented behind `s = ` and invisible to the test, but the closing
delimiter sits at column 0 and matched. Every cell boundary after it inverted —
the enclosing code cell became an unterminated-string `SyntaxError` and the
following code was emitted as narrative prose. Same failure class as
PyAutoHands#211's opener bug, opposite trigger.

Cell segmentation now comes from `_narrative_docstring_ranges`, which parses the
script and takes the module-level bare string expression statements. `ast`
separates a docstring from a string bound to a name by node type, so the
confusion cannot recur. `strip_env_declarations` moved to the same helper, and
`navigator.py` needed no change — it already reads its blocks back out of
`add_notebook_quotes`.

**Latent, not shipping.** One file workspace-wide had the trigger shape (a
gallery-build script's module-level `CSS` block); it sits outside `scripts/`,
which `iter_script_paths` alone walks, so it was never converted. That is why it
was deferred from #211 rather than fixed there.

## Two corrections to the plan

1. **`strip_env_declarations` was not a live defect.** The plan claimed it shared
   the bug. It doesn't — the false "opener" match fires, but every non-`__Env__`
   path emits the block verbatim, so the misparse is absorbed. It shipped as
   hardening (one segmentation source instead of two prefix tests that can
   drift), and its test is a pin, not a regression.
2. **A second latent defect was found and fixed in passing.** The prefix test
   also missed an *indented* closing delimiter, so the block never closed and
   everything after was swallowed into the markdown cell — the mirror of #211.
   Three files carry that shape, all outside `scripts/`.

## Evidence

- `pytest PyAutoHands/tests/` — 349 passed (was 340). CI green on 3.12 / 3.13 / 3.14.
- **Control test:** the 8 new behavioural tests were run against the pre-fix
  module and all 8 fail there. The 9th passes before and after — correctly, per
  correction 1.
- **Zero-diff:** old vs new over 693 converted scripts (byte-identical, 0 new
  raises) and 60 real scripts end-to-end through `ipynb-py-convert` (0 notebook
  JSON differences). Done by direct comparison, so no workspace tree was touched.
- **Divergence audit:** 18 of 1517 workspace `.py` files where old and new
  disagree — all outside `scripts/`, each inspected, new behaviour correct in
  every case.

## Notes

- CI's first failure was the **tenant firewall**, not pytest: a test comment
  named a tenant repo inside organ code. Fixed by rewording, not allowlisting.
- Heart was `stale`/85 at ship time (sole reason: PyAutoGalaxy release-validation
  staleness, unrelated); the human acknowledged that one reason.
- Workspace impact (iii) none. `/smoke_test` was not applicable — it executes
  workspace scripts, and this change is confined to the notebook generator.

## Original prompt

# `add_notebook_quotes` mistakes a code string literal's closing delimiter for a docstring

Type: bug
Target: hands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: safe
Priority: low

`add_notebook_quotes` decides what is a narrative docstring with a line-prefix
test (`add_notebook_quotes.py`):

```python
if line.startswith('"""') or line.startswith("'''"):
```

A triple-quoted **string literal** assigned in code opens on a line that does
*not* start at column 0 (`s = """`), so the opener is invisible to the test —
but its **closing** delimiter usually sits at column 0, and that line *does*
match. It flips `is_in_quotes`, and every cell boundary after it is inverted.

Reproduced:

```python
"""
__Intro__
"""

x = 1
s = """
literal
"""
print(s)
```

converts to a final code cell whose source is

```python
x = 1
s = """
literal
# %%
'''
print(s)
```

— the literal's closing delimiter became a cell marker, and `print(s)` landed
inside a broken string. Same failure class as
PyAutoLabs/PyAutoHands#211's opener bug, different trigger.

## Reachability

One occurrence workspace-wide, found by scanning every `.py` in the four
workspaces, their `_test` / `_developer` siblings, and the three HowTo repos for
a column-0 triple-quote-closing line belonging to a code string:

- `autolens_workspace_test/gallery/gallery_build.py:42`

`gallery/` sits outside `scripts/`, and `iter_script_paths` only walks
`scripts/`, so this file is **never converted** — the bug is latent, not
shipping. That is why it was left out of #211 rather than fixed there.

## Fix

Replace the line-prefix test with real tokenization. `tokenize.generate_tokens`
yields `STRING` tokens with exact `start`/`end` line numbers, which distinguishes
a module/narrative docstring (a bare `STRING` expression statement) from a string
bound to a name. `strip_env_declarations` and `navigator.py` share this same
tokenizer-by-line-prefix assumption (`add_notebook_quotes.py` docstring: "the
single shared strip layer"), so all three should move together or the catalogue
and the notebooks will disagree.

Cheaper interim option, if tokenizing is judged too invasive: raise on a column-0
triple-quote line that closes a string the scanner never saw opened. Loud beats a
silently mangled cell, and matches the stray-`# %%` guard added in
PyAutoLabs/PyAutoHands#214.

## Validation

- The reproducer above yields `[markdown, code]` with the literal intact inside
  the code cell, and no cell source containing `# %%`.
- The existing `tests/test_add_notebook_quotes.py` suite stays green.
- Regenerating all six artifact-bearing workspaces produces a **zero diff** —
  no live script has the shape, so a correct fix must change nothing.
- `navigator` catalogues are unchanged for the same reason.

## Notes

- Found 2026-07-30 while fixing the docstring-after-code split
  (PyAutoLabs/PyAutoHands#211 / #214).
