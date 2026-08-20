## undo-community-file-declutter
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/253
- completed: 2026-08-20
- workspace-pr: https://github.com/PyAutoLabs/PyAutoMind/pull/254 · https://github.com/PyAutoLabs/PyAutoMemory/pull/40 · https://github.com/PyAutoLabs/PyAutoBrain/pull/244 · https://github.com/PyAutoLabs/PyAutoHeart/pull/157 · https://github.com/PyAutoLabs/PyAutoHands/pull/245
- summary: Undid the 2026-08-19 community-file declutter (#248 Mind, #32 Memory):
  AI_POLICY.md + CONTRIBUTING.md moved from .github/ back to the repo root in Mind,
  Memory, Brain, Heart and Hands — dashboards are the primary interface now, so root
  scannability no longer justified the split placement (Gut/Nerves/Scientist had kept
  root copies). Lockstep contract updates: spawn.py MIND_RULES + MEMORY_RULES, both
  spawn tests, spawn_spec.md rules 3b/1b, Memory validate_structure ALLOWED_TOP_FILES.
  Gotcha hit AGAIN: a concurrent session's prompt_sync swept this task's staged Mind
  edits into its own commit on the feature branch, stranding its active.md repo-claim
  off main — repaired by restoring the claim to main and merging main back into the
  branch (no history rewrite); main briefly carried the claim line twice and the PR
  deduped it.

## Original prompt

# Undo the community-file declutter — AI_POLICY/CONTRIBUTING back to repo roots

Difficulty: easy
Autonomy: supervised

## Original request (verbatim)

> We did a "declutter" moving some files across repos (e.g. AI_Policy.md) to
> make the contents of the repo more visble, but now dashboards are the main
> interface its not required. Can you undo this decluttering, which is just
> confusing moving a few files to another folder

## Scope

The 2026-08-19 declutter (#248 Mind, #32 Memory) moved `AI_POLICY.md` +
`CONTRIBUTING.md` into `.github/` in five repos: @PyAutoMind, @PyAutoMemory,
@PyAutoBrain, @PyAutoHeart, @PyAutoHands (Gut/Nerves/Scientist kept root).
Now dashboards are the primary interface, root clutter no longer matters and
the split placement is just confusing. Move both files back to each repo
root, updating the move contract in lockstep:

- Mind `scripts/spawn.py` MIND_RULES + MEMORY_RULES `.github/` entries → root
- both spawn tests (`test_spawn_privacy.py`, `test_spawn_template_contract.py`)
- `docs/pyautobrain/spawn_spec.md` rules 3b / 1b
- Memory `scripts/validate_structure.py` ALLOWED_TOP_FILES += both files

No other references to the `.github/` paths exist (swept all repos).
