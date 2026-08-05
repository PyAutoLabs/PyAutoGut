# Bug: the health conductor mis-reports a STALE verdict as UNKNOWN.

Type: bug
Target: PyAutoBrain
Repos:
- PyAutoBrain
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

Bug: the health conductor mis-reports a STALE verdict as UNKNOWN. In PyAutoBrain agents/conductors/health/health.sh the recommendation chain branches on green / blockers / real-warnings / (gaps or yellow) and otherwise falls through to an UNKNOWN branch, and _exit_code_for maps only green/yellow/red with a catch-all 4. When PyAutoHeart returns STALE the card correctly prints 'adopted verdict = stale' with a score, then the recommendation incorrectly prints 'UNKNOWN - could not obtain a verdict from the vitals faculty' and the script exits 4. The triage item classifier only walks the red and yellow reason lists, so stale reasons are dropped and the counts wrongly read 0 blockers / 0 warnings / 0 gaps. PyAutoHeart AGENTS.md makes STALE a first-class freshness tier that the dev-ship gate treats as passing, so a caller cannot distinguish 'Heart says STALE' from 'Heart unreachable'. Reproduced on a live health run 2026-08-05.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
