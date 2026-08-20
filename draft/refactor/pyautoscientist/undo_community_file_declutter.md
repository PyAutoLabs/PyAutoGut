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
