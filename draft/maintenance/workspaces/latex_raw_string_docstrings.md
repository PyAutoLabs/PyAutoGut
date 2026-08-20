# Raw-string the LaTeX docstrings across the six workspace repos

Type: maintenance
Target: workspaces
Repos:
- HowToFit
- HowToGalaxy
- HowToLens
- autofit_workspace
- autogalaxy_workspace
- autolens_workspace
Difficulty: medium
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
double-backslashes, which would leak into the rendered notebook prose.

## Survey 2026-08-20 — scope and prerequisite both corrected

A full sweep at `/start_dev` time found the original four lines to be a small
corner of the problem, and found a hard dependency the prompt did not know
about. Both sweeps are ~20 lines each and specified below — rebuild them rather
than trusting these counts blind.

### BLOCKED BY: `draft/bug/hands/raw_string_docstring_prefix.md`

Two PyAutoHands docstring parsers **silently** mis-handle an `r"""` opener, so
raw-stringing these scripts today would break the generated artefacts rather
than fix them. Both reproduced, neither raises:

- `add_notebook_quotes.py:67` — the `r"""` block is not recognised as a cell
  boundary, so **the tutorial prose ships as a Python code cell**.
- `env_config.py:110` — block parity inverts and `read_env_declaration` returns
  `None` instead of the declared tokens. **Seven `autolens_workspace` scripts
  here carry `__Env__` sections** (3 under `scripts/guides/`, 4 under
  `.../potential_correction/`), so their smoke env profile would be silently
  rerouted.

Do not start this task until that Hands fix has merged.

### Two sweeps are needed, not one

`SyntaxWarning` only fires for escapes Python does **not** recognise. The
escapes it *does* recognise fire silently and corrupt the string with no
diagnostic at all — `\t` in `\theta`, `\f` in `\frac`, `\r` in `\rm`, `\b` in
`\beta`, `\a` in `\alpha`, `\v` in `\vec`. Today `\theta_E` in the
`tutorial_3_scaling_relation.py` prose is literally `TAB + "heta_E"`.

- warning sweep: `compile(src, path, "exec")` under
  `warnings.simplefilter("always")`, collecting `SyntaxWarning` — **171 hits**.
- silent sweep: walk the AST, and for every non-raw `str` constant whose source
  segment contains a backslash, flag any control character (`ord < 32`, `\n`
  excepted) in the *value* — **132 hits**.

`HowToLens/scripts/chapter_4_scaling_up_lensing/tutorial_5_cluster_scale.py`
has **only** silent hits and zero warnings, so a warning-only sweep skips it
entirely. Drive the edit off the union of both.

Notebooks are **not** currently corrupt: the generator reads source text, not
runtime values, so `notebooks/*.ipynb` already carry the correct `\theta_E`.
This is warning noise plus latent breakage, not a shipped-artefact bug.

### Scope — 41 files, 6 repos

**HowToFit** (4 files)
- `scripts/chapter_1_introduction/tutorial_1_models.py` — 2 warned, 2 silent
- `scripts/chapter_1_introduction/tutorial_2_fitting_data.py` — 5 warned, 5 silent
- `scripts/chapter_1_introduction/tutorial_3_non_linear_search.py` — 1 warned, 0 silent
- `scripts/chapter_1_introduction/tutorial_4_why_modeling_is_hard.py` — 5 warned, 0 silent

**HowToGalaxy** (4 files)
- `scripts/chapter_1_introduction/tutorial_1_grids_and_galaxies.py` — 5 warned, 3 silent
- `scripts/chapter_1_introduction/tutorial_3_fitting.py` — 7 warned, 6 silent
- `scripts/chapter_2_modeling/tutorial_1_non_linear_search.py` — 1 warned, 1 silent
- `scripts/chapter_3_pixelizations/tutorial_5_bayesian_formalism.py` — 7 warned, 3 silent

**HowToLens** (8 files)
- `scripts/chapter_1_introduction/tutorial_1_grids_and_galaxies.py` — 6 warned, 3 silent
- `scripts/chapter_1_introduction/tutorial_2_ray_tracing.py` — 2 warned, 2 silent
- `scripts/chapter_1_introduction/tutorial_4_point_sources.py` — 1 warned, 2 silent
- `scripts/chapter_1_introduction/tutorial_7_fitting.py` — 7 warned, 6 silent
- `scripts/chapter_2_lens_modeling/tutorial_1_non_linear_search.py` — 1 warned, 1 silent
- `scripts/chapter_3_pixelizations/tutorial_5_bayesian_formalism.py` — 7 warned, 4 silent
- `scripts/chapter_4_scaling_up_lensing/tutorial_3_scaling_relation.py` — 2 warned, 2 silent
- `scripts/chapter_4_scaling_up_lensing/tutorial_5_cluster_scale.py` — 0 warned, 1 silent

