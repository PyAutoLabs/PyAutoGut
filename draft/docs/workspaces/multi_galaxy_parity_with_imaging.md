# multi_galaxy examples: bring to parity with imaging

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal

The `scripts/multi_galaxy/` package is thinner than `scripts/imaging/` in
several ways. The user's request, verbatim:

> Issues with multi_galaxy examples:
>
>  - Im imaging/start_here.py the __Model__ is quite non technical and saves
>    the main stuff for modeling.py, there is too much detail in
>    multi_galaxy/start_here.py __Model__ so make it more like imaging.
>  - include in multi_galaxy/start_here.py __JAX__, __Iterations Per Update__
>    and __Live Visual Update__, __Extra Galaxy Removal GUI__, __Model Your Own
>    Lens__, both __Simulator__ sections.
> - Remove __Mass/Light Offsets__ from all examples (including modeling.py)
> - The modeling.py file is a users first end-to-end modeling example,
>   imaging/modeling.py has loads of info and context mutli_galaxy/modeling.py
>   does not. Make them the same level of detail, using as much of the text in
>   imaging's modeling.py wherever possible (but always adapt it to the multi
>   gaalxy use case).
> - The multi_galaxy fit.py file is also way over simplfieid compared to
>   imaging/fit.py, so do the same approach of getiong them to the same level
>   of detail.
> - Include likelihood_function.py, simulator_sample.py, source_science.py in
>   multi_galaxy.

## Scope

1. `scripts/multi_galaxy/start_here.py`
   - Trim `__Model__` to the non-technical register of `imaging/start_here.py`
     (defer the SIE-vs-dPIE / truncation / upgrade-path detail to
     `multi_galaxy/modeling.py`).
   - Add the pre-search `__JAX__` block (vmap/jit, `use_jax=False` debugging),
     `__Iterations Per Update__`, `__Live Visual Update__`,
     `__Extra Galaxy Removal GUI__` (Scribbler try/except), align
     `__Model Your Own Lens__` with imaging's, and add both `__Simulator__`
     sections (grid+tracer, then `SimulatorImaging`) adapted to the
     co-dominant pair.
   - Switch the search to `iterations_per_quick_update` + `live_visual_update`
     so the new prose matches the code.
2. Delete `__Mass/Light Offsets__` everywhere it appears — currently
   `multi_galaxy/start_here.py` and `multi_galaxy/modeling.py` (plus their
   `__Contents__` entries and generated notebooks).
3. `scripts/multi_galaxy/modeling.py` — bring to `imaging/modeling.py`'s level
   of detail, reusing imaging's prose wherever it transfers: Plotters,
   Over Sampling, Model Composition / Coordinates, Improved Lens Model
   (Sersic -> linear + MGE motivation), Search / Unique Identifier,
   Iterations Per Update, Live Visual Update, Analysis, JAX, VRAM Use,
   Run Times, Output Folder Layout, Result (incl. corner plot + loading from
   output folder), Source Science, Features, Data Preparation, HowToLens,
   Modeling Customization — each adapted to the multi-deflector case.
4. `scripts/multi_galaxy/fit.py` — same treatment against `imaging/fit.py`:
   Fitting, Bad Fit, Fit Quantities, Figures of Merit, Plane Quantities,
   Unmasked Quantities, Mask, Pixel Counting, Outputting Results, keeping the
   existing per-galaxy deflection-sum section that is genuinely multi-galaxy
   specific.
5. New `scripts/multi_galaxy/{likelihood_function,simulator_sample,source_science}.py`
   ported from the imaging equivalents and adapted:
   - `likelihood_function.py`: two lens galaxies, summed deflection field.
   - `simulator_sample.py`: draw random co-dominant *pairs*.
   - `source_science.py`: flux/magnification behind two deflectors.

## Constraints / known traps

- The `multi_galaxy/simple` dataset ships **no** `mask_extra_galaxies.fits`
  (its simulator writes none), so imaging's `__Extra Galaxies Noise Scaling__`
  sections in `modeling.py` / `fit.py` / `likelihood_function.py` cannot be
  ported verbatim. Either omit them or add the mask to the simulator — decide
  explicitly, do not silently load a file that does not exist.
- `multi_galaxy/start_here.py` **is** smoke-enabled (`smoke_tests.txt:11`)
  whereas `imaging/start_here.py` is not. The Scribbler GUI block and the new
  simulator sections must not hang or fail headless CI; if they do, either
  guard them or disable the entry with a documented reason.
- Whole-file `Write` is forbidden unless the entire current file was read
  (workspace `AGENTS.md` bulk-edit rule); run `scripts/check_sizes.sh` before
  committing.

## Acceptance

- Smoke suite green (`python .github/scripts/run_smoke.py`), with the three new
  scripts added to `smoke_tests.txt` if they run cleanly under
  `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1`.
- `scripts/multi_galaxy/README.md` Files list updated for the three new scripts.
- Notebooks regenerated and `workspace_index.json` refreshed via PyAutoHands.
- No `Mass/Light Offsets` string remains anywhere in the workspace.
