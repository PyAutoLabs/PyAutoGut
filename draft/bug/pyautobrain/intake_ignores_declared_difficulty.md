# Intake discards a declared Difficulty and persists its own derived one

Type: bug
Target: pyautobrain
Repos:
- PyAutoBrain
Difficulty: medium
Autonomy: safe
Priority: normal
Status: formalised

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
