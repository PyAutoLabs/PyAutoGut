Docs-only workspace changes no longer run the full smoke matrix.

- issue: PyAutoHeart#126 (auto-closed) · pr: PyAutoHeart#127 (`ad0d8840f`), merged unchanged
- a `changes` gate job in the reusable smoke-tests.yml (all workspace callers, no new
  third-party actions): base = pull_request.base.sha || event.before, shallow fetch,
  two-dot diff; FAIL CLOSED (no base / zero sha / unfetchable / empty diff / any
  non-allowlisted file → matrix runs); allowlist only *.md, root docs/, LICENSE,
  runtime.txt (dotfiles/sidecars count as code). Skips list files in the step summary;
  a skipped matrix satisfies required checks. Wiring test pins the needs+if shape.
  Classifier exercised over 8 edge cases. Library main.yml untouched by design.

## Original prompt

# Docs/metadata-only PRs should not run the full smoke matrix

Type: maintenance
Target: workspaces
Repos:
- PyAutoHeart
- autofit_workspace
- autogalaxy_workspace
- autolens_workspace
- HowToFit
- HowToGalaxy
- HowToLens
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Problem

Every workspace `smoke_tests.yml` is `on: [push, pull_request]` with no path
filter, so a README/docs/metadata one-liner triggers the full reusable matrix
(2 Python versions × 5-library chain checkout + install + smoke run). The current
system over-tests routine changes without proportionate confidence.

## Scope

Design once, apply per repo. Preferred shape: a cheap `changes` gate job inside
Heart's reusable `smoke-tests.yml` (e.g. `dorny/paths-filter` or a plain
`git diff --name-only` step) that skips the matrix when the diff touches only a
conservative docs allowlist (`*.md`, `docs/`, `LICENSE`, `runtime.txt`, `.github/*.md`)
— putting it in the reusable body means one implementation for all callers, and
the check still *reports* (skipped-as-success with an explanatory summary), so
branch-protection semantics stay intact.

Explicitly out of scope until separately decided: path-filtering the *libraries'*
`main.yml` (unit tests are the libraries' only PR gate — keep them universal), and
any filtering of scheduled/dispatch runs (mode of the weekly sweep unchanged).

Careful: the allowlist must fail CLOSED — anything not matched runs the matrix.
Dotfiles and sidecars count as code (memory: extension-filtered sweeps hide
CI-load-bearing dotfiles).
