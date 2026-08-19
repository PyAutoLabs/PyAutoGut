# Active Tasks

## memory-surfaces-stale-names
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/239
- status: in-dev — issued 2026-08-19, plan approved (batch of three knowledge-board
  follow-ups, executed A→B→C); PyAutoBrain fix/memory-surfaces-stale-names
- prompt: active/memory_surfaces_stale_names.md
- repos:
  - PyAutoBrain: fix/memory-surfaces-stale-names
- summary: memory faculty gains the PyAutoMemory root surface (index/queue/bib-README/
  schema); retired *_wiki names renamed across policy.yaml, printed conductor pointers,
  samplers/sampler_pipeline/MIND_TAXONOMY/adoption prose, Mind REFERENCE; policy-seam
  tests updated + first memory-faculty tests.

## wiki-hygiene
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/34
- status: queued behind memory-surfaces-stale-names (same session, sequential)
- prompt: active/wiki_hygiene.md
- repos:
  - PyAutoMemory: maintenance/wiki-hygiene
- summary: PDF frontmatter paths → new archive: provenance field (human-decided KEEP;
  schema amended); alias subsystem retired (human-decided); ~19 path-shaped wikilinks
  → slugs; uncited junk bib keys (SN/ADS/colon classes) deleted.

## paper-management-pipeline
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/35
- status: queued behind wiki-hygiene (same session, sequential)
- prompt: active/paper_management_pipeline.md
- repos:
  - PyAutoMemory: feature/paper-management-pipeline
- summary: land the dev-box's uncommitted queue tidy; reading-queue sections → real ##
  headers with a DONE <date> read-state convention; board shows waiting/read per
  section; the Mind arXiv Slack digest gains a paste-ready one-tap queue-append block
  (human-gated).

## jax-default-dependency
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/702
- status: shipped-awaiting-release-followups — ALL ELEVEN PRs merged 2026-08-19 (human-authorized):
  six library (PyAutoHeart#150, PyAutoNerves#150, PyAutoFit#1503, PyAutoArray#450, PyAutoGalaxy#574,
  PyAutoLens#703) + five workspace (autolens_workspace#486, autogalaxy_workspace#212,
  autofit_workspace#139, HowToLens#71, HowToGalaxy#67; pending-release hold waived by human — prose-only,
  few-hour docs-ahead window until the nightly). Worktree removed, claims released, branches deleted.
- nojax CI leg caught two real bugs day one: unmarked jax-requiring autolens test (94d8f54ba);
  NumPy-scalar misrouting in autofit Beta/Gamma/Normal message dispatch (19c679583).
- jax cap stays <0.11 (widen reverted 848a254; jax 0.11 bug prompt:
  draft/bug/autofit/jax_011_message_log_partition_tuple_shape.md).
- NEXT (release-blocked; nightly 02:00 UTC): (1) bump intra-family floors `>=2026.7.29.2` → first
  promoted version in all five pyprojects, then move this task to complete/; (2) later, make
  unittest-nojax a required check once it has green history.
- prompt: active/jax_default_dependency.md

## transformed-message-factor-gradient-unpack
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1501 (issued 2026-08-19)
- prompt: active/16_transformed_message_factor_gradient_unpack.md
- status: HOLD — do not start dev. Fix-or-delete hangs off the PyAutoFit#1498 logpdf-contract
  decision (parked #1500 design bundle); dead code (zero production callers), crashes on first
  call if ever exercised.
- external: community PR https://github.com/PyAutoLabs/PyAutoFit/pull/1502 (@trexfr-ops) targets
  this exact unpack — review via /community before any local work; the #1498 adjudication decides
  whether the method should exist at all.
- registered: 2026-08-19 by the wake_up session — the issuing session (claude/autofit-priors-messages-audit-ylvenv)
  filed the prompt + issue but not this entry, tripping Lifecycle Drift on main.
- repos-none-claimed: this entry claims NO repos — one line deliberately, not 2-space bullets.
