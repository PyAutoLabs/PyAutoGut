- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/48 (auto-closed on merge)
- shipped: 2026-08-21 — PyAutoMemory PR https://github.com/PyAutoLabs/PyAutoMemory/pull/49
  (merge 9d0e14ec) + PyAutoMind 68bc7051 (spawn DROP).
- classification: feature (PyAutoMemory) — item 4 of the four human-approved dashboard
  follow-ups; completes the paper-management loop: tap → notes → submit → filing PR.
- summary: `.github/workflows/queue_filing.yml` wires claude-code-action@v1 to the
  dashboard's 📥 queue-intake / 📑 queue-cite issues. Trigger `labeled` ONLY (fires
  for creation-applied labels too — an opened+labeled pair would double-run);
  author-association gate as in queue_actions.yml. Claude gets workspace-edit tools
  + arXiv-scoped WebFetch, no git/gh; it adds the canonical bib entry, writes the
  sources section (cite = minimal key+notes, intake = full stub), DONE-marks the
  queue line, or writes /tmp/filing_error.txt and aborts cleanly (reason posted to
  the issue). Deterministic steps then gate (make validate + pytest), stage explicit
  paths only, push queue-filing/issue-<n>, open a PR that closes the issue. Merge
  stays human.
- LIVE + VALIDATED 2026-08-21: human minted a fresh `claude setup-token` OAuth
  token into the Memory repo secrets, then a real 📑 cite round-trip on Memory#50
  (Morgan et al. 2026, arXiv:2608.17041) took three runs, each fixed by a
  corrective PR: #51 (runner ships no pytest — install it), #52
  (claude-code-action rewires checkout git credentials for its own OIDC token —
  push via explicit x-access-token URL with the job token), #54 (org policy
  "Actions may not create PRs" blocked gh pr create — degrade to a one-tap
  compare-link comment). Run 3 filed/gated/pushed green; the filing PR (#53) was
  opened by hand and left for human review. Filing quality was high: correct
  BibTeX, right sources page, accurate minimal claim.
- traps:
  - GITHUB_TOKEN-created filing PRs never trigger validate.yml — the gates must run
    inside the filing workflow before push (they do).
  - gh in pre-checkout steps needs GH_REPO env for repo context.
  - PyAutoLabs org has "Allow GitHub Actions to create and approve pull requests"
    OFF; repo-level PUT silently no-ops under it, and flipping the org toggle
    needs admin:org scope the local gh token lacks — until a human enables it
    (org Settings → Actions → General, then repo), filing ends at the
    compare-link comment.
- affected-repos:
  - PyAutoMemory

## Original prompt

# Memory queue: claude-action filing of intake/cite issues

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

Item 4 of the human-approved dashboard follow-ups ("ok do all 4",
2026-08-21; items 1-3 = #46/PR#47). Today a 📥 `queue-intake` / 📑
`queue-cite` issue from the dashboard waits for a Claude Code session. Wire
`anthropics/claude-code-action@v1` so the filing happens in CI and arrives
as a reviewable PR: tap → notes → submit → PR.

Design (mirror the org pattern in PyAutoMind `arxiv_papers.yml` /
`morning_status.yml`):

- New `.github/workflows/queue_filing.yml`, trigger `issues: [opened,
  labeled]`, gated on label ∈ {queue-intake, queue-cite} AND actor
  association ∈ OWNER/MEMBER/COLLABORATOR (public repo — same gate as
  queue_actions.yml).
- claude-code-action@v1 with `claude_code_oauth_token:
  secrets.CLAUDE_CODE_OAUTH_TOKEN`, `id-token: write` (OIDC), checkout
  load-bearing, `show_full_output: true`, allowed tools scoped to
  workspace edits (Read/Edit/Write + Bash for `make validate`). Claude
  edits files ONLY; deterministic workflow steps then stage the expected
  paths (`bibliography/`, `wiki/`, `reading-queue.md` — explicit, never
  add -A), run `make validate` + `pytest tests/` as a hard gate, push a
  `queue-filing/issue-<n>` branch, and open a PR that references and
  will close the issue. Merge stays human.
- Prompt contract: parse section/line/notes from the issue body;
  `queue-cite` → canonical bib entry + minimal sources section (key +
  notes, nothing deeper); `queue-intake` → bib entry + full stub per
  wiki/CLAUDE.md, folding the notes in; mark the queue line
  `DONE <date> — `; never touch anything else.
- **Human prerequisite:** add the `CLAUDE_CODE_OAUTH_TOKEN` secret to
  PyAutoMemory (it exists only as a PyAutoMind repo secret; values are
  unreadable so it cannot be copied programmatically). The workflow must
  fail with a clear message when the secret is absent.
- Spawn template: explicit DROP for the new workflow in
  PyAutoMind/scripts/spawn.py + spawn_spec.md rule 8 (no `.github/**`
  catch-all).
