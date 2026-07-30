wiki-currency paired-PR support: cited sources match the PR branch.

- issue: PyAutoLabs/autolens_assistant#103 (left open for human close)
- prs: autolens_assistant#104, autofit_assistant#28, autocti_assistant#19 — merged
- one generic step after the citation clones: on pull_request events, any sources/
  repo carrying a branch matching the PR's head branch is fetched + checked out
  (sparse clones keep their cone). workflow_call/dispatch (release-time) unchanged —
  still grade against main/tags. The fleet's matching-branch convention (smoke chain,
  navigator); merge-order discipline stays human, same trade-off as the Brain-ref
  hatch (PyAutoBrain#186). This closes the last expected-red cross-repo CI gate.

## Original prompt

# wiki-currency: matching-branch checkout for citation ground truth

Type: maintenance
Target: autolens_assistant
Repos:
- autolens_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued — https://github.com/PyAutoLabs/autolens_assistant/issues/103

The --check-citations merge-order gate reds paired PRs; adopt the fleet's
matching-branch checkout convention for the sources/ clones on pull_request
events only. Filed from the 2026-07-30 CI/release audit follow-on assessment.
