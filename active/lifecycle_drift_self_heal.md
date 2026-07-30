# Make the Lifecycle Drift index check self-healing

Type: maintenance
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: easy
Autonomy: supervised
Priority: high
Status: formalised

Original request (verbatim): "Make PyAutoMind's Lifecycle Drift CI self-healing:
on index drift, run `lifecycle.py index --apply`, commit and push the
regenerated index as a bot commit (with loop guard), failing/emailing only if
the repair push itself fails."

## Problem

`.github/workflows/lifecycle_drift.yml` fails `lifecycle.py index --check` on
every push to main while `complete/index.md` is stale, emailing the human once
per push. Because Mind pushes go directly to main, one stale commit turns every
subsequent push red until something regenerates the index. This has now caused
three email storms (2026-07-24 PR #97; 2026-07-30 morning `aba2ce5`; 2026-07-30
evening `fa35972` — ~25 failure emails 17:35–19:27 UTC).

The prevention pattern used so far — fold each drifting registry state into
`lifecycle.py record --apply` — cannot cover the third break: an ad-hoc
`git mv` of 10 phase-prompt files into `complete/2026/07/` *after* `record
--apply` had already regenerated the index, in the same commit. Any manual
mutation of `complete/` outside lifecycle.py re-breaks the index, and with many
concurrent agent sessions that will keep happening. The storm only ended when
the next `record --apply` (76f97f8) regenerated the full index as a side
effect.

## Required behaviour

- On **push to main**, an index-freshness failure is repaired, not reported:
  run `index --apply`, verify convergence with `index --check`, commit
  `complete/index.md` as a bot commit, and push. The run fails (and emails)
  only if the repair itself fails (non-convergence, or push rejected after
  rebase retries against concurrent main advances).
- Pushes made with the default `GITHUB_TOKEN` do not trigger new workflow runs,
  so the heal commit cannot loop; verify convergence before pushing anyway.
- On **pull_request**, keep the current read-only fail-with-message behaviour —
  a PR author should fix their own branch.
- The semantic `lifecycle.py check` (slug-state contradictions) stays a hard
  fail — those are real inconsistencies a regen cannot fix.
