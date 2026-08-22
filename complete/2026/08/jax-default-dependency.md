# jax-default-dependency

**Completed 2026-08-22.** JAX became a default dependency across the family
(PyAutoLens#702): eleven PRs merged 2026-08-19 (six library — PyAutoHeart#150,
PyAutoNerves#150, PyAutoFit#1503, PyAutoArray#450, PyAutoGalaxy#574,
PyAutoLens#703 — plus five workspace: autolens_workspace#486,
autogalaxy_workspace#212, autofit_workspace#139, HowToLens#71, HowToGalaxy#67),
released as **2026.8.22.1** (nightly-release run 50, dispatched by hand after
the gates cleared), and closed out with the intra-family floor bumps
`>=2026.7.29.2` → `>=2026.8.22.1`: PyAutoFit#1509, PyAutoArray#466,
PyAutoGalaxy#582, PyAutoLens#708. PyAutoNerves needs no bump — its pyproject
carries no intra-family floor, so four PRs cover all five libraries' floors.

## Why the release (and therefore this task) sat blocked for two days

The promoting release was held up by two stacked regressions the task did not
cause, found and fixed while driving it out (2026-08-21/22 session):

- **PyAutoArray#453's in-place numba Cholesky kernels rejected JAX inputs**:
  the sparse-operator inversion path hands `fnnls_cholesky` JAX arrays even
  under `PYAUTO_DISABLE_JAX=1`; indexing a JAX array yields another JAX array,
  which numba maps to a *readonly* buffer, so kernel compilation died with
  "Cannot modify readonly array" — HowToLens smoke red from 2026-08-20 22:30,
  readiness RED, nightly blocked. Fixed by boundary coercion to numpy
  (PyAutoArray#463) with a jnp-input regression test. The scipy solvers #453
  replaced tolerated JAX input by copying internally — an in-place rewrite of
  a copy-tolerant seam must re-check every caller's array provenance.
- **The rectangular mesh split (PyAutoArray#462 et al.) merged library-side
  without its downstream legs**, breaking the retired `RectangularAdapt*`
  names in HowToLens, HowToGalaxy and autogalaxy_workspace_test (the Stage-3
  release gate). Legs landed as HowToLens#74, HowToGalaxy#71,
  autolens_workspace#496, autogalaxy_workspace#222, autogalaxy_workspace_test#106.

Release attempts: run 47 (scheduled) blocked on readiness RED; run 48 blocked
at Stage 3 (agwt old names; validation otherwise 672p/0f); run 49 passed
everything but blocked STALE — PyAutoGalaxy#581 merged mid-run, the staleness
gate correctly refusing to ship a set that no longer matched main; run 50
(pins incl. #581) released 2026.8.22.1 and PyPI carries all five packages.

## Keep / traps

- The nojax CI leg caught two real bugs on day one: an unmarked
  jax-requiring autolens test (94d8f54ba) and NumPy-scalar misrouting in
  autofit Beta/Gamma/Normal message dispatch (19c679583).
- jax cap stays `<0.11` (widen reverted 848a254; jax 0.11 bug prompt:
  draft/bug/autofit/jax_011_message_log_partition_tuple_shape.md).
- The staleness gate makes manual dispatches race active development: a
  library merge landing between the driver's rehearsal SHA-pin (~15 min in)
  and its readiness re-check (~80 min in) blocks the night. Dispatch when
  merging has quiesced, or expect a re-run.

## Remaining (deliberately not part of this record)

- Make `unittest-nojax` a required check once it has green history (the
  "later" half of the old NEXT list).

## Original prompt

# Make JAX a default (non-optional) dependency across the library stack

Type: maintenance
Target: libraries
Repos:
- PyAutoNerves
- PyAutoFit
- PyAutoArray
- PyAutoGalaxy
- PyAutoLens
- PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

Original request (verbatim):

> is it time to make JAX not an optional but a default dependency of
> autolens? Its easy to install, and performance is crap without it, thoughts?

> Ok good, I think autofit and autogalaxy should also be JAX default at this
> point, I agree that we should retain the full support for numpy only path,
> perhaps we need some sort of explicit test to make sure this path works
> cause most environment tests probably install jax? And yes definitely
> document how mac users can still install via a no jax route, but this is
> now the exception with special pip install options rather than the rule.

## Scope

Promote each library's `[jax]` extra into its **base dependencies**, at every
layer of the chain, so `pip install autolens` (and `autofit`, `autogalaxy`,
`autoarray` standalone) is JAX-enabled by default:

- @PyAutoNerves: move `jax>=0.7`, `jaxlib`, `jaxnnls==1.0.1` from the `jax`
  extra into `dependencies`, widening the cap `<0.11.0` → `<0.12.0`
  (0.11.1 is out; floors-not-pins policy — as a base dep the cap now
  collides with e.g. Colab's preinstalled jax).
  **DECIDED (2026-08-19, human):** declare jax/jaxlib with environment
  markers `; sys_platform != "darwin" or platform_machine == "arm64"` so
  Intel Macs (no jaxlib macosx_x86_64 wheels ≥0.7) resolve cleanly to
  NumPy-only instead of failing at install.
- @PyAutoFit: promote `autonerves` (no longer `[jax]`) + `optax>=0.2.5`.
- @PyAutoArray: promote; drop the `autonerves[jax]` extra indirection.
- @PyAutoGalaxy: promote `autofit` + `jax_zero_contour`.
- @PyAutoLens: promote `autogalaxy`.
- **Keep the `[jax]` extra in every repo as a no-op/alias** (same content as
  base) so existing docs, CI and user muscle memory (`pip install
  autolens[jax]`) keep working — a vanished extra recreates the pip
  history-walk warning trap the extras comments in each pyproject document.

## NumPy-only path stays fully supported

- Do **not** delete or degrade the numpy fallback code paths. The smoke
  profile deliberately runs JAX-disabled and unit tests are no-JAX by policy.
- Add an **explicit no-JAX-installed test leg** in
  @PyAutoHeart `.github/workflows/lib-tests.yml` — the central reusable
  workflow all five library repos' `main.yml` call. Confirmed: today's test
  env installs `[optional]` extras → `[jax]`, so nothing exercises the
  jax-not-installed environment. The leg installs normally, then
  `pip uninstall -y jax jaxlib jaxnnls optax jax_zero_contour`, then runs
  the suite — one extra job on Python 3.13 only (not a full matrix double).
- Add a **one-time loud warning** at import when jax is absent (autonerves
  `jax_wrapper`): NumPy-only mode, performance significantly reduced. The
  numpy path stays supported but never silent (no-silent-guards policy).

## Docs

- Install docs (`PyAutoLens/docs/installation/{pip,conda}.md` and siblings in
  the other repos): JAX-enabled is now the rule; `pip install autolens`
  suffices. Note that Intel Macs automatically fall back to NumPy-only via
  the environment markers (jaxlib publishes no macosx_x86_64 wheels ≥0.7)
  and will see the import-time warning.
- Note the platform coverage that justifies the change: cp312+ CPU wheels
  exist for win_amd64, manylinux x86_64/aarch64, macOS arm64; `jaxnnls` is
  pure Python.

## Watch-outs

- Import-time cost: the jax import chain is ~43% of `import autolens` time
  (see Mind memory / profiling record); making it default makes every import
  pay it. Acceptable, but do not "fix" it here — out of scope.
- Release ordering: extras→base promotion must walk the chain bottom-up
  (autonerves → autofit/autoarray → autogalaxy → autolens) with intra-family
  floors bumped to the first promoted version, mirroring the 2026.7.29.2
  extras-introduction release.
- GPU installs unchanged: CPU jax by default; CUDA remains a manual/extra
  step.
