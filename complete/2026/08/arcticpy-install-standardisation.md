- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/170
- prs:
  - https://github.com/PyAutoLabs/PyAutoHeart/pull/171 (merged) — the canonical action
  - https://github.com/PyAutoLabs/autocti_workspace_test/pull/18 (merged)
  - https://github.com/PyAutoLabs/autocti_assistant/pull/22 (merged)
  - https://github.com/PyAutoLabs/PyAutoCTI/pull/109 (merged)
  - https://github.com/PyAutoLabs/autocti_workspace/pull/26 (merged)
- summary: |
    One canonical Heart-owned arcticpy install — a composite action at
    `PyAutoHeart/.github/actions/install-arcticpy`, holding the single
    `arcticpy==2.6` pin — consumed by every CTI repo, replacing four divergent
    shell copies. Four documented recipes fixed to match. Verified end-to-end:
    the action builds and clocks charge through arctic on Python 3.12 and 3.13
    in CI, PyAutoCTI's lib-tests are green through it, and autocti_workspace_test
    smoke is green through it.

## Audit correction — the site list in the prompt was wrong

The prompt flagged PyAutoCTI's own lib-tests CI as UNREAD and counted two copies.
Audited: `PyAutoCTI/.github/workflows/main.yml` is a *thin caller* of
`PyAutoHeart/.github/workflows/lib-tests.yml@main` and carries no recipe of its
own — but that reusable workflow carries **two** copies, one per job (`unittest`,
`unittest-nojax`). So there were **four** shell copies, not two:

| # | site | had `setuptools wheel`? |
|---|------|---|
| 1 | `PyAutoHeart/.github/workflows/lib-tests.yml` job `unittest` | yes |
| 2 | `PyAutoHeart/.github/workflows/lib-tests.yml` job `unittest-nojax` | yes |
| 3 | `autocti_workspace_test/.github/scripts/smoke_install.sh` | no |
| 4 | `autocti_assistant/.github/workflows/wiki-currency.yml` | yes |

`autocti_workspace` has no `.github/` at all — docs-only consumer.

## Correction — smoke_install.sh was NOT one runner-image change from breaking

The prompt described it as relying on the runner image's ambient `setuptools`.
It was not: Heart's `smoke-tests.yml` runs `pip install --upgrade pip setuptools
wheel` immediately before invoking the epilogue. The real defect was weaker but
still worth removing — the epilogue's correctness depended implicitly on a step
in a *different repository's* workflow, with nothing on either side stating it.
The canonical step is self-contained, so the coupling is gone rather than
merely documented.

## Two things the specified recipe got wrong (found by building it, not reading it)

1. **`--no-deps` suppresses arcticpy's RUNTIME dependencies too.**
   `arcticpy/read_noise.py` does `from scipy.optimize import curve_fit` and
   `import matplotlib as mpl`, and `__init__.py` imports `read_noise`. Installing
   only the build deps leaves `import arcticpy` raising `ModuleNotFoundError:
   No module named 'scipy'`. The prompt's prose called out matplotlib only.
2. **arcticpy exposes NO `__version__` attribute.** The assertion the prompt
   specified — `import arcticpy; print(arcticpy.__version__)` — raises
   `AttributeError` on a perfectly good install. The same broken command was
   already documented in `autocti_assistant/skills/ac_setup_environment.md`,
   i.e. the assistant would have told a user their healthy arcticpy was broken.
   Use `importlib.metadata.version("arcticpy")`.

Both were caught because the self-test was written and run, not assumed. Two
further API mistakes surfaced the same way: `add_cti` needs an `ac.CCD`, not an
`ac.CCDPhase` (else `AttributeError: fraction_of_traps_per_phase`), and
`parallel_roe` is not optional in practice (else `AttributeError: dwell_times`).

## Verified

- **Negative case reproduced**: with setuptools uninstalled the build dies at
  `BackendUnavailable: Cannot import 'setuptools.build_meta'`. And a fresh
  **Python 3.12 venv ships no setuptools at all** — checked directly — so the
  omission was a real hazard, not a style nit.
- **Canonical recipe builds** on 3.11 and 3.12 locally, 3.12 and 3.13 in CI.
- **arctic actually clocks**: bright pixel 1000.0 -> 997.2389438265325, trail
  [1.18249389, 0.77773508, 0.50869121, 0.33114622, 0.21469258] (decaying),
  charge conserved to 5.8e-4. Byte-identical numbers locally and in CI.
- PyAutoCTI `unittest` (3.12, 3.13) and `unittest-nojax` green through the action.
- autocti_workspace_test `smoke` (3.12, 3.13) green through the action.

## Caching decided with a measurement, not an assumption

The prompt asked for before/after timings rather than an assumed win. GitHub's
per-step timings from the self-test run (32769526194, job `build (3.12)`):

```
Install GSL headers (apt-get)            15.9 s
Build deps (setuptools/wheel/numpy/cython) 9.0 s
Runtime deps (scipy/matplotlib)            9.9 s
Build and install arcticpy 2.6            16.8 s   <- compile is ~14 s of this
Verify import                              0.8 s
                                   total  ~52 s
