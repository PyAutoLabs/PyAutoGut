## central-community-docs
- issue: https://github.com/PyAutoLabs/PyAutoScientist/issues/5
- completed: 2026-07-27
- primary-pr: https://github.com/PyAutoLabs/PyAutoScientist/pull/6
- workspace-prs: 22 coordinated PRs — https://github.com/PyAutoLabs/PyAutoScientist/issues/5#issuecomment-5094035448
- summary: PyAutoScientist became the canonical home for the PyAutoLabs Contributor Covenant 2.1 Code of Conduct and shared contribution guide. Fifteen Code of Conduct files and eighteen contribution files became uniform pointers; sixteen duplicated Markdown issue templates were removed so organization YAML forms are inherited. All 22 PRs merged after their reported CI checks passed.
- findings: The review faculty found one over-broad statement that every repository had both README.md and AGENTS.md; the canonical guide and pointers were corrected to say "where present" before shipping.
- merge-order: PyAutoScientist merged first and both canonical URLs returned HTTP 200 before any pointer PR merged.
- validation: Review faculty CLEAN; pointer hashes single-source; no legacy templates remained; all 22 merge states verified MERGED; final autolens_workspace_test smoke matrix passed 4/4.
- cleanup: `worktree_remove` skipped the hidden `.github` worktree in its shell glob, leaving stale worktree metadata; the path was already gone, so the metadata was pruned and the merged local branch deleted manually. The helper needs a follow-up fix for hidden repositories.
- follow-ups: A future AI_STATEMENT.md can use the same canonical-document plus pointer structure. SECURITY.md, SUPPORT.md, and GOVERNANCE.md remain future centralization candidates.

## Original prompt

# Centralise shared community and governance documents

Type: docs
Target: pyautoscientist
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Make @PyAutoScientist the canonical home for the PyAutoLabs-wide community and
governance documents that are currently duplicated across repositories.
Inventory all registered repositories before fixing the scope. Move the shared
`CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` content to PyAutoScientist, then keep
small repository-root pointer files at the conventional filenames so GitHub
and contributors can still discover the canonical documents. Identify any
other duplicated repository-level files that belong to this same remit, while
distinguishing genuinely shared policy from repository-specific instructions.

Design the central layout so a forthcoming shared AI statement can follow the
same canonical-document plus repository-pointer pattern. Do not draft the AI
statement as part of this task unless needed only to establish its location or
link structure.

## Inventory findings

- `PyAutoLabs/.github` already provides public organization-wide default
  `CODE_OF_CONDUCT.md` and `CONTRIBUTING.md` files, issue forms, and a pull
  request template. It should remain the GitHub-native distribution layer,
  with its two policy files reduced to pointers to the full canonical documents
  in @PyAutoScientist.
- Fourteen registered repositories have a local `CODE_OF_CONDUCT.md`, seventeen
  have a local `CONTRIBUTING.md`, and twenty repositories have at least one of
  the two. Replace those full local copies with short, uniform pointers. Repos
  with no local override will inherit the `.github` pointer automatically.
- Eight repositories carry the same legacy Markdown bug/feature issue
  templates, which suppress the newer organization-level YAML forms. Remove
  those local duplicates so the organization defaults take effect.
- Keep licenses and scientific citation files local. Record `SECURITY.md`,
  `SUPPORT.md`, and `GOVERNANCE.md` as future candidates for the same shared
  community-health architecture; none currently exists locally to migrate.
- The forthcoming `AI_STATEMENT.md` is not a GitHub-native default community
  file, so its later rollout will need explicit repository pointers or links
  from one of the inherited standard files.

## Original request

> The repos all share and duplicate CODE_OF_CONDUCT.md, CONTRIBUTING.md, can we move their up to PyAutoScientist and have each repo level on just direct to that? We will add an AI STATEMENT next which follows the same logic. Check if anything else falls in this remit
