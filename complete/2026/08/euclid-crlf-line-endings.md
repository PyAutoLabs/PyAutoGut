- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline/issues/40
- pr: https://github.com/PyAutoLabs/euclid_strong_lens_modeling_pipeline/pull/41 (merged 037bd06)
- repos: euclid_strong_lens_modeling_pipeline
- autonomy: `safe` (declared `safe` ∩ maintenance cap `safe`), launched `--auto`
- summary: Extended the 2026-07-25 org-wide CRLF sweep to the Euclid pipeline, the tier it
  never reached. 42 of 189 tracked files were CRLF and the repo had no `.gitattributes` at
  all. Six of the 42 execute or are sourced, so this was functional HPC breakage rather than
  the cosmetic `.py` churn the library sweep dealt with.

## The prompt did not exist

`/start_dev draft/maintenance/workspaces/euclid_crlf_line_endings.md --auto` was invoked on a
path that had no file behind it — only the task name existed. The prompt was written from a
live inventory of the repo at HEAD `62b2fd4` before dev started, per the workflow rule for a
development task with no prompt file. Worth knowing this happens: the recovery is to inventory
first and write the prompt from evidence, not to guess intent from the slug.

## Traps and findings

**1. `.gitattributes` is last-match-wins — the plan had the ordering backwards.**
The issue plan said to put the binary guards *first*:

```
*.fits binary          # ← silently overridden
* text=auto eol=lf
```

Git applies the **last** matching pattern, so `*.fits` resolved to `text: auto` and would have
been normalised anyway. Caught by running `git check-attr text -- <file>` *before*
renormalising rather than after. Correct form is the catch-all first, specifics after. The
shipped file carries a comment saying so, because the failure is silent.

**2. Git's text heuristic misfiles FITS as text.** `git grep -Il` reported two of the nine
tracked `.fits` as text: FITS headers are plain ASCII and those payloads carry no NUL in git's
sampled prefix. `text=auto` uses the same heuristic. Without the `*.fits binary` guard,
`git add --renormalize .` would have stripped ~10k CR bytes out of binary image data and
corrupted both datasets. `*.png` is declared for the same reason, plus a wrinkle: two files
named `.png` are actually JPEGs.

Generalises: **any repo mixing `text=auto` with FITS is exposed.** The five libraries adopted
`* text=auto eol=lf` in the July sweep — if any of them ever tracks a FITS file, it needs this
guard. Verify with hashes, never by reading the diff view: `git ls-files -s -- '*.fits'` before
and after must be byte-identical.

**3. `activate.sh` was the real bug, and it is subtle.** Its `PYTHONPATH` uses backslash
line-continuations. Under CRLF the backslash escapes the **CR**, not the newline, so the
continuation never happens — and the continuation lines get run as commands:

```
$ source ./activate.sh              # CRLF
./activate.sh: line 6: /mnt/ral/jnightin/PyAuto/PyAutoNerves:: No such file or directory
  ... (Fit, Array, Galaxy, Lens the same)
PYTHONPATH=[/mnt/ral/jnightin/PyAuto:]     ← all five library paths dropped
```

The HPC venv activation had been silently exporting a `PYTHONPATH` with every PyAuto library
missing. A CRLF shebang is the better-known half (`hpc/sync`, the four `hpc/batch_*` SLURM
scripts) but the continuation trap is the one that hides. `hpc/sync.conf.example` was
normalised alongside them: it is the template users copy to `hpc/sync.conf`, which `hpc/sync`
then sources, so leaving it CRLF reintroduces the fault downstream of the fix.

## Verification approach worth reusing

Split into two commits — the seven executed files (reviewable on its own) then the 33 cosmetic
ones via `git add --renormalize .`. The proof that the whole thing is endings-only:

```
git diff --ignore-cr-at-eol <base>..HEAD    →  only .gitattributes (+16)
```

Everything else in a 41-file, +2960/-2944 diff is line terminators. Binary integrity proven by
blob SHA against base (30 files, identical), not by inspection.

## Ship gate

The `web-github` session first recorded legs 1 (tests) and 2 (smoke) as **unrunnable** and
parked the task at push. That was premature. The blocker was the Debian-patched `setuptools`
in the container — `pip install autolens` died building `gprof2dot` / `timeout-decorator` with
`AttributeError: install_layout`, and upgrading setuptools in place failed too
(`Cannot uninstall wheel 0.42.0, RECORD file not found`). **Installing into a clean venv
bypasses the Debian layer and works first try.** Remember this: a failed system `pip install`
in one of these containers is not evidence that a leg cannot run.

With the stack installed both legs ran: `pytest tests/ -x -q` → 1 passed; all six
`smoke_tests.txt` scripts under `PYAUTO_TEST_MODE=2` → 6 passed, 0 failed. Two smoke scripts
first failed on `ModuleNotFoundError: 'jax'` then `'jaxnnls'` — missing optional deps of the
venv raised inside `autoarray`, unrelated to the diff; the `autolens[jax]` extra cleared them.
No code was changed to make a leg pass. Review CLEAN judged inline (the review faculty could
not resolve a checkout); Heart n/a (`pyauto-heart` absent).

