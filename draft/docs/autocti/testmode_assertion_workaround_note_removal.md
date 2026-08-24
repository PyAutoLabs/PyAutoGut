# Delete the TEST_MODE ordered-assertion workaround note from @autocti_workspace AGENTS.md

Type: docs
Target: autocti_workspace
Repos:
- @autocti_workspace
- @autocti_workspace_test
- @autocti_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24

Re-homed from `draft/triage/` by the filing session: intake classified this
`triage` / `Target: PyAutoFit` / `too-large` on low confidence, which is wrong on
all three counts — the PyAutoFit fix has already shipped, so nothing here touches
library source. This is a prose deletion across up to three workspace repos.

Delete the TEST_MODE ordered-assertion workaround note from @autocti_workspace AGENTS.md. PyAutoFit#1520 (merged 438f56fac, 2026-08-24) fixed the bypass so a model with identical priors plus an ordering assertion no longer ties at the prior medians — the bypass now picks a deterministic assertion-valid point via _test_mode_valid_parameter_vector, at TEST_MODE 2 and 3. The workspace AGENTS.md documents the crash as a live artifact and tells readers to work around it; that text is now wrong. Delete the note rather than update it — the testmode-env-drift precedent is delete the trap, do not document it. Verify the note's exact wording and location in autocti_workspace first; if a sibling note exists in autocti_workspace_test or autocti_assistant, remove those too.

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from user-intake -->
