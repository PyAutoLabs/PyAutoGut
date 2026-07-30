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
