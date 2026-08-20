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
