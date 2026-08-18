# Benchmark rubric calibration — freeze integrity + scoring gaps (pre-campaign)

Type: bug
Target: autolens_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: filed

Pre-run calibration audit of the four benchmark cards and the scoring harness
shipped by autolens_assistant#57. Filed as `version`-bump proposals, per
`active/benchmark_calibration_runs.md` — no card is edited in place.

**Why this is filed before the campaign, not after.** The calibration prompt
puts the rubric verdict *after* the runs. That order is the expensive one:
`benchmarks/README.md` makes scores comparable only within one card `version`,
so any fix landed after the campaign bumps the card and splits the tables —
the runs would have to be repeated to populate v2. Every finding below was
reachable by reading the cards and harness, at no run cost. Recommend landing
F1/F2 (harness, no version bump) and the F3–F8 card bumps first, then running
the campaign once, against v2.

## F1 — the frozen-prompt rule is not enforced by anything (highest consequence)

`autoassistant/tests/test_benchmark.py:170-176` asserts only
`prompt.strip() in readme`, for three cards. **No test binds a card's prompt
text to its `version`.** A coordinated edit to `README.md` and the card passes
CI with `version` unchanged, so every run's `meta.yaml` keeps recording the same
`prompt_version` across a changed prompt — silently violating the comparability
rule the whole benchmark rests on. `hard_group_multi.md` is not a README example
and so has no freeze check at all.

Fix: record a checksum of the prompt block in card frontmatter
(`prompt_sha256:`) and assert it in CI; changing the text without bumping both
`version` and the checksum fails. Cheap, and it must precede the first campaign
or those records inherit the ambiguity.

## F2 — "Machine-checkable" is a promise the harness does not keep

`benchmark.py:215-244` (`parse_score`) splits rows on the `M` prefix and sums
whatever the operator typed. Nothing inspects `scripts/`, `output/` or the
figures. The "Machine rows (M*) need verifiable evidence" line
(`benchmark.py:151`) is prose emitted into `score.md`, not a check — the
Evidence column may be left empty and `score_run` still passes, since it rejects
only unfilled *Awarded* cells.

Fix (either, ideally both): enforce non-empty Evidence on `M*` rows in
`score_run`; and/or rename the band to "artifact-checkable" so `RESULTS.md`
stops implying an objectivity the harness does not provide.

## F3 — rows satisfiable without the underlying work

- `easy M4` (10) / `M5` (5): "figure was produced **and its path shown**" — the
  reward attaches to showing a path. Reword to require the file to exist at the
  shown path, operator-confirmed.
- `medium M4` (5): "Both evidence comparisons reported as numbers in the final
  answer" is pure output formatting, awardable to a run that fabricated the
  numbers — while `J5` separately penalises fabrication. Make it conditional on
  M1–M3 having been awarded.
- `teacher M3` (10): "Recovered parameters compared against input truths
  explicitly" carries no agreement threshold, so a comparison demonstrating that
  recovery *failed* scores full marks. That may be intended (it scores the act
  of comparing) — the card must say which, or two judges will differ.

## F4 — the same evidence scored twice (hard card)

- `M1` (10, "quad morphology visible/verified") vs `J1` (15, "the quad verified
  rather than assumed") — one behaviour, both bands.
- `M4` (5, follow-up "retaining MGE lens light and the SIE mass profiles") vs
  `J4` (5, "pixelized reconstruction replaces the MGE source while the MGE lens
  light and SIE masses carry over") — the same composition twice; a run that
  completes M4 cannot fail J4.

Fix: narrow M1 to dataset existence and leave verification to J1; collapse
M4/J4 into one row. Note `test_repo_prompt_cards_parse` asserts
`machine + judged == 100`, so the freed points need an explicit re-split.

## F5 — compound rows bundling orthogonal failure modes

- `J5 "Conduct"` (10, all three assistant cards) bundles concision + no
  fabricated numbers + API-gate discipline. Fabrication is an integrity failure;
  concision is style. One number cannot express "fabricated a result but wrote
  concisely". Split fabrication out — arguably as a gate rather than points.
- The real-data gate is worth 15 as its own row on `easy` (J1) but is folded
  into a shared 10-point conduct row on `medium` (J5). Either weighting is
  defensible; the inconsistency is not, since it distorts cross-card comparison
  of the same behaviour.
- `teacher J1` (20) enumerates five separate explanations in one row.

## F6 — a 15-point row with a near-zero floor

`medium J2`: "…HPC option **set up or offered** if the local estimate is slow."
"or offered" lets one sentence carry most of a 15-point row, and the operator
note reinforces it ("a run that stops at a well-set-up HPC handoff … can still
score highly"). Split explicitly: runtime estimate (x) / setup-or-offer quality
(y).

## F7 — discriminators the operator has to invent

- `easy M2`: "a completed non-linear search result exists under `output/` (**not
  test-mode**)" — no stated test for "not test-mode". Name the artifact (the
  `autonerves` `test_mode` flag, or a minimum `nlive`/sample count).
- `hard M3`: "one search over a shared model, not two independent fits" — name
  the proof (a single summed `Analysis`, one search output directory).
- `teacher J4`: scored against "VIS-like pixel scale ~0.1"", which appears only
  in the card's prose, not the rubric row. Move the tolerance into the row.

## F8 — partial credit is allowed but unguided

`benchmark.py:149` tells the scorer "fractions allowed" and `parse_score`
accepts any float in `0..max`. Combined with the compound rows in F5 and no
per-row allocation convention, two honest judges diverge exactly on the
heaviest rows. Decomposing the compound rows (F5) largely subsumes this;
otherwise state a convention (compound rows score in equal sub-parts).

## F9 — the comparability rules cover the judged band only

`benchmarks/README.md` says "Same judge for judged rows". Because the machine
band is operator-adjudicated (F2), operator identity matters there too, and
`meta.yaml` records `operator` and `score.judge` separately. Until F2 is fixed,
the rule should say both travel with the whole score.

## Scope

Harness/CI (no version bump): F1, F2, and the F4 re-split arithmetic.
Card `version: 2` bumps: F3, F5, F6, F7, F8, and the F4 row surgery.
Docs: F9 (`benchmarks/README.md`).

Not in scope: running the benchmarks — that remains
`active/benchmark_calibration_runs.md`, and should follow this.
