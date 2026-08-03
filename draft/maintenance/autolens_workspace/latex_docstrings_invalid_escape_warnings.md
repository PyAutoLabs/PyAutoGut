# LaTeX in non-raw docstrings emits SyntaxWarning: invalid escape sequence

Type: maintenance
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

## Origin

Split out of #457 (potential-correction `ENV: full_datasets` declarations, PR #459 merged
2026-08-03). Observed while running those scripts under the smoke profile; deliberately NOT bundled
there because it is unrelated to the dpsi-mesh failure and warrants a wider pass than three files.

## The problem

Workspace scripts write LaTeX in ordinary (non-raw) triple-quoted docstrings, so Python parses
`\o`, `\c`, `\d`, `\,`, `\p`, `\s` as escape sequences and emits `SyntaxWarning: invalid escape
sequence` on every run. Observed on all four potential-correction scripts:

```
scripts/imaging/features/advanced/potential_correction/start_here.py:11: SyntaxWarning: invalid escape sequence '\d'
  pixelized corrections $\delta\psi$ to the lensing potential are defined on a coarse regular mesh
scripts/imaging/features/advanced/potential_correction/start_here.py:72: SyntaxWarning: invalid escape sequence '\,'
  ... $10^{10} \, M_\odot$ NFW dark ...
scripts/interferometer/features/advanced/potential_correction/likelihood_function.py:297: SyntaxWarning: invalid escape sequence '\,'
  - the curvature is $F = A^T \, (T^H C^{-1} T) \, A$ ...
```

Roughly a dozen warnings per script across the four. These are currently benign — Python still
stores the literal backslash — but the behaviour is deprecated and is scheduled to become a
`SyntaxError`, so this is a latent break, not only noise.

## Scope to establish first

Do **not** assume this is confined to potential_correction. Sweep the workspace (and likely the
sibling workspaces + HowTo* repos) before deciding the fix's size:

```bash
python3 -W error::SyntaxWarning -c "import py_compile,sys; py_compile.compile(sys.argv[1], doraise=True)" <script>
```

or compile every script and collect the warnings:

```bash
python3 -W always::SyntaxWarning -m compileall -q scripts/ 2>&1 | grep "invalid escape sequence"
```

Report the count and the distinct repos affected before proposing the change.

## Candidate fixes (decide after the sweep)

1. **Raw docstrings** — prefix the affected docstrings with `r"""`. Minimal and local, but the
   `r` prefix appears in the user-facing script text and is carried into generated notebooks and
   markdown; check how it renders before committing to it.
2. **Escape the backslashes** (`\\delta`) — leaves the docstring non-raw but doubles every
   backslash, which is noisier to read and easy to regress.

Option 1 is the conventional fix; option 2 is listed so the trade-off is on the record.

## Constraints

- Docstring content is user-facing tutorial prose — do not reword the LaTeX or the surrounding
  sentences while fixing the escapes. Prose changes belong to a docs task, not this one.
- Notebooks are regenerated, never hand-edited. Verify the regenerated `.ipynb` renders the maths
  identically, and check `workspace_index.json` / `llms-full.txt` for unintended churn.
- Verify with `-W error::SyntaxWarning` afterwards so the fix is proven by the warning
  disappearing, not by the script merely still running.

## Related

- `complete/2026/08/potential-correction-env-declaration.md` — the task this was split from.
