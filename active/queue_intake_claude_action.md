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
