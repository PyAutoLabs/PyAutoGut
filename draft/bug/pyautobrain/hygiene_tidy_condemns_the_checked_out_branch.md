# Hygiene tidy condemns the checked-out branch, and refs crashes on

Type: bug
Target: PyAutoBrain
Repos:
- PyAutoBrain
Difficulty: small
Autonomy: safe
Priority: high
Status: formalised

Hygiene tidy condemns the checked-out branch, and refs crashes on a missing root. Two guard bugs in the hygiene conductor's scans (PyAutoBrain agents/conductors/hygiene). First: enumerate_condemn_candidates (hygiene.sh:428) and prescan_tidy (hygiene.sh:127) filter only the literal names main, master, HEAD and the default branch; neither excludes the branch HEAD actually points at. A freshly cut agent branch is an ancestor of origin/main until its first commit, so it always reads merged=yes and is reported as 'recommend straight delete'. Every agent session hits this, and the tidy path files condemned entries async with no per-item gate. Fix: exclude git symbolic-ref --short HEAD in both places. Second: _hygiene_refs.py:348 calls root.iterdir() unguarded, raising FileNotFoundError with a full traceback when PYAUTO_ROOT does not exist, where the extras and config modes degrade gracefully to a 'not scannable here' row; in the default all-mode scan the traceback prints twice. Fix: guard the root and emit the same graceful row. Add regression tests to tests/test_hygiene_conductor.py.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