Merged via `/prm` on the hand-run gate with explicit human authorization: the repo has **no CI
workflows**, so there were no checks to wait on.

## Follow-up

`Jammy2211/euclid_assistant` was never inventoried — it is in a different GitHub owner tier and
`add_repo` refuses cross-tier adds within a session. Whether it carries the same drift is
unknown. A session started with that repo as its initial source could check it in minutes.

## Original prompt

# Normalise CRLF line endings in the Euclid pipeline (+ add .gitattributes)

Type: maintenance
Target: euclid_strong_lens_modeling_pipeline
Repos:
- @euclid_strong_lens_modeling_pipeline
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

## Why

The 2026-07-25 org-wide CRLF sweep (`complete/2026/07/crlf-line-endings-cleanup.md`)
normalised 878 files and added `* text=auto eol=lf` .gitattributes enforcement
across the **five libraries** — Nerves, Fit, Array, Galaxy, Lens. It never
reached the workspace/pipeline tier, so `euclid_strong_lens_modeling_pipeline`
still carries the drift, with no `.gitattributes` at all.

Live inventory (2026-08-24, HEAD 62b2fd4): **42 of 189 tracked files** are CRLF.
Unlike the library case — where CRLF `.py` was cosmetic, since Python reads with
universal newlines — the Euclid pipeline's CRLF sits on the **HPC entry points
that actually execute**:

| File | First line (CR shown) | Consequence |
|------|----------------------|-------------|
| `hpc/sync` | `#!/usr/bin/env bash^M` | the `hpc/sync push-submit gpu …` driver — the documented way GPU runs are launched |
| `hpc/batch_gpu/submit_start_here` | `#!/bin/bash -l^M` | SLURM batch script |
| `hpc/batch_gpu/submit_full_model` | `#!/bin/bash -l^M` | SLURM batch script |
| `hpc/batch_cpu/submit_start_here` | `#!/bin/bash -l^M` | SLURM batch script |
| `hpc/batch_cpu/template` | `#!/bin/bash -l^M` | SLURM array template |
| `activate.sh` | `BASE=/mnt/ral/jnightin/PyAuto^M` | sourced venv activation; the stray CR lands inside `$BASE`, so every path built from it is wrong |

This is precisely the "bash scripts don't work on HPC" failure the earlier
`crlf_script_normalization_gitattributes` prompt named: a CRLF shebang makes the
kernel look for interpreter `/bin/bash^M`, and `bash <script>` on a CRLF file
carries the CR into every unquoted token. Nothing in this repo is mode 755, so
the scripts are invoked via `bash`/`sbatch`/`source` — which fails on CR the same
way, just with noisier errors.

The remaining 36 are cosmetic-but-tidy: 11 `.py`, 10 `.csv`, 8 `config/**.yaml`,
2 `.json`, 2 `.gitignore`, `hpc/sync.conf.example`.

## Hazard — two `.fits` files look like text to git

`git grep -Il` reports two FITS files as text:

- `dataset/q1_walsmley/102018665_NEG570040238507752998/102018665_NEG570040238507752998.fits` (840,960 B, 2,746 CR)
- `dataset/sample_group/group/group.fits` (2,949,120 B, 7,283 CR)

FITS headers are ASCII and these payloads happen to carry no NUL in the sampled
prefix, so git's binary heuristic — the same one behind `text=auto` — misfiles
them. A bare `* text=auto eol=lf` plus `git add --renormalize .` would strip
~10k CR bytes out of binary image data and **corrupt both datasets**.

So the `.gitattributes` must declare `*.fits binary` (and any other binary
extension present) **before** any renormalisation runs, and the change must be
verified byte-wise, not just eyeballed.

## Task

1. **Add `.gitattributes`** at the repo root, binary guards first:
   ```
   *.fits binary
   * text=auto eol=lf
   ```
   Audit the tracked extension list for any other binary type needing the same
   guard before renormalising.
2. **Normalise the 6 HPC/activation scripts to LF** in their own commit — this is
   the functional fix and should be reviewable on its own.
3. **Renormalise the remaining 36 cosmetic text files** to LF in a second,
   mechanical commit.
4. **Prove it is endings-only**: every diff clean under
   `git diff --ignore-cr-at-eol`, and both `.fits` byte-identical to their
   pre-change blobs (compare hashes against `HEAD`, do not trust the diff view).

## Acceptance

- `git grep -Il $'\r'` returns nothing outside the declared-binary paths.
- `.gitattributes` present with `*.fits binary` ahead of `* text=auto eol=lf`;
  a fresh clone checks out the scripts with LF on any platform.
- The two `.fits` blobs hash-identical to HEAD before the change.
- Zero behavioural diff — byte-identical modulo line terminators.
- `bash -n` parses each normalised shell script; `activate.sh` sources with a
  clean `$BASE`.

## Not in scope

`Jammy2211/euclid_assistant` — the other Euclid repo — was **not** inventoried:
it is in a different GitHub owner tier and could not be attached to the session
that filed this prompt. If it carries the same drift it is a follow-up prompt,
not a widening of this one.
