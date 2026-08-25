- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/57
- shipped: 2026-08-24 — PyAutoMemory main 0e4e551 + 7b94805, PyAutoMind main ff93809.
  Pushed straight to main at the human's direction ("straight to main too"), so there
  is no PR for either leg.
- classification: feature (PyAutoMemory + PyAutoMind) — fourth in the paper-management
  line after #35 (structured queue + arXiv ingest), #42 (per-paper board actions) and
  #48 (claude-action filing of intake/cite issues).
- summary: the nightly strong-lensing digest no longer ends in a Slack paste-block the
  human must copy into a session. Its survivors are appended to a new PyAutoMemory
  `arxiv-inbox.md`, the knowledge board renders them above the reading queue with a
  days-left column and four one-tap actions (➕ add to queue, 📥 intake, 📑 cite,
  ✖️ dismiss), and un-acted lines lapse after seven days. `scripts/inbox_actions.py`
  is the single owner of the line format, the window and all four transitions — neither
  board.py nor any workflow's shell re-expresses them, and the Mind digest runs that
  script inside a PyAutoMemory checkout rather than writing the format itself.
- the deliberate reversal: #35 built the digest so it NEVER commits — ingest was
  human-gated by the paste step. This reverses that on purpose. The gate moved from
  "paste the block into a session" to "tap a button on the board"; it did not go away,
  since nothing reaches reading-queue.md without a tap. Recorded here and in the
  workflow comment so a later reader does not read it as drift.
- lapse semantics (decided): a lapsed line is DELETED, not DONE-marked. Memory's
  never-delete rule protects *reading history*, and an un-acted suggestion is not
  history — git holds it either way. `## Lapsed` was the conservative alternative and
  was rejected as clutter.
- traps:
  - a prefilled `issues/new?…&labels=x` URL SILENTLY DROPS `x` when the label does not
    exist, and queue_actions.yml gates on the label — so a tapped button on a missing
    label looks like it worked and does nothing. Already recorded from #42, hit again
    here. Fixed structurally rather than by hand: knowledge_board.yml now ensures all
    five labels on every render (`gh api`, not `gh label create`, so it does not depend
    on the runner's gh version; 422 already-exists is the normal path). The board
    renders the buttons, so the board guarantees their labels.
  - knowledge_board.yml's `on: push` paths filter does not list the workflow file
    itself, so a workflow-only commit does NOT trigger it. The label step therefore did
    not run on its own push and needed a manual dispatch — worth knowing before
    assuming a board change is live.
  - `export UK_DATE` in the fetch step is scoped to that step's shell and is NOT
    visible to later steps; the inbox step reads uk_date from arxiv_papers.json instead.
  - PyAutoMind's `PAT_PYAUTOLABS` already existed (spawn_drift.yml) — the cross-repo
    write needed no new secret. The plain GITHUB_TOKEN cannot reach another repo.
  - spawn.py has no root-file catch-all: `arxiv-inbox.md` needed an explicit EMPTY rule
    (+ an EMPTY_TITLES entry) or the spawn run fails on an unmatched file. scripts/* and
    tests/* are already KEEP, so inbox_actions.py and its tests ship without a rule.
- design notes worth keeping:
  - every action URL now emits `file:`, including the reading-queue ones, so the
    workflows never guess which file a tap refers to. The older scripts ignore the
    extra key, so this was backward-compatible.
  - queue_actions.yml decides whether to commit from `git status --porcelain` on the two
    files rather than from a status token, so a script that dies before printing cannot
    mis-close the issue.
  - the inbox step runs AFTER the Slack POST on purpose: the digest is the product, the
    inbox is a convenience on top of it, and a cross-repo auth or push failure must
    never cost the morning's post. Expected-absent preconditions warn and exit 0; a
    genuinely broken script still fails the step.
- validation: 69 PyAutoMemory tests (35 new) + make validate green; 186 PyAutoMind tests
  green; spawn.py dry-run reports PyAutoMemory-template unmatched: none, canary clean.
  Rehearsed end to end against a real PyAutoMemory clone with today's two survivors:
  append → board renders 7d-left rows → re-run adds nothing → sweep drops both on day
  eight. The knowledge_board.yml dispatch ran green and created queue-add/queue-dismiss.
  NOT yet proven live: the digest's own inbox step first runs on the 2026-08-25 02:00
  UTC cron, and no button has been tapped yet.
- pre-existing, untouched: PyAutoMind's spawn_drift was ALREADY failing on main before
  this task (2026-08-24 07:19 scheduled run) on three unmatched Mind-template files —
  .github/workflows/firewall_gate.yml, .github/workflows/pages_dashboard.yml and
  dashboard.html. Unrelated to this change and still open.
- affected-repos:
  - PyAutoMemory
  - PyAutoMind