**autofit_workspace** (2 files)
- `scripts/cookbooks/configs.py` — 1 warned, 0 silent
- `scripts/overview/overview_1_the_basics.py` — 1 warned, 1 silent

**autogalaxy_workspace** (6 files)
- `scripts/imaging/features/linear_light_profiles/likelihood_function.py` — 4 warned, 4 silent
- `scripts/imaging/features/multi_gaussian_expansion/likelihood_function.py` — 4 warned, 4 silent
- `scripts/imaging/features/pixelization/likelihood_function.py` — 7 warned, 7 silent
- `scripts/imaging/likelihood_function.py` — 4 warned, 3 silent
- `scripts/interferometer/features/pixelization/likelihood_function.py` — 7 warned, 7 silent
- `scripts/interferometer/likelihood_function.py` — 4 warned, 3 silent

**autolens_workspace** (17 files)
- `scripts/group/features/linear_light_profiles/likelihood_function.py` — 1 warned, 1 silent
- `scripts/group/features/multi_gaussian_expansion/likelihood_function.py` — 1 warned, 1 silent
- `scripts/group/likelihood_function.py` — 4 warned, 3 silent
- `scripts/guides/galaxies.py` — 1 warned, 0 silent  *(carries `__Env__`)*
- `scripts/guides/results/aggregator/data_fitting.py` — 1 warned, 0 silent  *(carries `__Env__`)*
- `scripts/guides/tracer.py` — 1 warned, 0 silent  *(carries `__Env__`)*
- `scripts/imaging/features/advanced/potential_correction/likelihood_function.py` — 12 warned, 7 silent  *(carries `__Env__`)*
- `scripts/imaging/features/advanced/potential_correction/start_here.py` — 5 warned, 3 silent  *(carries `__Env__`)*
- `scripts/imaging/features/linear_light_profiles/likelihood_function.py` — 5 warned, 4 silent
- `scripts/imaging/features/multi_gaussian_expansion/likelihood_function.py` — 5 warned, 4 silent
- `scripts/imaging/features/pixelization/likelihood_function.py` — 8 warned, 9 silent
- `scripts/imaging/likelihood_function.py` — 7 warned, 7 silent
- `scripts/interferometer/features/advanced/potential_correction/likelihood_function.py` — 10 warned, 5 silent  *(carries `__Env__`)*
- `scripts/interferometer/features/advanced/potential_correction/start_here.py` — 3 warned, 1 silent  *(carries `__Env__`)*
- `scripts/interferometer/features/pixelization/likelihood_function.py` — 8 warned, 9 silent
- `scripts/interferometer/likelihood_function.py` — 7 warned, 7 silent
- `scripts/point_source/fit.py` — 1 warned, 1 silent

The four matplotlib labels in
`HowToFit/.../tutorial_4_why_modeling_is_hard.py` (`'Normalized Residuals
($\sigma$)'`, lines 437/604/712/820) are runtime strings, not docstrings — same
`r` prefix, same reason.

### Deliberately EXCLUDED

- `autolens_workspace/dataset/cluster/a2744/prep.py:38` — `line.split("\t")` is
  a genuine tab in a TSV parser, not LaTeX. Leave it.
- `PyAutoGalaxy` (4 warnings: `operate/lens_calc.py`, `util/mock/mock_cosmology.py`)
  and `PyAutoCTI` (19 warnings: `extract/two_d/*`, `instruments/acs/array_2d.py`).
  Same defect, but library source — needs `ship_library` and a pending-release
  gate, so it does not belong on a prose-only workspace PR. File separately.
- `autocti_workspace`, every `*_workspace_test` / `*_workspace_developer`, and
  `PyAutoFit` / `PyAutoArray` / `PyAutoLens` source: swept, **zero** hits.

## Verification per repo (the diff-empty gate)

1. Both sweeps return zero.
2. Regenerate:
   `PYTHONPATH=../PyAutoHands/autohands python3 ../PyAutoHands/autohands/generate.py <project>`
   (`howtofit`, `howtogalaxy`, `howtolens`, `autofit`, `autogalaxy`, `autolens`).
3. **`git diff notebooks/ markdown/ llms-full.txt workspace_index.json` must be
   empty.** The generator swaps the delimiter line for `'''` either way, so the
   generated artefacts are byte-identical before and after. A non-empty diff
   means the Hands prerequisite is incomplete — this is the gate, not a
   formality.
4. `read_env_declaration` still returns its tokens for all 7 `__Env__` files.

Ship as six independent PRs, one per repo. Prose-only, no API surface, so no
cross-repo merge ordering.

## Follow-up worth filing

A `-W error::SyntaxWarning` compile guard in workspace CI, so this cannot
regress. Note it would catch only the 171-hit class; the silent class needs the
AST sweep above.
