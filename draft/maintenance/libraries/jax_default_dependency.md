# Make JAX a default (non-optional) dependency across the library stack

Type: maintenance
Target: libraries
Repos:
- PyAutoNerves
- PyAutoFit
- PyAutoArray
- PyAutoGalaxy
- PyAutoLens
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

- @PyAutoNerves: move `jax>=0.7,<0.11`, `jaxlib`, `jaxnnls==1.0.1` from the
  `jax` extra into `dependencies`. Consider widening the `<0.11.0` cap while
  here (0.11.1 is out; floors-not-pins policy) — as a base dep the cap now
  collides with e.g. Colab's preinstalled jax.
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
- Add an **explicit no-JAX-installed test leg**: a CI job (per repo or one
  stack-level job) that installs the library *without* jax present and runs
  the unit test suite (or a representative subset). Rationale: today "JAX
  disabled" testing still has jax importable; nothing exercises the
  jax-not-installed environment, and once jax is a default dep no ordinary
  environment will ever hit it accidentally.

## Docs

- Install docs: JAX-enabled is now the rule. Document the no-JAX route as the
  exception (`pip install autolens --no-deps` is not it — likely a documented
  constraints/`--no-binary`-free path or a `pip install` sequence that skips
  jax), aimed primarily at **Intel Mac** users: jaxlib publishes no
  macosx_x86_64 wheels for the `>=0.7` range, so the default install cannot
  resolve there.
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
