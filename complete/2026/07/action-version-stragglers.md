Bumped the last v2/v1 GitHub Action revisions to the fleet standard
(checkout@v4 / setup-python@v5 / upload-artifact@v4).

- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/217 (auto-closed)
- prs (all merged unchanged, mechanical version strings only):
  PyAutoHands#218 (`release.yml`: checkout@v2→v4 ×several, setup-python@v2→v5),
  PyAutoCTI#102 (`27c26a029`) + PyAutoGalaxy#539 (`908dfc25e`)
  (`draft-pdf.yml`: checkout@v2→v4, upload-artifact@v1→v4 — v1 was past
  end-of-life, so the JOSS draft jobs were likely already broken).
- fleet census (2026-07-30 audit): everything else already at v4/v5; the
  coordinated v4→v5 fleet bump stays deferred until GitHub sets a removal date.
- release.yml is only exercised by a rehearsal — the nightly covers it.

## Original prompt

# Bump the ancient GitHub Action revisions (v2/v1 stragglers)

Type: maintenance
Target: ci
Repos:
- PyAutoHands
- PyAutoCTI
- PyAutoGalaxy
Difficulty: small
Autonomy: safe
Priority: normal
Status: draft

## Problem

Fleet-wide census (2026-07-30): the workflows are uniform on
`checkout@v4` / `setup-python@v5` / `upload-artifact@v4` (the tier GitHub currently
emits Node-20 deprecation *warnings* for), except three files on genuinely ancient
revisions:

- `PyAutoHands/.github/workflows/release.yml` — `checkout@v2` (×several) +
  `setup-python@v2` in the release_workspaces / bump_library_colab_urls area.
- `PyAutoCTI/.github/workflows/draft-pdf.yml` — `checkout@v2`, `upload-artifact@v1`.
- `PyAutoGalaxy/.github/workflows/draft-pdf.yml` — `checkout@v2`, `upload-artifact@v1`.

`upload-artifact@v1` is past end-of-life and may already hard-fail those JOSS
draft jobs.

## Scope

Three tiny PRs (one per repo) bumping to the fleet-standard revisions
(checkout@v4, setup-python@v5, upload-artifact@v4). No behavioural changes; note
that `release.yml` edits cannot be exercised except by a rehearsal — keep the diff
mechanical. The coordinated fleet-wide v4→v5 bump is deliberately deferred until
GitHub sets a removal date (memory: claude-code-action also rejects branch
workflow edits — open these as normal PRs from a human-pushed branch).
