# CORRECTED: HowToFit build target is fine — the stub is the Jammy2211 fork

Type: maintenance
Target: workspaces
Repos:
- @HowToFit
Difficulty: easy
Autonomy: supervised
Priority: low
Status: draft

## Correction (2026-07-25, supersedes the original finding)

The original version of this prompt claimed PyAutoLabs/HowToFit was an empty
shell missing `config/build/no_run.yaml`, failing PyAutoHands'
`test_every_build_target_owns_no_run` on full checkouts. **That was wrong.**

PyAutoLabs/HowToFit is fully populated (scripts/, notebooks/, config/build/
with no_run.yaml + profile_smoke.yaml + markdown_examples.yaml,
smoke_tests.txt). The failing test was a checkout artifact of the cloud
session that ran the health sweep: its `HowToFit` sibling directory was a
clone of **Jammy2211/HowToFit** — a stub containing only a README — so the
sibling-path check found no config there.

## Remaining (small) task

Two loose ends, both about the stub fork, not the org repo:

1. Decide the fate of **Jammy2211/HowToFit** (README-only stub). If it has no
   purpose, archive or delete it so tooling and session source-lists cannot
   confuse it with PyAutoLabs/HowToFit. (A stray
   `claude/g-heart-green-fable-opus-uuiaqf` branch with one harmless seed
   commit was pushed to it on 2026-07-25 before the mix-up was caught; branch
   deletion was permission-blocked from the session — remove it when
   archiving/cleaning.)
2. Check the cloud-session source configuration that produced the checkout:
   the session mapped `HowToFit` to the Jammy2211 fork while every other
   repo mapped to PyAutoLabs. Point it at PyAutoLabs/HowToFit.

## Acceptance

- Jammy2211/HowToFit archived/deleted or clearly marked; no session source
  list resolves `HowToFit` to the stub.
- PyAutoHands `test_every_build_target_owns_no_run` passes on a full sibling
  checkout that uses the corrected mapping (already true with the org repo).
