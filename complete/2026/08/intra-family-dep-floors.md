# Intra-family dependency floors — `autolens[optional]` resolved an ancient autofit

Issue: PyAutoLabs/PyAutoLens#687 (CLOSED 2026-08-04 — see "What was still outstanding")

## What was wrong

`pip install "autolens[optional]"` installed **`autofit 2026.4.30.582`** — an
April release — alongside a current autoarray/autogalaxy/autonerves. The install
succeeded; `import autolens` then raised
`AttributeError: module 'autofit' has no attribute 'Latent'`. This was Heart's
RED leg `install verification FAILED (testpypi; checks D)` (PyAutoHeart run
30788224561, job 91606144514; sidecar 2026-08-03T06:01:09Z).

**Root cause.** Every intra-family dependency was a **bare package name with no
version floor**. Backtracking the `[optional] → [jax] → autofit[jax] →
autonerves[jax]` extras chain, pip may walk the release history back to 2022 —
and *"version X does not provide the extra 'jax'"* is a pip **warning, not an
error**, so a pre-extras release is a legal solution and pip settles there
(~22,600 log lines of backtracking).

**Why it stayed hidden.** Check D builds its venv with the default `python3`.
The release job's `setup-python` steps run 3.11 → 3.12 → 3.13 and the last one
wins, so CI resolves `python3` to **3.13** while a dev laptop resolves **3.12**.
On 3.12 pip stops at a release that still has `af.Latent` and the check PASSES.
Reproducing "the failing check" locally therefore looked like CI flake.

## What shipped (all merged 2026-08-03)

| Repo | PR | Change |
|---|---|---|
| PyAutoArray | #432 | `autonerves` → `>=2026.7.29.2` (base + `[jax]`) |
| PyAutoFit | #1446 | `autonerves` → `>=2026.7.29.2` (base + `[jax]`) |
| PyAutoGalaxy | #547 | `autofit`, `autoarray` → `>=2026.7.29.2`; `autofit[jax]>=2026.7.29.2` |
| PyAutoLens | #688 | `autogalaxy` → `>=2026.7.29.2`; `autogalaxy[jax]>=2026.7.29.2` |
| PyAutoCTI | #104 | `autofit`, `autoarray` → `>=2026.7.29.2` |
| PyAutoHeart | #133 | Check D names its interpreter in the sidecar detail |

PyAutoNerves inspected — **no change**, it carries only self-references.

