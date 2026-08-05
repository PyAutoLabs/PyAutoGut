# Bug in the workspace smoke runners: the notebook leg aborts

Type: bug
Target: workspaces
Repos:
- autofit_workspace
- autogalaxy_workspace
- autolens_workspace
- workspaces
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Bug in the workspace smoke runners: the notebook leg aborts the whole run when jupyter is missing. In autofit_workspace, autogalaxy_workspace and autolens_workspace, .github/scripts/run_smoke.py execute_notebook calls subprocess.run with a bare 'jupyter' argv and no FileNotFoundError guard, so on a machine without jupyter the exception escapes main(): the run dies with a raw traceback, prints no === Smoke test summary === line, and every remaining entry is silently uncovered. The script leg is unaffected because it invokes sys.executable, which always exists. CI never sees this because the runner images always have jupyter, so the gap only bites a local developer sweep — where it looks like a crash rather than a missing optional tool, and quietly discards coverage. Observed on 2026-08-05 running the runner locally in all three workspaces. Fix by catching FileNotFoundError in execute_notebook and returning a clear per-entry failure or skip, so the runner keeps its documented contract of continuing through failures and always ending with the summary line. The same file is duplicated across nine repos but only these three run the notebook leg.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
