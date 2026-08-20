# Teach the notebook/env parsers to accept raw-string (`r"""`) docstrings

Type: bug
Target: hands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: safe
Priority: medium
Status: formalised

Filed 2026-08-20 from the `/start_dev` survey of
`draft/maintenance/workspaces/latex_raw_string_docstrings.md`, which needs to
raw-string 41 workspace tutorial scripts and **cannot** until this lands.

PyAutoHands has two independent docstring parsers, and **both silently
mis-handle an `r"""` opener**. Neither raises. There are currently zero `r"""`
narrative docstrings in any workspace repo, which is why this has never fired.

## The two sites

1. `autohands/add_notebook_quotes.py:67` — `_narrative_docstring_ranges`:

   ```python
   if not (lines[start].startswith('"""') or lines[start].startswith("'''")):
       # A column-0 string statement written with a single-quote delimiter
       # was never a cell boundary; leave it as code, as it always was.
       continue
   ```

   An `r"""` block is a perfectly good `ast.Expr(Constant(str))` at
   `col_offset == 0`, so it reaches this test and then fails it. The block is
   dropped as a cell boundary and **the tutorial prose ships as a Python code
   cell** containing a bare string literal.

2. `autohands/env_config.py:110` — `_DOCSTRING_DELIM_RE`:

   ```python
   _DOCSTRING_DELIM_RE = re.compile(r"^(?:\"\"\"|''')\s*$")
   ```

   `read_env_declaration` is deliberately line-based (no `ast`). An `r"""`
   opener does not match, so the scan walks past it and matches the block's
   **closing** delimiter as an opener instead. Block parity inverts for the rest
   of the file, and an `__Env__` section further down is read as if it were
   outside a docstring — **the `ENV:` declaration is silently lost**.

## Reproduction (both confirmed, 2026-08-20)

`add_notebook_quotes` — a probe file with an `r"""` block followed by a plain
`"""` block:

```
ranges: [(7, 9)]        # only the plain block; the r-string block is invisible
```

and the converted output leaves `r"""` … `"""` verbatim inside the code cell
rather than emitting `# %%` + `'''` around it.

`read_env_declaration` — two files identical but for an `r` on an earlier
docstring, each carrying a valid bottom-of-file `__Env__` / `ENV: jax` section:

```
probe_env_plain.py -> ['jax']
probe_env.py       -> None          # silently dropped
```

Seven `autolens_workspace` scripts carry `__Env__` sections (3 under
`scripts/guides/`, 4 under `.../potential_correction/`), so site 2 would
silently reroute their smoke env profile the moment an earlier docstring in
those files is raw-stringed.

## Fix

- Site 1: accept an optional `r`/`R` prefix on either delimiter. The converter
  *replaces* the opener line with `'''` when it emits the cell, so the prefix
  disappears from the generated notebook on its own — no downstream change.
- Site 2: `_DOCSTRING_DELIM_RE = re.compile(r"^[rR]?(?:\"\"\"|''')\s*$")`.

Cover `r"""`, `R"""`, `r'''`, `R'''`.

## Checked and NOT affected

- `autohands/generate_markdown.py:139` — `re.search(r'"""(.*?)"""', text)` finds
  the `"""` after the `r`, so `script_title` extracts the same content.
- `autohands/navigator.py:108` — reads the **converted** output, which is
  already normalised to `'''`.

## Tests

Add to `PyAutoHands/tests/`, locking both reproductions above as regressions:

- `test_add_notebook_quotes.py` — an `r"""` narrative block becomes a markdown
  cell, byte-identical to the same block without the prefix.
- `test_strip_env_declarations.py` — an `r"""` block carrying `__Env__` strips
  the same way as a plain one.
- `read_env_declaration` returns its tokens when an **earlier** docstring in the
  file is raw — the parity case, which a single-block test would miss.

## Blocked by

`hands-hygiene-leftovers` currently claims PyAutoHands
(`~/Code/PyAutoLabs-wt/hands-hygiene-leftovers`, branch
`feature/hands-hygiene-leftovers`, 3 dirty files). Start this once that ships.
