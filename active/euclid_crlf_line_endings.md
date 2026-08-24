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
