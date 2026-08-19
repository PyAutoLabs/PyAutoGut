# Memory faculty blind spots + retired *_wiki layout names

Type: bug
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

Found by the 2026-08-19 knowledge-board census (PyAutoMemory#32):

- @PyAutoBrain/agents/faculties/memory/_memory.py:32-41 greps ONLY
  `PyAutoMemory/wiki/*` — it never reads `index.md` (the entry surface
  PyAutoMemory/AGENTS.md tells every agent to index first), never reads
  `reading-queue.md`, never reads `bibliography/`. The repo's own front door is
  invisible to the faculty that consumes it. Decide which of those surfaces the
  digest should include and add them.
- Retired pre-2026-07 `*_wiki` layout names still pinned:
  @PyAutoBrain/config/policy.yaml:31-44 (`lensing_wiki`, `methods_wiki`, …),
  `tests/test_policy_seams.py:50-53` (asserts the old keys),
  `agents/conductors/feature/_feature.py` (`TARGET_DEFAULT_WIKI` values),
  `agents/faculties/samplers/AGENTS.md:143`, `_samplers.py:220`,
  `skills/sampler_pipeline/SKILL.md:29,75`, plus `PyAutoMind/REFERENCE.md:435`.
  Verify what each actually resolves against today, then migrate to the
  `wiki/<domain>` names.
