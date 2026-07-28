# Active Tasks

## multistart-prodigy-compile
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/93
- session: claude --resume 73eff5ef-e2f6-46ba-9304-60dade7008ac
- status: workspace-dev
- notes: phase A (measure, autolens_profiling) in flight; phase B (PyAutoFit pyloop batching) serialises behind preserve-in-zip-replace-member's PyAutoFit merge (#1414 / PR#1427)
- worktree: ~/Code/PyAutoLabs-wt/multistart-prodigy-compile
- repos:
  - autolens_profiling (feature/multistart-prodigy-compile)

## preserve-in-zip-replace-member
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1414
- status: library-shipped, awaiting-merge
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1427, https://github.com/PyAutoLabs/PyAutoGalaxy/pull/533 (docs, merge second)
- heart-ack: workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked script(s); manifest drift: tenant firewall (organ code); release validation stale
- worktree: ~/Code/PyAutoLabs-wt/preserve-in-zip-replace-member
- repos:
  - PyAutoFit (feature/preserve-in-zip-replace-member)
  - PyAutoGalaxy (feature/preserve-in-zip-replace-member)

## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- session: claude --resume daaa46f9-aac5-48e2-9146-1202a92d879e
- status: library-merged, workspace-pending
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (ALL MERGED 2026-07-27; codex-review fixes included; branches + worktree cleaned)
- phases: 1 (design) + 2 (core API) COMPLETE; next: start_workspace on active/../draft phase-3 prompt (workspace_test jax_likelihood + profiling examples), then phase 4 (guides), then phase 5 (JAX solver gradients)
- repos:
