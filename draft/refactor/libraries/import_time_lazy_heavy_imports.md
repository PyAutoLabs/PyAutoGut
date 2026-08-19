# Slow imports: autolens 4.3s, autogalaxy 3.4s (hygiene perf tier, >3s threshold)

Type: refactor
Target: libraries
Repos:
- @PyAutoLens
- @PyAutoGalaxy
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Finding (2026-07-25 hygiene perf tier)

Cold-import timings (subprocess, Python 3.11 venv, editable installs):
autofit 1.39s, autoarray 1.75s, **autogalaxy 3.41s**, **autolens 4.27s** —
the last two exceed the hygiene slow threshold (3.0s). Every workspace
script, test run and smoke entry pays this on startup, so it compounds
across the dev loop and CI.

## Task

Profile the import graphs (`python -X importtime -c "import autolens"`),
identify the heavy eager imports (matplotlib? scipy submodules? profile
registries built at import?), and defer what can be deferred (lazy submodule
imports, function-local imports for heavyweight optional paths) without
changing the public `al.*` / `ag.*` surface. The JAX rule already bans
module-level jax imports — check nothing regressed there too.

## Acceptance

- `import autolens` cold under ~2.5s on the same box (stretch: match
  autoarray's ~1.75s overhead + delta), autogalaxy proportionally.
- No public API change; full test suites green; workspace smoke green.