```

**Recommendation: do not cache the wheel.** It would eliminate ~14 s, against
which `actions/cache` restore+save costs several seconds, and a stale key costs
more than no cache. The larger costs are `apt-get` (15.9 s) and the pip
downloads (18.9 s), neither addressed by caching the wheel. The premise that
"arcticpy compiles on every CI run" is true, but the compile turns out to be
cheap — arctic is a small C++ extension. If revisited, target `apt-get`.

## Design note — why a composite action, and how consumers reference it

PyAutoHeart had no `.github/actions/` before this. It is the right shape because
PyAutoHeart is **public**, so `uses: PyAutoLabs/PyAutoHeart/.github/actions/
install-arcticpy@main` resolves from any consumer with no checkout of Heart —
the same reach and reference style the reusable workflows already have. A shell
script in Heart would have needed each consumer to fetch it first.

`smoke_install.sh` is bash and cannot `uses:` an action, so the arcticpy install
moved OUT of the workspace epilogue into Heart's `smoke-tests.yml` behind a new
`arcticpy: true` input (default false, so every non-CTI caller is byte-identical).
That matches the precedent already in `lib-tests.yml`, which gates its arcticpy
step on `inputs.package == 'autocti'`.

## The self-test, and why it exists

`PyAutoHeart/.github/workflows/arcticpy-action.yml` +
`.github/scripts/arcticpy_smoke.py`. Because consumers reference the action at
`@main`, a recipe change would otherwise reach four repos with nothing having
exercised it. The self-test references the action by **local** path so it builds
the branch's version, and asserts a real CTI trail rather than "pip exited 0".
It is what caught both recipe bugs above.

## Docs fixed

`PyAutoCTI/AGENTS.md` §arcticpy (the note the other repos cite as canonical, and
the least complete — it omitted Cython *and* setuptools *and* the runtime deps),
`autocti_workspace/AGENTS.md`, `autocti_workspace_test/AGENTS.md`, and
`autocti_assistant/skills/ac_setup_environment.md` (whose broken
`arcticpy.__version__` verification is also fixed). All four now point at the
action as the recipe's single owner and the home of the pin.

Note: the assistant's `.claude/skills/*.md` are symlinks into `skills/` (git
mode 120000) — confirmed on the branch; one edit covers both surfaces.

## Original prompt

# Standardise the arcticpy CI install across every CTI repo

Type: maintenance
Target: pyautoheart
Repos:
- @PyAutoHeart
- @autocti_workspace_test
- @autocti_assistant
- @PyAutoCTI
- @autocti_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

`import autocti` hard-requires **arcticpy**, which is not a pip dependency: its
sdist is source-only (needs `libgsl-dev` + a C++ toolchain + Cython) and its own
requirements downgrade numpy below 2.0. Every CTI repo that runs CI therefore
carries its own copy of the install recipe. There is no single owner, the copies
have already **diverged in a way that matters**, and the recipe as documented is
incomplete for a clean environment.

Make one canonical arcticpy install step, owned by the organ that owns the
reusable CI workflows, and have every CTI repo consume it.

## The duplication today (verified by reading the files)

- `autocti_workspace_test/.github/scripts/smoke_install.sh` — the install
  epilogue for PyAutoHeart's reusable Smoke Tests workflow.
- `autocti_assistant/.github/workflows/wiki-currency.yml`, step "Install the
  stack (source @ main, or a pinned release)" (~L120-138). Its own comment says
  *"Recipe mirrors autocti_workspace_test/.github/scripts/smoke_install.sh"* —
  copy-paste, acknowledged in a comment rather than factored out.
- `autocti_workspace/AGENTS.md` §arcticpy and
  `autocti_assistant/skills/ac_setup_environment.md` document the same recipe
  for humans/agents. `PyAutoCTI/AGENTS.md` is cited by both as holding the
  canonical note plus a no-root header workaround — **not verified, PyAutoCTI
  was not checked out for this prompt.**
- **To audit:** PyAutoCTI's own lib-tests CI must install arcticpy somehow too;
  that site is unread here. Any other repo whose CI imports `autocti` counts.

## The divergence that matters

`wiki-currency.yml` runs `python -m pip install --upgrade pip setuptools wheel`
*before* the arcticpy build. `smoke_install.sh` does **not** — it installs only
`numpy cython` and relies on the runner image's ambient `setuptools`.

`--no-build-isolation` means every build dependency must already be present, and
arcticpy does not declare them. So `smoke_install.sh` is one runner-image change
away from breaking, and Python 3.12+ venvs no longer ship setuptools by default.
This is a latent failure, not a style nit.

## Verified build requirements (measured 2026-08-24, clean Ubuntu container)

Built arcticpy 2.6 successfully from a bare Python 3.12 venv. Each missing build
dep failed the build with an error naming the next one:

1. `setuptools` missing → build fails (`ModuleNotFoundError: setuptools`)
2. `Cython` missing → build fails (`ModuleNotFoundError: No module named 'Cython'`)
3. with both present → **builds and works**

Working recipe:

```bash
apt-get install -y libgsl-dev          # g++/gcc/make already present on the image
pip install numpy scipy setuptools wheel Cython matplotlib
pip install arcticpy==2.6 --no-build-isolation --no-deps
```

`matplotlib` is a *runtime* import (`arcticpy/read_noise.py`), needed only
because `--no-deps` suppresses it; the CTI stack installs it anyway, so it is
not a build dep. Verified working end-to-end: `add_cti` on a single bright pixel
produced a correct exponential CTI trail with charge conserved.

**Consequence for the docs:** the recipe in `autocti_workspace/AGENTS.md` and
`ac_setup_environment.md` says "after numpy+cython" and omits `setuptools`. That
is incomplete for a clean venv on modern Python — a first-time user following it
verbatim hits the same `ModuleNotFoundError: setuptools` I did. Fix the prose in
the same task.

## Work

1. **Put the canonical step in PyAutoHeart**, alongside the reusable workflows
   the CTI repos already call (`smoke-tests.yml`, `lib-tests.yml`,
   `docs-build.yml`). A composite action (`.github/actions/install-arcticpy/`)
   is the natural shape — callable from a plain step, version-pinned in one
   place. **Check PyAutoHeart's actual layout and conventions before choosing
   the shape**; do not assume a composite action is how that repo does things.
2. **Add the missing `setuptools wheel`** to the canonical step, so the
   `smoke_install.sh` latent failure cannot recur anywhere.
3. **Assert the install worked** — end the step with
   `python -c "import arcticpy; print(arcticpy.__version__)"`. Today a broken
   arcticpy surfaces much later as a confusing `import autocti` failure in an
   unrelated job.
4. **Repoint every consumer** at the canonical step and delete the local copies.
5. **Fix the documented recipe** in `autocti_workspace/AGENTS.md`,
   `autocti_assistant/skills/ac_setup_environment.md` and (if it carries the
   same omission) `PyAutoCTI/AGENTS.md`, so human/agent instructions match CI.
6. **Single pin.** `arcticpy==2.6` is currently written out in every copy;
   after this, bumping it should be a one-line change.

## Optional, decide deliberately

arcticpy compiles from source on **every** CI run in every CTI repo. Caching the
built wheel (`actions/cache` keyed on arcticpy version + Python version + runner
image) would cut that repeatedly. Not required for correctness — raise it as a
measured proposal with before/after timings rather than assuming it is worth the
cache-invalidation complexity.

## Why now

Filed after `test-mode-bypass-assertion-ties` and `testmode-assertion-note-removal`
(both shipped 2026-08-24). Two tasks in that sequence were deferred on the
belief that arcticpy could not be built outside a prepared machine — a belief
that turned out to be false, and cost real work. A canonical, documented,
CI-owned install is what stops that assumption forming again.

Unblocks: `draft/test/autocti/phase5_smoke_reenable_ordered_trap_scripts.md`
(CTI epic Phase 5) and helps `draft/bug/autocti/wiki_currency_baseline_drift.md`,
whose baseline regeneration needs the same stack.
