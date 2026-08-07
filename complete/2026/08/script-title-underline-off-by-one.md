Fixed the off-by-one RST title underlines across autolens_workspace scripts.
autolens_workspace#478 MERGED 2026-08-07 (573bde8c, merge commit; single change
commit 5844ad5), closing issue #476. Branch `claude/dev-script-title-underline-5d3c3p`
(session-designated — a Claude Code web session may push only that branch, so it
replaced the `feature/<name>` convention; the same-named PyAutoMind branch
carries this record until merged to Mind main).

- **Scope grew 29 → 41.** The prompt's 2026-07-30 measurement at 726d060d found
  29 typos; 12 more landed since with the scaling-relation and datacube feature
  families. Each fix is one line: rule set to exactly `len(title)` `=` chars.
- **Banner guard held.** Discriminator `abs(len(title)-len(rule)) <= 2` = typo,
  wider = deliberate full-width banner. Control-tested at 726d060d in a temp
  worktree, reproducing the recorded 29/15 split exactly before being trusted
  on main. Current main has 14 banner rules (one block removed upstream since);
  all 14 byte-untouched, re-verified after the fix (0 typos / 14 banners).
- **Notebooks**: the 41 paired notebooks regenerated via PyAutoHands
  generate.py; catalogue (llms-full.txt / workspace_index.json) regenerated
  with zero diff — underline rules do not flow into catalogue summaries.
  check_navigator --banners fail green, check_sizes green, all 41 scripts
  byte-compile. CI: both smoke legs (3.12/3.13) + all three navigator checks
  green in ~9 min.
- **KEY FINDING — repo-wide notebook regeneration drift (FILED, not fixed):**
  a generate.py dry-run against *unmodified* scripts modifies **331 committed
  notebooks by one line** — PyAutoHands build_util.py uncomments
  `# from autolens import setup_notebook; setup_notebook()` for notebook
  cells, but committed notebooks carry the commented form, so main's notebooks
  never call setup_notebook(). This PR brought only its own 41 notebooks to
  generator truth (39 carry the flip; 2 lack the line) and hand-restored the
  other ~290 regenerated files to keep the diff scoped. Follow-up prompt:
  `draft/maintenance/workspaces/notebook_setup_notebook_regen_drift.md`.
- **Environment trap:** `pip install ipynb-py-convert` fails on modern
  setuptools (`install_layout` AttributeError in bdist_wheel). Workaround:
  `pip download --no-deps --no-binary :all:`, copy the `ipynb_py_convert`
  package into site-packages, and write a 4-line `/usr/local/bin/ipynb-py-convert`
  entry-point shim — generate.py shells out to the CLI name.
- **Sizing note:** the Feature Agent's heuristic said large (score 8) /
  split-into-phases; overridden — prose-driven overestimate (same pattern as
  the mge-sigma-min sizing-note). Actual: small, single-phase, one PR.

## Original prompt

# Fix 29 off-by-one script title underlines in @autolens_workspace

Difficulty: small
Autonomy: safe
Priority: low

## The problem

Every workspace script opens with an RST-style title and an `===` rule that
should match the title's length:

```
Simulator: DSPL
===============
```

**29 scripts on `main` have a rule that is 1–2 characters off.** Measured at
`726d060d` (2026-07-30). Examples:

| File | Title len | Rule len |
|---|---|---|
| `scripts/cluster/likelihood_function.py:2` | 45 | 46 |
| `scripts/group/features/pixelization/slam.py:2` | 24 | 25 |
| `scripts/group/features/linear_light_profiles/slam.py:2` | 33 | **35** |
| `scripts/cluster/lenstool/parameterization_mapping.py:2` | 64 | 63 |
| `scripts/interferometer/features/datacube/data_preparation.py:2` | 26 | 28 |
| `scripts/imaging/features/advanced/mass_stellar_dark/slam.py:2` | 46 | 47 |

Most are `rule = title + 1`, consistent with a title being edited without
re-counting the rule.

## Scope — 44 raw matches, only 29 are real

A naive scan for "line of `=` whose length ≠ the line above" returns **44** hits.
**15 of those are false positives** and must be left alone: they are deliberate
full-width ASCII banner blocks where an 78–98 char rule sits under a short line
(often a bare `"""`). Examples:

```
scripts/guides/results/start_here.py:97      '   MODEL FIT'          rule=78
scripts/cluster/mass_parameterizations_pyautolens.py:94                rule=80
scripts/interferometer/features/datacube/likelihood_function.py:238    rule=98
```

**Discriminator that worked:** treat `abs(len(title) - len(rule)) <= 2` as a real
typo and anything wider as an intentional banner. That split gives 29 / 15. Do
not skip this classification — a blanket "make the rule match the line above"
pass would mangle all 15 banners.

## Impact

Cosmetic in the scripts themselves, but the titles flow into generated notebook
markdown cells and into the navigator catalogue summaries, so the mismatch is
user-visible in rendered docs where RST-ish underlines are interpreted.

## Proposed fix

Scripted pass over `scripts/**/*.py`: for each title/rule pair with a
length delta of ≤2, set the rule to `len(title)` characters. Then regenerate
notebooks and the catalogue as usual.

Mind the notebook side: titles live in markdown cells too, so either regenerate
from scripts or apply the same edit in lockstep and prove it by regeneration.

## Verification

- Re-run the classifier: 0 remaining `<=2` mismatches, **still exactly 15** wide
  banner blocks (assert the banner count is unchanged — that is the guard
  against clobbering them)
- Notebooks byte-identical to generator output
- `check_navigator.py --root workspace --banners=fail` green

## Provenance

Surfaced as a side-observation while shipping the DSPL rename
(autolens_workspace#394), which introduced none of them — that PR's own files
were verified clean. Never investigated further at the time.
