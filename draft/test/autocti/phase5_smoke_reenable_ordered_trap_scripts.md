# Re-enable autocti_workspace smoke coverage of the ordered-trap modeling scripts

Type: test
Target: autocti_workspace
Repos:
- @autocti_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Epic: CTI resurrection — Phase 5

Re-homed from `draft/test/autofit/` by the filing session. Intake set
`Target: PyAutoFit` and listed PyAutoFit as an affected repo — wrong on both:
the PyAutoFit fix has already merged (438f56fac), so this task changes no
library source and only needs a PyAutoFit main that contains it. Difficulty
lowered from `large`: the work is verify-scripts-run, add lines to
`smoke_tests.txt`, and time them against the gate cap — sized by script count,
which is not yet known, hence `medium` rather than `small`.

Re-enable @autocti_workspace smoke coverage of the modeling/start_here.py-class scripts, unblocked by PyAutoFit#1520 (merged 438f56fac). Those scripts were un-smokeable at PYAUTO_TEST_MODE=2 because ordered trap models tie at the prior medians and the bypass hard-failed; the bypass now selects a deterministic assertion-valid point, at TEST_MODE 2 and 3. This is CTI resurrection epic Phase 5. Work: confirm the scripts now run bypassed against a PyAutoFit main that includes 438f56fac, add them back to the workspace smoke_tests.txt, and check timings against the smoke gate cap before adding them.

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from user-intake -->
