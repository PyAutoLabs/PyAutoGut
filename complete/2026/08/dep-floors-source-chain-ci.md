# dep-floors-source-chain-ci

**Issue:** PyAutoLabs/PyAutoNerves#146 · **Shipped:** 2026-08-03

## What was wrong

Every workspace smoke job died at the **install** step from 18:08Z on
2026-08-03, when the six intra-family dep-floor PRs merged (PyAutoLens#687):

```
ERROR: Cannot install autofit==1.0.dev0 and autonerves 1.0.dev0 ...
    autofit 1.0.dev0 depends on autonerves>=2026.7.29.2
ERROR: ResolutionImpossible
```

## Root cause — not the floors

`setup.py:4` in all six libraries read
`version = os.environ.get("VERSION", "1.0.dev0")`. `1.0.dev0` sorts **below
every date release**, so any source build advertised itself as older than a 2022
wheel. Harmless only while nothing in the family constrained a sibling; fatal the
moment the `>=2026.7.29.2` floors landed.

**The defect was long-latent, not fallout.** `autolens_workspace_test`,
`autogalaxy_workspace_test` and `autocti_workspace_test` each already carried
`pip install --force-reinstall --no-deps ./PyAutoNerves`, commented *"the
`[optional]` re-resolution above can upgrade autonerves to the stale PyPI
release"* — the same bug in its **silent** form, patched per repo. The floors
converted silent into loud, everywhere at once. That is why it read as a cascade
from one dependency change.

Three version mechanisms coexisted, mutually disagreeing:

| Mechanism | Value on main | Read by |
|---|---|---|
| `setup.py` `VERSION` fallback | `1.0.dev0` | pip / resolution |
| `<pkg>/__init__.py` `__version__` (sed-stamped at release) | `2026.7.23.1` | `autonerves.check_version()` |
| `[tool.setuptools_scm]` | inert — `setup.py` passes explicit `version=` | nothing |

## The fix

`setup.py:4` → `os.environ.get("VERSION", "9999.0.0.dev0")` in six libraries.
Sorts above every date release (satisfies present **and future** floors), keeps
`.dev` so nothing claims the checkout is a release, and is invisible to the
workspace handshake (which reads `__version__`, not pip metadata).

Rejected: exporting `VERSION` in `PyAutoHeart/.github/workflows/smoke-tests.yml`,
the original prompt's hypothesis. It is one line, but it fixes **one of five**
source-install surfaces:

| Surface | Before | Fixed by stamp | Fixed by CI `VERSION:` |
|---|---|---|---|
| 10 workspace smoke epilogues | RED | yes | yes |
| `PyAutoHands/.github/workflows/python_matrix.yml` | latent red | yes | no |
| `autocti_assistant/.github/workflows/wiki-currency.yml` | latent red | yes | no |
| `autocti_assistant/skills/ac_setup_environment.md:96` | broken | yes | no |
| `PyAutoHeart/.github/workflows/lib-tests.yml` | green, silently installing **PyPI** autonerves over source | yes | no |

## PRs (13, all merged 2026-08-03)

- **Stamp:** PyAutoNerves#147, PyAutoFit#1447, PyAutoArray#433, PyAutoGalaxy#548, PyAutoLens#689, PyAutoCTI#105
- **Companions:** PyAutoHands#222 (refuse to build on empty `VERSION`), PyAutoHeart#135 (check-B example version)
- **Unblocked and merged behind it:** autofit_workspace#130, HowToFit#42, autolens_workspace#460, HowToLens#65, autolens_workspace#461
- **Closed unmerged:** autolens_workspace_test#246 — the pre-merge verification rig

## Evidence

Local control → treatment before pushing: `pip install ./PyAutoNerves ./PyAutoFit`
on main reproduced the exact `ResolutionImpossible`; the same command against the
branches with **no `VERSION` set** resolved, every package from source at
`9999.0.0.dev0`, no family wheels from PyPI. Confirmed on the autolens (5) and
autocti (4) chains.

Pre-merge CI, autolens_workspace_test#246 run 30851790560, both legs green, with
the provenance assertion printing `9999.0.0.dev0` for all five packages.

**The decisive result** — autofit_workspace#130, three attempts on the *same
commit*, nothing in the PR ever changing:

| attempt | time | result |
|---|---|---|
| 1 | 17:30Z | success — pre-floors |
| 2 | 20:07Z | `ResolutionImpossible` — post-floors |
| 3 | 21:3xZ | success — post-stamp-fix |

All five previously-blocked PRs returned green with no change of their own.

## Traps recorded

- **The prompt's proposed provenance assertion was wrong.** It asked to assert
  `autofit.__file__` resolves under the checkout. Smoke installs non-editable and
  sets `PYTHONPATH` only to `PyAutoHands/autohands`, so every family import
  resolves under `site-packages` either way — the check would pass whether the
  package came from source or PyPI. The discriminator is the **version**.
- **`gh --json` field mismatches fail silently in effect.** Three times this
  session (`jobs` on `run view`, `state` on `pr checks`, `headRefOid` on
  `pr view`) a nonexistent field made a command error into a retry branch: a
  monitor polled forever without emitting, a checks query reported "no checks" on
  passing PRs, and a re-run dispatch sent an empty `head_sha` filter and re-ran
  whichever run was newest — including one unrelated `main` run. Validate the
  field list before arming anything that polls.
- **`worktree_check_conflict` was wrong in both directions again.** It flagged
  four conflicts (PyAutoFit ×2, PyAutoLens, PyAutoHeart), all stale — those repos
  had no open PRs and Heart#132 merged 2026-07-31 — while missing a live local
  branch in a worktree.
- **Brain `bug` sized this `too-large (28)` → split.** Overridden: 11 repos
  contributed +20 and the change is one line per library.

## Follow-ups (not done here)

- Retire the three `--force-reinstall --no-deps ./PyAutoNerves` workarounds and
  their now-wrong comments (they blame `setuptools_scm`, which produces nothing).
- Decide the fate of the inert `[tool.setuptools_scm]` blocks.
- Manually dispatch `PyAutoHands` Python Version Matrix and `autocti_assistant`
  wiki-currency to confirm they recovered — both check out libraries at their
  default branch, so neither could be proven pre-merge.
- The four `pending-release` workspace PRs were merged ahead of their gate on
  explicit human instruction; workspace `main` now calls library API that is on
  library `main` but not yet on PyPI.

## Original prompt

# Intra-family dep floors break every workspace's source-chain smoke CI

Type: bug
Target: health_fixes
Repos:
- autolens_workspace
- HowToLens
- autogalaxy_workspace
- autofit_workspace
- autolens_workspace_test
- autogalaxy_workspace_test
- autofit_workspace_test
- autocti_workspace_test
- HowToFit
- HowToGalaxy
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: URGENT — main is broken
Status: formalised

## The break

The six `intra-family-dep-floors` PRs (PyAutoLens#687) merged in a 15-second
burst on 2026-08-03:

| PR | merged |
|---|---|
| PyAutoArray#432 | 18:08:00Z |
| PyAutoFit#1446 | 18:08:03Z |
| PyAutoGalaxy#547 | 18:08:06Z |
| PyAutoLens#688 | 18:08:09Z |
| PyAutoCTI#104 | 18:08:12Z |
| PyAutoHeart#133 | 18:08:15Z |

Every workspace smoke job has failed at the **install** step since. Smoke never
runs — the job dies before it. Observed on autolens_workspace#460 and
HowToLens#65 at 18:20Z:

```
ERROR: Cannot install autofit==1.0.dev0 and autonerves 1.0.dev0
       (from /home/runner/work/.../PyAutoNerves)
       because these package versions have conflicting dependencies.

The conflict is caused by:
    The user requested autonerves 1.0.dev0 (from .../PyAutoNerves)
    autofit 1.0.dev0 depends on autonerves>=2026.7.29.2

ERROR: ResolutionImpossible
```

Proof it is the floors and not the workspace PRs: autolens_workspace#459 and
#453 both show **green** smoke — their runs are timestamped BEFORE 18:08. Re-run
either and it should go red. Confirm this before doing anything else (control
test).

## Mechanism

`<workspace>/.github/scripts/smoke_install.sh` installs the whole chain from
LOCAL SOURCE in one resolver pass:

```bash
pip install ./PyAutoNerves ./PyAutoFit ./PyAutoArray ./PyAutoGalaxy ./PyAutoLens
```

Each builds via `setup.py`, which reads:

```python
version = os.environ.get("VERSION", "1.0.dev0")
```

CI sets no `VERSION`, so every local package is `1.0.dev0`. PyAutoFit's
pyproject now declares `autonerves>=2026.7.29.2` (line 31, plus
`autonerves[jax]>=2026.7.29.2` at line 71). `1.0.dev0` cannot satisfy
`>=2026.7.29.2`, and pip has both constraints in one pass → ResolutionImpossible.

## Blast radius — 10 repos carry an affected `smoke_install.sh`

`HowToFit`, `HowToGalaxy`, `HowToLens`, `autocti_workspace_test`,
`autofit_workspace`, `autofit_workspace_test`, `autogalaxy_workspace`,
`autogalaxy_workspace_test`, `autolens_workspace`, `autolens_workspace_test`.

The shared runner is `PyAutoHeart/.github/workflows/smoke-tests.yml`
(step "Install (base + the workspace's own epilogue)", line 120), which calls
each workspace's epilogue. So the fix may belong in the shared workflow rather
than in 10 copies — check before fanning out.

## Do NOT loosen or revert the floors

They fixed a real Heart RED (`install verification FAILED (testpypi; checks D)`)
with a proven control test: without floors pip backtracks to autofit
2026.4.30.582 and raises `AttributeError: module 'autofit' has no attribute
'Latent'`. The floors are correct for PUBLISHED wheels. The gap is that they
were verified against built wheels + `--find-links` + published versions, which
never exercised the local-source `1.0.dev0` install path that CI uses.

Note #687's own `do-not` warned that a floor "makes a local 1.0.dev0 wheel build
unsatisfiable" — but scoped that to SELF-referential extras. This is a
CROSS-package floor hitting local source installs; the same failure mode, a case
the task did not anticipate.

## Fix hypothesis — VERIFY IT, do not just apply it

Export a `VERSION` at or above the floor for the source installs, so local
builds satisfy the cross-package floors:

```bash
VERSION=2026.7.29.2 pip install ./PyAutoNerves ./PyAutoFit ./PyAutoArray ...
```

Open questions the investigation must settle:

1. Does one `VERSION` for the whole chain work, or does each package need
   stamping separately? They are built in one pip invocation.
2. Pick the value deliberately. Exactly `2026.7.29.2` satisfies the floors but
   is a lie about what the code is. A high sentinel (`9999.1.1`) is honestly
   "not a release" but could mask a genuine floor violation later. Decide and
   record why.
3. `VERSION` also stamps `*.egg-info` in the checkout — #687 hit this locally
   ("restore with `python3 setup.py egg_info`"). Confirm CI's ephemeral
   checkouts make that irrelevant.
4. Does `pip install --no-deps` for the local chain plus a separate third-party
   pass work better? It sidesteps the resolver entirely but risks dropping real
   transitive deps — measure, don't assume.

## Verification required

- Reproduce RED first on an unchanged workspace branch (control test). A fix
  "verified" without first seeing the failure proves nothing.
- Green smoke on BOTH matrix legs (3.12 AND 3.13) — the epilogue branches on
  `PYTHON_VERSION` and the legs install different extras.
- Confirm the installed chain is the LOCAL source, not PyPI wheels: assert
  `autofit.__file__` resolves under the checkout. A fix that silently switches
  CI to released wheels would go green while destroying what smoke tests.
- Re-run smoke on autolens_workspace#459 and #453 and confirm they return green.

## Blocked on this

- autolens_workspace#460 + HowToLens#65 (`missing-auto-simulate-guards`, #455) —
  both red solely from this; their scripts are verified green locally under real
  smoke envs. Merge once CI is fixed.
- Any workspace PR opened after 18:08Z on 2026-08-03.
- autolens_workspace#461 (`point_source/start_here` composes `PointSolved`) —
  release-validation corrective, red solely from this.
- autofit_workspace#130 + HowToFit#42 (`simulator-util-to-af-ex`,
  PyAutoFit#1444) — these DISPLAY green, but their CI ran at 17:30Z, before the
  18:08Z floor merges. Latent-red, see the control test below.
- PyAutoHeart release-integrate run 30842349506 and the whole release drive.

---

# ADDENDUM (session e0105850, 2026-08-03 ~20:10Z) — control test DONE, scope NARROWED

## 1. Control test: CONFIRMED, on a subject this prompt did not know about

The prompt asks to re-run #459/#453. I used a stronger subject —
**autofit_workspace#130**, whose smoke run 30837040345 passed at **17:30Z**,
before the floors. Re-ran the **identical commit** (attempt 2, 20:07Z):

- attempt 1 (17:30Z, pre-floors): **success**
- attempt 2 (20:07Z, same commit, post-floors): **failure**, and for the right
  reason — `ERROR: Cannot install autofit==1.0.dev0 and autonerves 1.0.dev0 ...
  autofit 1.0.dev0 depends on autonerves>=2026.7.29.2 ... ResolutionImpossible`

Nothing about the PR changed; only the libraries underneath it did. The
diagnosis is proven, not asserted. **You do not need to repeat this** — but
#459/#453/#42 remain available as further subjects if you want them.

## 2. Scope is ONE FILE, not 10 repos — settles open question 4

The prompt says "the fix may belong in the shared workflow rather than in 10
copies — check before fanning out." Checked:

- The 10 `smoke_install.sh` files are **all different** — distinct md5s, 2–7
  `pip install` lines each, different chains (HowToFit installs 2 packages,
  autofit_workspace 7). They CANNOT be fixed by editing one shared file.
- **But `VERSION` is an environment variable, not an install command.** All five
  libraries' `setup.py` read `os.environ.get("VERSION", "1.0.dev0")` (verified in
  all five), and `PyAutoHeart/.github/workflows/smoke-tests.yml` already has an
  `env:` block on the exact step that runs
  `bash workspace/.github/scripts/smoke_install.sh` (it sets `PYTHON_VERSION`
  there today). Adding `VERSION:` beside it propagates to all 10 epilogues
  unchanged.

So **`VERSION` = one line in one shared file; `--no-deps` = editing all 10
differing scripts** AND risking dropped transitive deps. That is a substantive
argument for `VERSION` over `--no-deps`, not just convenience. Question 4 should
be settled on this basis unless you find something that overrides it.

## 3. Question 2 (which VERSION value) — a suggestion, still yours to settle

`2026.7.29.2` asserts the local checkout IS a released version, and would
silently satisfy any FUTURE floor regardless of what the source contains — the
masking risk, permanently. A sentinel (`9999.1.1`) is honest ("not a release")
but has the same masking risk in the other direction.

Suggestion: take the sentinel AND rely on the provenance assertion this prompt
already mandates (`autofit.__file__` resolves under the checkout) to catch
masking, rather than trying to encode that safety in the version string. Decide
with evidence; record the reasoning either way.

## 4. Do NOT touch PyAutoHeart#134 — independent, green, and load-bearing

Separate bug, already fixed and open: `verify_install` Check D pins only
`autolens`, and pip refuses pre-releases for DEPENDENCIES without `--pre`, so
every rehearsal resolved the family from stable PyPI and validated
already-published, floor-less metadata instead of the candidate build.

Control test on **python3.13** (3.12 is unaffected and MASKS it) installing
`autolens[optional]==2026.8.3.1.dev70001`:

| | autofit | autogalaxy | autoconf | import |
|---|---|---|---|---|
| without `--pre` | 2026.4.30.582 | 2026.8.2.1 | 2026.7.15.1 | FAIL `no attribute 'Latent'` |
| with `--pre` | dev70001 | dev70001 | none | OK |

This is independent proof that **the floors are load-bearing on the published
path** — reinforcing this prompt's "do NOT revert the floors". #134 is green
(pytest 3.12 + 3.13). Do not revert it as collateral.

## 5. Interpreter trap — verify on BOTH 3.12 and 3.13

In the Check D investigation, 3.12 silently passed where 3.13 failed, and a
first control test run only on 3.12 was worthless. This prompt already requires
both matrix legs; treat that as load-bearing, not box-ticking.

## 6. Brain sizing

`pyauto-brain bug` returned `too-large (score 27) → split`. 11 repos alone
contribute +20. Given finding 2 (one line, one file), that split is not
warranted — override it and record the override, per the established pattern.

---

# ADDENDUM 2 (session fea70a51, 2026-08-03) — the fix locus MOVES to the libraries

Re-run of `pyauto-brain bug` scored `too-large (28)`; overridden again, on the
same basis.

## The prompt's fix hypothesis is treating a symptom

Both the prompt and addendum 1 assume the fix is to inject `VERSION` at the CI
call site. **Do not do that.** The defect is not in CI — it is the *default* the
libraries stamp on a source build:

```python
version = os.environ.get("VERSION", "1.0.dev0")   # setup.py:4, all six libraries
```

`1.0.dev0` sorts **below every real release**. A source checkout therefore
advertises itself as older than a 2022 wheel. The floors are the first constraint
that ever looked.

## This is a long-latent defect, not fallout from the floors

`autolens_workspace_test`, `autogalaxy_workspace_test` and `autocti_workspace_test`
each already carry a hand-rolled workaround for it —
`pip install --force-reinstall --no-deps ./PyAutoNerves` — commented *"The
`[optional]` re-resolution above can upgrade autonerves to the stale PyPI release
(… the local copy as 1.0.dev0 …)"*. Same bug, silently swapping a PyPI wheel over
the source checkout, patched per-repo. (The comment blames `setuptools_scm`, which
is not what produces the value.) The floors converted a **silent** misinstall into
a **loud** one everywhere at once — which is why it reads as a cascade.

## Three version mechanisms, mutually disagreeing

| Mechanism | Value on `main` | Read by |
|---|---|---|
| `setup.py` `VERSION` fallback | `1.0.dev0` | pip / resolution |
| `<pkg>/__init__.py` `__version__` (sed-stamped at release) | `2026.7.23.1` | `autonerves.check_version()` |
| `[tool.setuptools_scm]` | inert (`setup.py` passes explicit `version=`) | nothing |

**This corrects addendum 1, section 3.** The workspace handshake reads
`__version__`, *not* pip metadata — so the choice of `VERSION` value has no
handshake or staleness-warning consequence. That whole trade-off was a phantom.

## The fix: `setup.py:4` → `"9999.0.0.dev0"`, six libraries

Sorts above every date release (satisfies present *and* future floors); keeps
`.dev` so nothing claims the checkout is a release; invisible to the handshake.

Blast radius the CI-side patch would have missed — all fixed by the stamp,
none by a `VERSION:` line in `smoke-tests.yml`:

- `PyAutoHands/.github/workflows/python_matrix.yml` (one-pass `-e` install) — latent red
- `autocti_assistant/.github/workflows/wiki-currency.yml` — latent red
- `autocti_assistant/skills/ac_setup_environment.md:96` — documented setup, broken
- `PyAutoHeart/.github/workflows/lib-tests.yml` — green, but its per-repo install
  loop now silently pulls **PyPI** `autonerves 2026.7.29.2` over the source one
- any future source-install site

Verified locally: `pip install ./PyAutoNerves ./PyAutoFit` reproduces the exact
`ResolutionImpossible`; the same command under `VERSION=9999.0.0.dev0` resolves
and installs both from source with no family wheels from PyPI; `pip install
./PyAutoFit` alone pulls `autonerves-2026.7.29.2` from PyPI, confirming the
shadowing row.

Companions in the same branch set: a `VERSION` unset/empty guard in
`PyAutoHands/.github/workflows/release.yml` before `python3 -m build` (the
fallback is unreachable there today, but 9999 escaping to PyPI would be a bad
day), and the check-B example version in
`PyAutoHeart/skills/verify_install/verify_install.md:41`.

Follow-ups, not this task: retire the three `--force-reinstall --no-deps`
workarounds and their now-wrong comments; decide the fate of the inert
`[tool.setuptools_scm]` blocks.
