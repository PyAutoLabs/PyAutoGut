# Active Tasks

## issue-cleanup
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/174
- session: claude
- status: awaiting-merge — PR https://github.com/PyAutoLabs/PyAutoBrain/pull/175 open (b42a831). POST-MERGE: run bin/install.sh from the CANONICAL checkout to create the ~/.claude command+skill symlinks — running it from a worktree repoints ~/.claude at that worktree.
- worktree: ~/Code/PyAutoLabs-wt/issue-cleanup
- autonomy: supervised
- prompt: active/issue_cleanup_skill.md
- note: Builds /issue_cleanup, the missing issue-tracker reconciliation door (no skill owned this — /repo_cleanup is git debris only, /community is external issues). Preceded by an ad-hoc sweep on 2026-07-28 that took the trackers 82 open → 47: closed 29 shipped-but-open (two-leg verified: record header + merged PR) and 6 obsolete 2018–2019 PyAutoCTI (named API greps zero in autocti/). LOAD-BEARING FINDING the skill must encode: the PyAutoMind record header KEY carries the meaning — `issue:` (630 uses) completes, but `followup-issue:`/`follow-up-issue:`/`library-followup-issue:`/`parent-issue:`/`upstream-issues-filed:`/`plan:` (13 uses) mean the record SPAWNED a still-open issue; a loose `*issue*:` match would close live follow-ups. Three more traps: body mentions ≠ header claims (many-vis-prep-dft.md discusses PyAutoArray#326 while its own issue: header says "no GitHub issue"); inline `(open …)`/`(STAYS OPEN …)` annotations override and appear on `plan:` lines too; a record in complete/ can carry `Status: issued` (ep-hierarchical-scale-collapse.md FILED PyAutoFit#1405, which is a live bug). PyAutoHands#16/#17 deliberately LEFT OPEN — same 1337-day vintage as the closed CTI ones but still-valid unimplemented asks (no --pre workflow, no RTD gating exist), so age ≠ obsolescence. Approved mode: audit auto-runs read-only in /wake_up, every close stays human-gated. Brain said large/split-into-phases — OVERRIDDEN to single phase (one skill, one repo, reasoning already settled); its "public-API ripple" risk is a false positive for a skill body. Claimed PyAutoBrain over a STALE guard-followups claim (all 3 of its PRs merged 12:53 2026-07-28; that entry has since been cleaned up by its own session). TWO MORE traps found by the skill's own regression bar, not by the sweep — they are why the bar ships with the skill: (a) Rule 1 was too loose — matching any `- word:` line as a header re-admits prose, because records use `- notes:` for paragraphs citing issue URLs freely (PyAutoGalaxy#417 is cited ONLY there, so nothing claims it); header keys are now a known-set allowlist. (b) NEW Rule 4 — a phase-scoped claim ("(Phase 5 item 4)") completes a PIECE, not the issue; 4 records each claim a Phase-5 item of PyAutoBrain#130 and none establishes it is done, so scoped claims route to bucket B. Bar pins post-sweep state 47 open / A=0 / B=1 / C=7 / spawn-held=3 / D=6 / E=8 / F=22 and both traps by name; ALL PASS at b42a831.
- repos:
  - PyAutoBrain: feature/issue-cleanup


## pix-prodigy-cpu
- issue: https://github.com/PyAutoLabs/autolens_workspace_developer/issues/117
- session: claude
- status: workspace-dev
- worktree: ~/Code/PyAutoLabs-wt/pix-prodigy-cpu
- autonomy: supervised
- prompt: active/pixelized_multistart_prodigy_cpu.md
- repos:
  - autolens_workspace_developer: feature/pix-prodigy-cpu
  - autolens_profiling: feature/pix-prodigy-cpu
  - autolens_workspace: feature/pix-prodigy-cpu

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-merged, workspace-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; next: start_workspace on active/../draft phase-3 prompt (workspace_test jax_likelihood + profiling examples), then phase 4 (guides), then phase 5 (JAX solver gradients)
- repos:
