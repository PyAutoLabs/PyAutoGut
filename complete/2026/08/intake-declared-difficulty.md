## intake-declared-difficulty
- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/274
- completed: 2026-08-24
- brain-pr: https://github.com/PyAutoLabs/PyAutoBrain/pull/275 (MERGED as 979fac5; pytest 3.12 + 3.13 green, 491 passed, tenant-firewall leg green)
- mind-pr: https://github.com/PyAutoLabs/PyAutoMind/pull/308 (MERGED as 243a871; lifecycle state only)
- prompt: active/intake_ignores_declared_difficulty.md (folded below)
- summary: the precedence rule "a DECLARED header key beats a value derived from
  prose" now lives ONCE, in the sizing faculty, instead of being re-implemented
  per conductor. `_sizing.effective_difficulty` (moved out of `_feature.py`) is
  the rule: declared wins, and the derived level + score come back alongside so a
  disagreement is REPORTED rather than silently resolved. `declared_header` also
  reads `Type:` and `Autonomy:`; new `declared_inline` reads the same keys out of
  unheadered conception prose. Intake and the Bug Agent now go through it.
- root cause, stated exactly: `_intake.analyse()` hand-built the prompt-shaped
  dict it passes the faculty and omitted the `declared_header(text)` keys that
  `parse_prompt` (the FILE-loading path) does fold in. So `estimate_difficulty`
  ran with no declared key present, nothing reconciled derived against declared,
  and the derived level was written into the header — silently replacing what the
  input asked for. The reported case: raw text declaring `Difficulty: medium`
  filed as `too-large` (score 11), unchanged when the full header block was
  prepended, hand-corrected after `--apply`.
- THE LESSON, which is why the rule moved: this was the THIRD instance of one
  family and a FOURTH was found while fixing it. (1) the Feature Agent's ranker
  — fixed 2026-08-10, PyAutoBrain#217, by adding a local `effective_difficulty`;
  (2) Intake's `Difficulty:`; (3) Intake's work-type classifier, which called the
  bug prompt for THIS bug `feature` while the difficulty leg was being written
  up; (4) the Bug Agent, sizing through raw `estimate_difficulty` and re-homing
  on prose keywords over a declared `Type: bug` — nobody had filed that one. One
  heuristic with N reconciliations is N chances to forget one, and two of the
  three forgot. Fixing #217 locally is what let (2)–(4) survive.
- length is a bad size proxy (recorded AGAIN, second time): the derived score
  weights prompt length, and a prompt is long when it carries a design and the
  sibling tasks' traps, not when the work is large. That inversion is already on
  the record in `feature-ranker-ignores-header-keys.md`; a declared `Difficulty:`
  is the documented escape hatch for it, and on the intake path it did nothing.
- TRAP, inherited and re-earned: the fenced-block skip is load-bearing, not
  tidiness — the bug prompt for this fix QUOTES `Difficulty:` header lines in a
  ```-block and in backticks, so a naive scan makes the bug report re-size
  itself. `declared_header` already skipped fences (the #217 trap); the new
  `declared_inline` masks fenced blocks AND inline code spans to spaces before
  matching, preserving offsets so the title-stripping stays aligned.
- second-order trap found by the tests: a declared value must not leak into the
  DERIVED TITLE. "Fix the docstring. Difficulty: large." titled the task after
  its own difficulty declaration and carried `large` into the slug — the
  filename. `strip_declarations` removes the clause for title derivation only;
  the prompt body stays verbatim (word-vomit is intent).
- a defect report legitimately says "refactor" and "documentation": that is why
  the Bug Agent's `re_home_check` now returns None for a declared `Type: bug`
  rather than weighing prose keywords against it. Note the sharp edge — the
  literal string "bug" in a `Type: bug` line trips the agent's own `defect`
  keyword hit, which masked the misbehaviour in a first draft of the test.
- verified on the live prompt: `intake classify --file` on this task's own prompt
  now reports `Work-type: bug (declared)` and `Difficulty: medium (declared;
  heuristic derived medium)`; before the fix it reported `feature` and re-sized.
  `pyauto-brain feature`/`bug` report the declared level with the derived one
  beside it.
- tests: `tests/test_declared_header_precedence.py` (15) is named for the FAMILY,
  not the instance — rule-level tests plus the reported reproduction, the
  prepended-header case, the title/slug leak, declared `Type:` at both intake and
  the Bug Agent's re-home check, and "no declaration -> still derives". The old
  per-instance test file written earlier in the session was dropped.
- gate note (`web-github`): PyAutoHeart is not among this session's repos, so the
  Heart leg could not run. `ship_library`'s documented fallback applied — the
  repo's own suite as the gate — and CI ran both pytest legs plus the tenant
  firewall on the PR.
- process note worth keeping: the session was launched with a prompt path that
  did not exist yet, wrote its own reconstruction of the prompt, and only later
  found the real one pushed to `main` (c1927d5). The real prompt scoped the work
  differently — it named `declared_header`, asked whether the rule belonged in
  the faculty, and asked for leg (2) in the same pass — and the reconstruction
  had reasoned the opposite way (per-conductor, faculty stays a pure estimator).
  The merge kept main's text and dropped the reconstruction. Read the filed
  prompt before designing; a plausible reconstruction of a task is not the task.
- scope: this branch is wider than one leg, deliberately, because the prompt asked
  for (2) in the same pass — one root cause, one shared rule; splitting would have
  meant two PRs editing the same function.

## Original prompt

# Intake discards a declared Difficulty and persists its own derived one

Type: bug
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: safe
Priority: normal
Status: formalised
Issued: 2026-08-24

@PyAutoBrain's Intake Agent never reads the `Difficulty:` a raw input declares.
`analyse()` hand-builds the prompt-shaped dict it hands the sizing faculty:

    agents/conductors/intake/_intake.py:268
        p = {"text": text, "repos": repos, "words": len(text.split()),
             "target": target, "work_type": work_type}
        level, score, factors = estimate_difficulty(p)

That dict omits `declared_header(text)`, which the file-loading path in
`agents/faculties/sizing/_sizing.py:369` does fold in. So `estimate_difficulty`
runs with no declared key present, nothing reconciles derived against declared,
and `_intake.py:320` then writes the derived level into the header — silently
replacing what the input asked for.

Reproduced 2026-08-24 while filing the arXiv-inbox-tier prompt: raw text
declaring `Difficulty: medium` classified as `too-large` (score 11), unchanged
when the full header block was prepended. The header had to be hand-corrected
after `--apply`.

This matters because the derived score weights prompt *length*. A prompt is long
when it carries a design and the sibling tasks' traps, not when the work is
large — the exact inversion `complete/2026/08/feature-ranker-ignores-header-keys.md`
already records ("length is a bad size proxy … that is what a declared
`Difficulty:` is for"). A declared key is the documented escape hatch, and on
this path it does nothing.

Third instance of one family — a conductor deriving from prose while ignoring a
declared header key:

1. the Feature Agent ranker — fixed, PyAutoBrain#217.
2. the Bug Agent classifying on prose keywords over a declared `Type: bug` —
   recorded in that same completion record and still unfiled.
3. this one.

Worth fixing (2) in the same pass, and considering whether the reconciliation
belongs in the sizing faculty itself — one place both conductors already call —
rather than being re-implemented per conductor. Decide the precedence rule
explicitly: declared wins, or declared wins with the derived score reported
alongside when they disagree (the latter keeps the heuristic honest and visible).

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from file:/tmp/claude-0/-home-user/09bebd08-3d0d-5ba1-8380-10185d92c0ca/scratchpad/sizing_bug.md -->

## Filing note (same session)

Intake classified *this* prompt as `feature`, from prose, despite the input
naming itself a bug throughout — so the work-type leg of the same family fired
while the difficulty leg was being written up. The file was re-homed to
`draft/bug/pyautobrain/` and its `Type:` corrected by hand. Two legs of one
conductor, one root cause: derive from prose, never look at what was declared.
