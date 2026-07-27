# Migrate HowToFit auto-simulate guards to should_simulate

Type: maintenance
Target: HowToFit
Repos:
- HowToFit
- PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Leg 3 of the dataset-bulk series. The HowTo repos have **no** committed-dataset problem
(all three blanket-ignore `dataset/`, track zero data files, purge leg #151 already
landed). But HowToFit is the one repo in the organism still on the old raw guard idiom,
which the `should_simulate` migration everywhere else was written to replace.

## Verified facts (2026-07-27 survey)

- HowToLens has 25 `al.util.dataset.should_simulate(...)` sites, HowToGalaxy has 21
  `ag.util.dataset.should_simulate(...)` sites — full coverage, implementation at
  `PyAutoArray/autoarray/util/dataset_util.py:54`.
- HowToFit has **11 raw sites** of `if not path.exists(dataset_path): subprocess.run([...])`:
  `scripts/chapter_1_introduction/tutorial_2_fitting_data.py:88`,
  `tutorial_3_non_linear_search.py:169`, `tutorial_4_why_modeling_is_hard.py:68`,
  `tutorial_5_results_and_samples.py:59`, and all 7 scripts in
  `scripts/chapter_3_graphical_models/`.
- Consequence: `PYAUTO_SMALL_DATASETS=1` cannot force-regenerate stale full-resolution
  data in HowToFit — the guard only fires when the dataset is absent.

## The likely reason it was never migrated (resolve this first)

`should_simulate` lives in **PyAutoArray**, but HowToFit imports only `autofit`, and
autofit does **not** depend on autoarray (they are independent roots of the dependency
graph). Options, pick one deliberately:

1. Add a `should_simulate` equivalent to PyAutoFit (small util mirroring
   `autoarray/util/dataset_util.py:54`) and migrate the 11 sites to `af.util.…` —
   consistent with the sibling repos, but a (tiny) library change.
2. Vendor a small local helper in `HowToFit/scripts/simulators/util.py` — no library
   change, slightly off-pattern.
3. Reject the migration and record why — then close this prompt.

## Also in scope

- The paired notebooks for the 11 scripts regenerate through the normal ship_workspace
  path.
- Writers live in `scripts/simulators/{simulators.py,simulators_sample.py,util.py}`
  (20+ targets under `dataset/example_1d/`) — no changes expected there beyond what the
  guard helper needs.

## Out of scope

- HowTo `markdown/` render bulk → `draft/maintenance/howto/howto_markdown_render_bulk.md`.
- clean_slate's silent no-op on the HowTo repos →
  `draft/maintenance/pyautobrain/clean_slate_write_site_provenance.md`.
