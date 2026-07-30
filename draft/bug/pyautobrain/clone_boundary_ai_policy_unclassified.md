# clone-boundary is red on every autolens_assistant branch — AI_POLICY.md unclassified

`Difficulty: small`

The `clone-boundary` CI check in @autolens_assistant has failed on **every** branch
since `feature/ai-policy` merged on 2026-07-27. It is not branch-specific work that
breaks it — the check fails on the merge commit of any PR:

```
check_boundary: 1 file(s) in autolens_assistant fall on neither side of the template
boundary:

  ✗ AI_POLICY.md
```

`AI_POLICY.md` was added without being classified, and `check_boundary.py` refuses any
unclassified tracked file — "the Clone Agent refuses to birth a newborn while any is
unclassified", so this also blocks every future assistant birth, not just CI.

## Fix

Classify `AI_POLICY.md` as `generic`, `domain` or `mixed` and record it in **both**
places, which the check requires to agree:

1. @autolens_assistant `modes/maintainer.md`, `## Assistant-as-template` — the prose that
   owns the boundary.
2. @PyAutoBrain `agents/conductors/clone/_clone.py` —
   `REFERENCE_PROFILES['autolens_assistant']`.

Almost certainly **generic**: the AI-use policy is framework-level, not lensing science,
and a newborn assistant should inherit it near-verbatim.

Grounding already done (2026-07-30):

- `AI_POLICY.md` is a root-level file absent from `_SHARED_GENERIC`
  (`_clone.py:52-72`), which is why it lands unclassified. Adding `"AI_POLICY.md"` to
  that shared list covers both existing profiles at once.
- All three cells (`autolens_assistant`, `autofit_assistant`, `autocti_assistant`) carry
  an `AI_POLICY.md`, and **none** of their `modes/maintainer.md` files mention it — so the
  prose half is missing everywhere, not just in the lens cell.
- `REFERENCE_PROFILES` has entries for `autolens_assistant` and `autofit_assistant` only;
  `autocti_assistant` has no profile, and no `boundary` check ran on `autofit_assistant`'s
  PRs — which is why only the lens cell goes red. Decide whether the other two should
  gain the check as part of this fix or in a separate task.

## Related

- A separate `AI_POLICY.md` **structure-test** failure on `origin/main` is already
  recorded as the ship-blocker for `python-312-memory-validation-ci` in
  `active.md` (@PyAutoMemory). Check whether that is the same root cause before
  fixing either in isolation.
- Found while shipping `assistant-output-folder-pointer`
  (PyAutoLabs/autolens_assistant#96 / #97), whose own content is unrelated to it.
