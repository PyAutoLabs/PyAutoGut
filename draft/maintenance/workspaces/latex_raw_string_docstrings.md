# Raw-string the LaTeX docstrings emitting SyntaxWarnings (HowToFit + HowToLens)

Type: maintenance
Target: workspaces
Repos:
- HowToFit
- HowToLens
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised

Filed 2026-08-06 from the `/cli_noise_clean` audit plus a compile check during
the hygiene-howto-refs-docstrings batch. Non-raw docstrings containing LaTeX
emit `SyntaxWarning: invalid escape sequence` on every compile/import:

- `HowToFit/scripts/chapter_1_introduction/tutorial_1_models.py:100,309`
  (`\sigma`, `\lambda`)
- `HowToLens/scripts/chapter_4_scaling_up_lensing/tutorial_3_scaling_relation.py:71,585`
  (`\sigma`, `\theta_E`)

Fix: make the enclosing docstrings raw (`r"""..."""`) — preferred over
double-backslashes, which would leak into the rendered notebook prose. Sweep
the sibling HowTo/workspace tutorial scripts for the same pattern
(`python3 -W error::SyntaxWarning -m py_compile` over `scripts/**/*.py`)
rather than fixing only the four known lines. Regenerate touched notebooks.
