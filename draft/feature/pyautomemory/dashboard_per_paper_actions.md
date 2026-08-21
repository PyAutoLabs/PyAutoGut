# Memory dashboard: per-paper browsing + one-tap read/intake actions

Type: feature
Target: pyautomemory
Repos:
- PyAutoMemory
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

Follow-up to the paper-management pipeline
(`complete/2026/08/paper-management-pipeline.md`, Memory #35/PR#37) and the
knowledge board (#32/PR#33). The dashboard at
https://pyautolabs.github.io/PyAutoMemory/ shows per-section waiting/read
counts only; the human wants to browse and act on the individual papers.

## Original request (verbatim)

> We did work on dashboards recently, the PyAutoMemory dashboard says how many
> papers need reading but does not provide an easy route to getting to their
> page to read them or go through the indviidual papers. There is a claude
> copy button but ideally it'd allow me to nevigate through them all, I guess
> each would have a claude copy button to say ive read them

> doesn't even need to be a claude copy button I could imagine a button which
> either says to intake it into memory or ive read it but i dont want it
> added?

## Agreed design (human chose: prefilled GitHub issues)

- `scripts/board.py` (html render): expand each reading-queue section into a
  collapsible per-paper list (`<details>` per section; 230 waiting papers must
  stay navigable, DONE papers stay out of the way or in a collapsed history).
- Each paper title links out: arXiv abstract page when the queue line carries
  ` — <arXiv id or URL>`, otherwise an arXiv title-search link.
- Two action buttons per paper, both **prefilled GitHub issue links**
  (`issues/new?title=…&body=…&labels=…`) so nothing changes state until the
  human taps Submit on GitHub (human-gated, works from phone, no secrets in
  the static page):
  - **"Read — don't file"** → issue labelled for a small new Action in
    PyAutoMemory that mechanically prefixes the queue line with
    `DONE <YYYY-MM-DD> — `, commits, closes the issue.
  - **"Intake into memory"** → issue stays open as the filing work item
    (bibliography entry + wiki stub is agent work; claude-action wiring can
    come later).
- Markdown render (`_site/dashboard.md`) grows the same per-paper links in
  plain form.
- Constraints: board.py stays stdlib-only and fully local-parse; contents
  privacy pin is titles/counts only (already satisfied — titles are pinned as
  allowed); `validate_structure.py` bans committed `.html`; the issue-label
  Action must respect the never-rewrite-history and explicit-path-staging
  rules; board.py travels into spawn templates, so it must keep deriving repo
  identity from the checkout/git remote (issue-link URLs included).
