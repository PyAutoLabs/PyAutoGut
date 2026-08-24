# `autoreduce` on PyPI belongs to another project — PyAutoReduce cannot publish under it

Type: bug
Target: pyautoreduce
Repos:
- PyAutoReduce
- autoreduce_workspace
Difficulty: small
Autonomy: supervised
Priority: high
Status: issued
Issue: https://github.com/PyAutoLabs/PyAutoReduce/issues/71
Filed: 2026-08-19 (backfilled from git)
Reframed: 2026-08-24 (original premise disproved — see "What the survey found")

## What the survey found

This prompt was filed as "the published `autoreduce 0.9` never got the Python
3.12 floor". That premise is wrong, and the truth is worse.

`autoreduce` on PyPI is **not a PyAutoLabs package**:

```
name        = autoreduce
version     = 0.9  (uploaded 2026-08-12)
summary     = Python tools for automated model reduction of nonlinear dynamical systems
author      = Ayush Pandey <ayushpandey@ucmerced.edu>
source      = https://github.com/ayush9pandey/AutoReduce
requires-python = >=3.9,<=3.14.7
```

Its release history runs 0.1.0 (2020-10-15) through 0.9 — a lineage with no
connection to this repository. Corroborating evidence that PyAutoLabs has never
published it:

- `git ls-remote --tags PyAutoLabs/PyAutoReduce` returns **nothing**. The repo
  has never been tagged, and its build is `setuptools-scm` + `dynamic =
  ["version"]`, so an untagged tree cannot produce a `0.9`.
- PyAutoHands contains **zero** references to `autoreduce`: not in
  `release.yml`'s project matrix, not in `pre_build.sh`'s `WORKSPACE_SPECS`.
- PyAutoReduce has no release workflow of its own — `.github/workflows/main.yml`
  is the Heart `lib-tests.yml` caller and nothing else.

So there is no floor gap, no build path assembling metadata independently of
`pyproject.toml`, and the `<=3.14.7` cap is a third party's — nothing for us to
justify or remove. `requires-python = ">=3.12"` from `d7bd916a` is in
`pyproject.toml` and is correct.

## The actual defect

`pyproject.toml` declares `name = "autoreduce"` — a distribution name owned by
someone else — and the docs instruct users to install it:

- `README.md:41-43` — `pip install autoreduce`, `"autoreduce[hst]"`,
  `"autoreduce[psf]"`
- `autoreduce_workspace/README.md:47` — `pip install autoreduce`

Those commands install a foreign package today. The `[hst]`/`[psf]` extras do
not exist there, so pip emits a warning about unknown extras and installs it
anyway. A user following our own README ends up with a nonlinear-dynamics model
reducer and an `import autoreduce` that resolves to it.

There is a second-order consequence in the provenance record.
`autoreduce/__init__.py:16` resolves `__version__` via
`importlib.metadata.version("autoreduce")`, and `package/provenance.py` writes
that into every `reduction.json`. On a machine with the foreign package
installed, our provenance would record *its* version as ours.

Induction into the PyAutoHands release machinery is blocked until the name is
ours: a `twine upload` under `autoreduce` would be rejected.

## Decision taken (2026-08-24)

Publish as **`pyautoreduce`** (free on PyPI); the **import package stays
`autoreduce`**. It matches the repo name and the org prefix, and the repo is
already half-using it — `docs/design/hst_acs_pipeline.md:253`,
`psf/starred_epsf.py`, `target.py` and `scripts/reduce_cosmos_web_ring.py` all
write `pyautoreduce[starred]` already. This change resolves that drift in the
direction the repo was already leaning, with no source renaming.

Rejected: renaming the import package too (dist==import parity is cosmetic and
costs a rename across this repo plus `autoreduce_workspace`); `autoreduce-hst`
(diverges from repo name and family prefix); pursuing the `autoreduce` name
itself (the owner shipped 0.9 on 2026-08-12, so it is actively maintained and
PyPI will not transfer it).

## Scope

In @PyAutoReduce:

- `pyproject.toml:6` — `name = "autoreduce"` → `name = "pyautoreduce"`, with a
  comment recording *why* (the name is taken by an unrelated, actively
  maintained project) so nobody "tidies" it back.
- `autoreduce/__init__.py:16` — `_version("autoreduce")` →
  `_version("pyautoreduce")`. Without this the dist rename silently degrades
  `__version__` to the `PackageNotFoundError` fallback `"0.0.dev0"`, or worse
  picks up the foreign package's version.
- `autoreduce/package/cosmic_rays.py:53` — `pip install autoreduce[frames]` →
  `pyautoreduce[frames]`.
- `autoreduce/psf/stpsf_model.py:51` — `pip install autoreduce[psf]` →
  `pyautoreduce[psf]`.
- `README.md:41-43` — the three install lines.
- `docs/design/hst_acs_pipeline.md:479` — `autoreduce[frames]` →
  `pyautoreduce[frames]` (line 253 is already correct).

In @autoreduce_workspace (companion PR, behind the library):

- `README.md:47` — `pip install autoreduce` → `pip install pyautoreduce`.

**Do not change** `autoreduce/package/provenance.py:16`. Its tuple is fed to
`__import__(package).__version__` — those are *import* names, and the import
package is deliberately unchanged. Renaming that entry would break provenance.

**Do not change** `.github/workflows/main.yml`'s `package: autoreduce` input.
Heart's `lib-tests.yml` uses it as the import package (`pytest --cov
${{ inputs.package }}`) and as a repo-mapping key, not as a distribution name.

## Out of scope (filed separately)

Induction into the PyAutoHands release machinery and the family's date-based
versioning — `draft/release/pyautoreduce/pyautoreduce_release_induction.md`.
That is what actually gets a `pyautoreduce` artifact onto PyPI; this task only
makes the name claimable and stops the docs pointing at a stranger's package.

## Done when

- `pyproject.toml` declares a distribution name PyAutoLabs can publish under.
- No document or error message in either repo tells a user to install
  `autoreduce`.
- `__version__` and the `reduction.json` provenance resolve against the new
  distribution name rather than the foreign one.
- The reason for the name is written down where the next reader will find it.