Floors, not exact pins (the PyAutoBuild#118/#120 design). `2026.7.29.2` is live
on PyPI, unyanked, and the oldest release still carrying `af.Latent`.
**Self-referential** extras (`autolens[jax]` inside `autolens[optional]`, and
siblings) deliberately left bare — a self-reference is already version-locked.

## Proof

The discriminating test: family wheels built from the branch, autolens pinned to
the published (unfloored) dev wheel, siblings supplied via `--find-links`,
python3.13, clean `env -u PYTHONPATH` venv, TestPyPI + PyPI. Identical inputs,
sibling metadata the only variable:

| arm | sibling metadata | resolved autofit | `import autolens` |
|---|---|---|---|
| control | bare (pre-merge `main`) | `2026.4.30.582` | `AttributeError` |
| fixed | floored | `2026.8.4.1` | OK |

This is what established the floors bite **transitively**, from sibling
metadata, not merely as top-level pins.

## Traps worth remembering

1. **Ad-hoc venvs inherit the dev `PYTHONPATH`.** The profile exports the five
   source checkouts, so a hand-rolled venv reports `Requirement already
   satisfied` for every PyAuto package and `import autolens` loads the SOURCE
   tree rather than the installed wheel. The first verification pass was
   contaminated and **falsely confirmed the fix**. `verify_install.sh` is safe
   (it `unset PYTHONPATH`s, line 47); ad-hoc reproductions are not.
2. **`pip install --dry-run`'s `Would install` line omits `--find-links`
   wheels**, so it cannot be used to read a resolution. Reading it produced a
   wrong "the fix doesn't work" conclusion mid-session. Do a real install and
   `pip list`.
3. **`python -m build` stamps `*.egg-info` into the source checkout** (version
   from `$VERSION`, `setup.py` default `1.0.dev0`), leaving a fabricated version
   visible to the whole dev env through that same PYTHONPATH. Restored here with
   `env -u VERSION python3 setup.py egg_info`.

## Retracted claim

The issue body flagged a "known trade-off" — that floors would break
`verify_install B --version 1.0.dev0 --find-links dist/`. **That was wrong** and
was retracted on the issue: pip already prefers the higher released sibling
(`2026.7.29.2` > `1.0.dev0`) over a local dev wheel, floors or no floors, since
only `autolens` is pinned by that invocation.

## What was still outstanding — DISCHARGED 2026-08-04, #687 CLOSED

The floors take effect **only once the libraries are republished carrying
them**. The RED `verify_install` leg does not clear until a release republishes
and Check D re-runs against those wheels, so issue #687 was deliberately left
OPEN until that happened.

It happened on **2026-08-04**: release `2026.8.4.1` published to PyPI at
`11:43:29Z` (unyanked). Three proofs, in ascending strength:

1. **Published metadata carries the floors** — `autolens` requires
   `autogalaxy>=2026.7.29.2`; `autogalaxy` requires `autofit>=2026.7.29.2` +
   `autoarray>=2026.7.29.2`; `autofit` and `autoarray` require
   `autonerves>=2026.7.29.2`; the `[jax]` variants likewise.
2. **Check D green in CI** — `integrate / verify_install_release` SUCCESS in
   PyAutoHeart Release Integrate `30901054267` (2026-08-04T10:32), a run green
   end-to-end (51 success / 2 skipped / 0 failure).
3. **Control test re-run on python3.13** — the interpreter that originally
   reproduced it (§"Why it stayed hidden": 3.13 fails, 3.12 passes). Fresh venv,
   `PYTHONPATH` unset: `pip install "autolens[optional]"` rc=0, `import autolens`
   rc=0, resolved `autofit 2026.8.4.1`, `af.Latent` present. The original
   `pip rc=0 import rc=1` on `autofit 2026.4.30.582` no longer reproduces.

Closed with this evidence: PyAutoLens#687 (comment `5184044932`).

**Residual, not tracked anywhere else yet:** `autocti` on PyPI is still
`2024.11.13.2`, its metadata carrying the pre-fix **exact pins**
`autofit==2024.11.13.2` / `autoarray==2024.11.13.2`. PyAutoCTI#104 put the floors
in source, but that package was not republished on this release cadence, so the
fix is not live for `autocti` users. Out of scope for #687 (the `autolens` chain),
but it means "the floors shipped" is true of four packages, not five.

Also unaddressed at the time, from the same readiness snapshot: `PyAutoFit: 1
commit(s) behind origin`, `release validation FAILED (stage integrate)`, and the
workspace smoke YELLOW (19 failed + 1 timeout, PyAutoHeart run 30790463134). The
integrate leg has since cleared — see the green run cited above and
[[nautilus-1core-serial-pool]].

## Original prompt

<details>
<summary>PyAutoMind/draft/bug/health_fixes/intra_family_dependency_floors.md</summary>

# `autolens[optional]` resolves an ancient autofit — intra-family deps have no version floors

Type: bug
Target: health_fixes
Repos:
- @PyAutoNerves
- @PyAutoArray
- @PyAutoFit
- @PyAutoGalaxy
- @PyAutoLens
- @PyAutoCTI
Difficulty: low
Autonomy: supervised
Priority: high
Status: draft

## Finding (2026-08-03, PyAutoHeart readiness RED)

`pyauto-heart verify_install` Check D (`pip install "autolens[optional]"`) FAILED
in the Release Integrate run (PyAutoHeart run 30788224561, job 91606144514),
sidecar `~/.pyauto-heart/verify_install.json` `2026-08-03T06:01:09Z`,
detail `pip rc=0 import rc=1`. It is one of the two legs holding the release RED.

The install succeeds; the import does not:

    [05:58:53] -> import autolens
    Traceback (most recent call last):
        import autolens; print(autolens.__version__)
    AttributeError: module 'autofit' has no attribute 'Latent'

Check D resolved **autofit 2026.4.30.582** (an April release, pulling
`autoconf 2026.7.15.1` with it) while autoarray / autogalaxy / autonerves came
in at `2026.8.2.1`.

### Root cause

`autolens[optional]` expands to
`autolens[jax]` -> `autogalaxy[jax]` -> `autofit[jax]` -> `autonerves[jax]`.

Every intra-family dependency in the five `pyproject.toml` files is a **bare
package name with no version floor** (`"autofit"`, `"autoarray"`,
`"autogalaxy"`, `"autonerves"`). When pip backtracks anywhere in that extras
chain it may walk the entire release history back to 2022 — and pip treats
*"version X does not provide the extra 'jax'"* as a **warning, not an error**,
so an ancient `autofit` carrying no `jax` extra is a legal solution. pip settles
there after ~22,600 lines of backtracking.

The metadata itself did not regress: `requires_dist` for autonerves / autofit /
autogalaxy is identical between `2026.7.29.2` (PyPI) and `2026.8.2.1`
(TestPyPI). The whole `2026.8.2.1` family is TestPyPI-only; PyPI's newest is
still `2026.7.29.2`.

### Why it passed locally and failed in CI

Check D builds its venv with the default `python3`. The `verify_install_release`
job calls `setup-python` for 3.11, then 3.12, then 3.13 — the last wins, so CI's
`python3` is **3.13**. Locally it is 3.12. Reproduced on both, same command,
same index args:

| interpreter | resolved autofit | `import autolens` |
|---|---|---|
| 3.12 | 2026.7.29.2 | passes (still has `Latent`) |
| 3.13 | **2026.4.30.582** | `AttributeError` |

Both are backtracked; 3.12 merely stops at a version that still has `Latent`.
This is a real user-facing defect, not a CI artefact — `pip install
autolens[optional]` from live PyPI today also silently walks the family back.

### Control test — floors fix it

Same command, same python3.13, floors added:

    pip install "autolens[optional]==2026.8.3.1.dev69801" \
        autofit>=2026.7.29.2 autogalaxy>=2026.7.29.2 \
        autoarray>=2026.7.29.2 autonerves>=2026.7.29.2

    -> autoarray 2026.8.2.1  autofit 2026.8.2.1
       autogalaxy 2026.8.2.1  autonerves 2026.8.2.1
    -> import autolens: OK

Without the floors the identical command lands on autofit 2026.4.30.582 and
raises.

## Task

1. Add `>=2026.7.29.2` floors to every intra-family dependency — base
   `dependencies` **and** the `[jax]` / `[optional]` extras — in
   PyAutoNerves, PyAutoArray, PyAutoFit, PyAutoGalaxy, PyAutoLens, and
   PyAutoCTI (`autofit`, `autoarray` are bare there too).
   This is a floor, not an exact pin — consistent with the floors-not-pins
   release design (PyAutoBuild#118/#120). A floor must name an *installable*
   version, so `2026.7.29.2` (live on PyPI, not yanked) is the right value.
2. Make Check D state which interpreter it used in its sidecar `detail`
   (`PyAutoHeart/heart/checks/verify_install.sh`, `check_d`). "Default
   `python3`" silently differing between CI (3.13) and local (3.12) is what hid
   this; the evidence should name the interpreter the way Check B's details do.

## Acceptance

- `pip install "autolens[optional]"` on python3.12 **and** python3.13 resolves
  the whole PyAuto family at the newest available release, and `import autolens`
  succeeds.
- Check D's sidecar detail names the interpreter version.
- Note: the floors only take effect once new wheels are published. The RED
  `verify_install` leg does not clear until a release rehearsal republishes to
  TestPyPI and Check D re-runs against those wheels.

</details>
