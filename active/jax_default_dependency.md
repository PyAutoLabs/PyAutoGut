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
