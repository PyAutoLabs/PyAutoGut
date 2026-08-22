# PyAutoNerves release — the prompt to hand a local session

Kept because the release is parked (`parked.md` →
`pyautonerves-release-for-regime-stamp`) and the instruction is the one artefact
that would otherwise live only in a chat transcript.

**Paste this and nothing else.** Do not append the floor-bump task; a two-task
prompt is part of why the first attempt stalled.

```
Release PyAutoNerves.

main is at 0ecefa0 with two merged, unreleased PRs (#154, #155). Both are in.
Run /release and publish. I've authorized this — you don't need to check back
before publishing.

Proceed on a GREEN Heart verdict. Only stop if Heart says YELLOW or RED, and
then just tell me the reason.
```

## Why it is this short

The first handoff prompt was ~40 lines and did not release. It ended with
*"Report the Heart verdict verbatim before publishing anything. Merge and release
approval are mine, not yours"* — an instruction to stop, which the session
correctly obeyed. It also reproduced the cloud session's STALE-Heart diagnosis,
sending a session with working tools off to investigate a problem it did not
have, and appended the autoarray floor bump as a second task.

The rule this taught: **a handoff prompt carries the instruction, not the
diagnosis.** Everything about why the release was parked belongs in `parked.md`.

## Afterwards — separate message, separate task

```
Bump autoarray's autonerves floor to the version just released.

PyAutoArray/pyproject.toml:30 currently pins autonerves>=2026.8.22.1, which
predates the SMALLDAT regime stamp, so PyPI installs get an unstamped autonerves.

Keep the existing comment above the pin (it explains the PyAutoLens#687/#702 JAX
reason) and add the stamp reason alongside it.

Do NOT remove the shape fallback in should_simulate or
_is_capped_at_the_current_cap — the floor governs what new installs write, not
the unstamped datasets already on disk.

Full context: draft/maintenance/libraries/bump_autoarray_autonerves_floor_after_stamp_release.md
```

## If it stalls again

Capture `pyauto-heart readiness --json` verbatim and the `/release` output
*before* concluding anything. The first failure was prompt-induced; the second
was never diagnosed. Do not assume a third is either.
