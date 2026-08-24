# Intake ignores a difficulty declared in the raw text

Type: bug
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised
Issued: 2026-08-24

The Intake Agent sizes every idea with the shared sizing heuristic and writes
that estimate into the prompt's `Difficulty:` header — even when the human who
wrote the raw text already said how hard the work is. A human declaration is
strictly better evidence than the keyword heuristic (the human knows the scope;
the heuristic only sees words), so it should win.

Reproduce:

```
bin/pyauto-brain intake "Fix the typo in the autoarray docstring for Mask2D. Difficulty: large. Autonomy: supervised."
```

Observed: `Difficulty: small (score 0)`, `Autonomy: safe` — the declaration is
dropped silently. Worse, the declaration text is swallowed by the title
(`Fix the typo in the autoarray docstring for Mask2D. Difficulty: large`) and so
leaks into the generated slug/filename.

This matters most for the `ideas.md` sweep, where the house style is to end a
bullet with e.g. `Difficulty large, supervised.` (see `ideas.md` line 31) —
exactly the entries where the human has already thought about scope.

Wanted:

- Parse a difficulty declared in the raw text (`Difficulty: large`,
  `difficulty large`, `Difficulty large, supervised.`) and let it override the
  heuristic estimate, with the IntakeDecision showing that it was human-declared
  rather than estimated.
- Same for a declared `Autonomy:` / `Priority:` where present, so the header the
  human wrote is not silently rewritten.
- Strip the declaration from the derived title/slug so it stops polluting the
  filename.
- The sizing faculty stays the estimator; the override belongs to the caller
  that owns the header (intake), not to `estimate_difficulty` itself.
