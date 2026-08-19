- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/239 (auto-closed on merge)
- shipped: 2026-08-19 — PyAutoBrain PR https://github.com/PyAutoLabs/PyAutoBrain/pull/240
- classification: bug (PyAutoBrain) — first of the three knowledge-board follow-ups (#32).
- summary: the memory faculty gained the PyAutoMemory root surface (index.md,
  reading-queue.md, bibliography/README.md, wiki/CLAUDE.md) — the repo's own front door
  was invisible to the faculty consuming it; verified live (`pyauto-brain memory
  "reading queue"` now ranks index.md [PyAutoMemory/root]); the 722 KB .bib stays
  excluded by design. Retired *_wiki names removed everywhere: policy.yaml memory_wikis
  keys + target_default_wiki values (autonerves/pyautonerves added beside legacy
  autoconf), the feature/bug conductors' printed context pointers (they named a
  nonexistent lensing_wiki/index.md), samplers faculty prose+digest string,
  sampler_pipeline SKILL (incl. the :75 write instruction that would have created a
  lint-rejected root methods_wiki/), MIND_TAXONOMY, adoption config_surfaces (which
  also mislocated the keyword map — it lives in config/policy.yaml), Mind REFERENCE.md.
- validation: 367/367 Brain tests; NEW tests/test_memory_surfaces.py is the faculty's
  first regression net (root-surface membership, repo-first labels for exit-4, the
  deliberate .bib exclusion, and a live assertion that every policy wiki name resolves
  to PyAutoMemory/wiki/<d>/index.md).
- key trap: sizing was never affected — it only flattens the keyword lists; the keys
  were labels. The real damage of stale layout names is printed pointers and prose
  instructions that route agents to nonexistent paths.
- affected-repos:
  - PyAutoBrain

## Original prompt

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
