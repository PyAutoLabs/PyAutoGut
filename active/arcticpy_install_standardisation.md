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
