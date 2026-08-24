PyAutoReduce no longer claims a PyPI distribution name owned by someone else,
and no document in either repo tells a user to install it. The distribution is
`pyautoreduce`; the import package stays `autoreduce`.

- issue: https://github.com/PyAutoLabs/PyAutoReduce/issues/71 (closed 2026-08-24)
- prs: PyAutoReduce#72 (merged `94a27f3`, head `31b1294`),
  autoreduce_workspace#1 (merged `a2386ba`, head `9546b47`, behind the
  library-first gate)
- CI: PyAutoReduce `unittest` 3.12 + 3.13 green (run 32782915519;
  `unittest-nojax` skipped by design — Heart's `lib-tests.yml` gates it on
  `package != 'autoreduce'`); autoreduce_workspace `workspace_smoke` 3.12 +
  3.13 green (run 32783038199). The workspace smoke clones the *matching*
  PyAutoReduce branch, so the pair was exercised together, not each half alone.

## The finding — the filed premise was wrong

Filed as "published `autoreduce 0.9` never got the Python 3.12 floor". It never
did, because **we never published it**. `autoreduce` on PyPI is
github.com/ayush9pandey/AutoReduce — "Python tools for automated model reduction
of nonlinear dynamical systems", author Ayush Pandey, releases 0.1.0 (2020-10-15)
through 0.9 (2026-08-12). Three independent confirmations:

- `git ls-remote --tags PyAutoLabs/PyAutoReduce` returns nothing, and the build
  is setuptools-scm + `dynamic = ["version"]` — an untagged tree cannot produce
  a `0.9`.
- PyAutoHands has zero references to `autoreduce`: not in `release.yml`'s
  matrices, not in `pre_build.sh`'s `WORKSPACE_SPECS`.
- PyAutoReduce has no release workflow of its own.

So there was no floor gap and no build path assembling metadata independently of
`pyproject.toml`; the `<=3.14.7` cap was the other project's.
`requires-python = ">=3.12"` from `d7bd916a` had been correct since 2026-07-30.

**The durable lesson: verify that a PyPI project is yours before reasoning about
its metadata.** A stale-looking `Requires-Python` on a package you assume is
yours is at least as likely to mean the package is not yours. The cheap check is
`curl -sS https://pypi.org/pypi/<name>/json` and read `author_email` /
`project_urls` — the 2020 first-release date on a 2026 repo was the tell.

## The actual defect

`pyproject.toml` declared `name = "autoreduce"` — unpublishable, since a
`twine upload` under it would 403 — while `README.md` and
`autoreduce_workspace/README.md` told users to `pip install autoreduce`. The
`[hst]`/`[psf]` extras do not exist on the foreign project, so pip warns about
unknown extras and installs it anyway.

Second-order: `autoreduce/__init__.py` resolved `__version__` via
`importlib.metadata.version("autoreduce")`, and `package/provenance.py` writes
that into every `reduction.json`. With the foreign package installed, our
provenance would have recorded *its* version as ours.

## Traps worth remembering

- **Distribution name != import name.** `provenance.py`'s tuple is fed to
  `__import__(package).__version__` — import names, deliberately left as
  `autoreduce`. `.github/workflows/main.yml`'s `package: autoreduce` is likewise
  an import name (Heart's `lib-tests.yml` uses it for `pytest --cov` and as a
  repo-mapping key). Renaming either would have broken something.
- **The `__init__.py` edit was load-bearing, not cosmetic.** Verified in the
  venv: after the rename `version("autoreduce")` raises `PackageNotFoundError`,
  so leaving it would have silently degraded `__version__` to the `"0.0.dev0"`
  fallback and written that into every provenance record.
- **The workspace was worse than first scoped.** One README line was planned; a
  repo-wide sweep for `autoreduce[` — the unambiguous distribution-name marker —
  found eight files. `requirements.txt`'s first line was a literal
  `autoreduce[hst]` install spec, i.e. actually broken, not merely misleading.
- **The repo was already half-using the new name.** `target.py`,
  `psf/starred_epsf.py`, `scripts/reduce_cosmos_web_ring.py` and
  `docs/design/hst_acs_pipeline.md:253` wrote `pyautoreduce[starred]` before this
  task. The rename resolved existing drift rather than creating any.

## Rejected, with reasons

- **Rename the import package too** (dist == import, as elsewhere in the family):
  parity is cosmetic, and it costs a rename across this repo plus
  `autoreduce_workspace`.
- **`autoreduce-hst`**: also free, but diverges from both the repo name and the
  family prefix.
- **Pursue the `autoreduce` name itself**: the owner shipped 0.9 on 2026-08-12,
  so it is actively maintained and PyPI will not transfer it. Would have blocked
  the induction indefinitely.

## Environment note

Run in a web-github session: no local worktree, no `gh`. Clones at
`/home/user/pyautoreduce` and `/home/user/autoreduce_workspace`; GitHub via the
MCP tools. Verification used `uv venv --python 3.12` because the session's own
Python is 3.11 — below the repo's own floor.

## Follow-up

`draft/release/pyautoreduce/pyautoreduce_release_induction.md` — induction into
the PyAutoHands release machinery, unblocked by this merge. Its three questions
were answered by the human on 2026-08-24: nightly cadence with the other
projects; the family's date scheme with no `0.x` line first; an account-scoped
PyPI token from the `Jammy2211` account under the PyAutoLabs org for the first
publish, narrowed to a project-scoped token afterwards. Two consequences recorded
there: nightly is activity-gated over a repo list, so PyAutoReduce must join that
list in PyAutoBrain's `nightly-release.yml` as well as `release.yml`'s matrices;
and `YYYY.MM.DD.1` and the family's `2026.8.24.1` are the same thing on PyPI
(`release.yml` computes `date +"%Y.%-m.%-d"`, and PEP 440 integer normalization
drops leading zeros anyway), so no padded variant should be added for this repo.

Also noticed, not fixed, worth its own hygiene task: the built wheel's
`top_level.txt` lists `docs` and `scripts` alongside `autoreduce` —
`[tool.setuptools.packages.find]`'s exclusions are not taking effect. Pre-existing
and unrelated to this diff.

## Original prompt

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
