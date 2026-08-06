## crlf-line-endings-cleanup
- completed: 2026-07-25
- summary: Org-wide CRLF→LF normalisation (878 files across Nerves/Fit/Array/Galaxy/Lens) with `* text=auto eol=lf` .gitattributes enforcement everywhere (PyAutoLens patches/ kept -text); every diff proven endings-only, all suites green (PRs incl. PyAutoNerves#139). Also absorbs the narrower crlf_script_normalization_gitattributes refactor prompt, folded below.

## Lifecycle note

Record backfilled 2026-08-06 (draft resolution-banner sweep): the work shipped with a RESOLVED banner written into the draft, but the prompt never advanced out of draft/; retired here dated by resolution day.

## Original prompt (autoarray_crlf_line_endings_cleanup)

> **RESOLVED 2026-07-25 — implemented org-wide, beyond the original PyAutoArray
> scope.** All five libraries normalised in one mechanical pass (878 CRLF text
> files -> LF: Nerves 46, Fit 127, Array 234, Galaxy 357, Lens 114) with
> `* text=auto eol=lf` .gitattributes enforcement added everywhere (PyAutoLens
> `patches/` marked `-text` to stay byte-exact). Every diff proven endings-only
> via `git diff --ignore-cr-at-eol`; all suites green. PRs: PyAutoNerves#139,
> PyAutoFit#1419, PyAutoArray#407, PyAutoGalaxy#524, PyAutoLens#651 (merged).

# Normalise CRLF line endings in PyAutoArray (+ add .gitattributes)

Type: maintenance
Target: libraries
Repos:
- @PyAutoArray
Difficulty: easy
Autonomy: full
Priority: low
Status: draft

## Context

PyAutoArray's AGENTS.md mandates Unix LF line endings, but a number of tracked
`.py` files are stored with CRLF in the git blobs. Observed during the
2026-07-24/25 heart-to-green work:

- `autoarray/inversion/mesh/image_mesh/abstract_weighted.py` — CRLF (edited
  matching-CRLF in #404 to keep the diff minimal)
- `autoarray/inversion/inversion/abstract.py` — CRLF
- the de-facto convention across `inversion/mesh/image_mesh/` is CRLF, while
  e.g. `inversion/plot/inversion_plots.py` is LF — the tree is mixed.

Two agents independently flagged this: naive text-mode edits rewrite whole
files (diff noise, review pain), and mixed endings make `.gitattributes`-less
checkouts platform-dependent.

## Task

1. Inventory: `git grep -Il $'\r' -- '*.py'` (and non-py text files) across
   PyAutoArray; consider the sibling libraries too if the same drift exists.
2. Normalise to LF in one dedicated, mechanical commit (no logic changes —
   easy to review with `git diff -w` / `--ignore-cr-at-eol`).
3. Add a `.gitattributes` (`* text=auto eol=lf` or targeted `*.py text eol=lf`)
   so the drift cannot recur.
4. Coordinate timing: land when no long-lived feature branches are open on the
   affected paths (a whole-file ending change conflicts with everything).

## Acceptance

- `git grep -Il $'\r' -- '*.py'` returns nothing in PyAutoArray.
- `.gitattributes` present; a fresh clone on Windows/WSL checks out LF.
- Zero behavioural diff (byte-identical modulo line terminators).

## Original prompt (crlf_script_normalization_gitattributes)

# Normalize CRLF in executable scripts + add .gitattributes eol=lf guards

Type: refactor
Target: libraries
Repos:
- PyAutoConf
- PyAutoFit
- PyAutoLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

The right-sized version of the CRLF fix (the hygiene `crlf` check surfaced it,
severity-split 2026-07-11, PyAutoBrain#98/#99). **Scope is the ~6 executable
scripts that actually break on Linux/HPC — NOT the ~710 cosmetic library `.py`.**
A CRLF shebang (`#!/bin/bash\r`) makes the kernel look for interpreter
`/bin/bash\r` → "bad interpreter" — exactly the "bash scripts don't work on HPC"
pain. Library `.py` CRLF is harmless (Python universal newlines) and mass-
normalising it churns `git blame` across the codebase for zero functional gain.

**Do:**
1. **Normalize the executable scripts with CRLF → LF.** Live count (2026-07-11):
   6 — PyAutoConf 4, PyAutoFit 1, PyAutoLens 1. Find them with
   `hygiene crlf` (the ranked count) or per repo:
   `git grep -Il $'\r$' -- '*.sh'` + executable `.py`
   (`git ls-files --stage -- '*.py' | awk '$1 ~ /755$/'`, then grep those for CRLF).
   Fix: `sed -i 's/\r$//' <file>` / `dos2unix`.
2. **Add a `.gitattributes` to each repo** (none exist today) to keep scripts LF
   forever regardless of a Windows contributor:
   ```
   *.sh    text eol=lf
   *.bash  text eol=lf
   ```
   (and, for any directly-executed `.py`, an explicit `<path> text eol=lf`).
3. **Leave the ~710 library `.py` CRLF alone** for now. If eventual whole-repo
   consistency is wanted, that is a SEPARATE decision and the mechanism is
   `* text=auto` in `.gitattributes` — it normalises files **as they are next
   touched**, avoiding a single ~710-file retroactive diff. Do NOT bundle a mass
   `.py` normalization into this task without an explicit go.

**Boundary/why supervised:** the *fix* is behaviour-preserving (line endings on
scripts), but the *policy* (which repos get `.gitattributes`, whether to adopt
`* text=auto`) is a judgement — confirm the scope before the mass-normalise step.
Extend to the other repos (Array/Galaxy/Build/Brain/Reduce + workspaces) if they
gain script CRLF later; today the 6 are in Conf/Fit/Lens.

**Done when:** the executable scripts are LF, each affected repo has a
`.gitattributes` with `*.sh text eol=lf`, `hygiene crlf` reports 0 scripts, and
the ~710 cosmetic `.py` are untouched (unless the user opts into `* text=auto`).

<!-- filed 2026-07-11 from the "is dos2unix important to enforce?" discussion:
     enforce for scripts (break on HPC), NOT all code. See hygiene crlf severity
     split PyAutoBrain#98/#99 + feedback_crlf_files_in_pyautoarray.md. -->
