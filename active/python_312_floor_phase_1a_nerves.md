# Python 3.12 floor — Phase 1A: PyAutoNerves

Type: feature
Target: PyAutoNerves
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Parent: `python_312_floor_phase_1_core.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

In @PyAutoNerves on `feature/python-312-floor`:

- Set `requires-python = ">=3.12"` and keep only 3.12/3.13 classifiers.
- Remove the now-tautological Python markers from jax, jaxlib, and jaxnnls;
  preserve the JAX `<0.11` cap and all other behavior-driven constraints.
- Keep the import-time version warning and `version.python_version_check`
  bypass, but simplify it for the new floor and make Python 3.14's unsupported,
  experimental status explicit. Remove the unreachable pre-3.11 JAX note.
- Preserve the containing `version:` block and `minimum_library_version`.
- Update warning tests and the `AGENTS.md` floor contract.

## Gates

- Required PyAutoNerves suite passes on Python 3.12 and 3.13.
- Built metadata reports `Requires-Python: >=3.12` and the expected unmarked JAX
  requirements without loosening caps.
- Simulated/current 3.12 and 3.13 emit no warning; simulated/current 3.14 emits
  the experimental warning and remains bypassable.

## Out of scope

JAX 0.11, Python 3.14 support, downstream package manifests, Hands/Heart
matrices, workspaces, release execution, and archival documentation.
