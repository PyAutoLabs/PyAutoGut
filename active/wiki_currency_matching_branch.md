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
