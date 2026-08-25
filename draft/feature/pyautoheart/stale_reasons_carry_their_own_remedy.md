# A STALE board gives you nothing to copy: every evidence gap should carry its own remedy

Type: feature
Target: pyautoheart
Repos:
- @PyAutoHeart
- @PyAutoBrain
Difficulty: small
Autonomy: supervised
Priority: normal
Status: SHIPPED 2026-08-25 (branch `claude/pyautoheart-stale-r4swxg` in
        @PyAutoHeart + @PyAutoBrain) — pending issue/PR close-out
Filed: 2026-08-25

## What shipped

Both legs, built directly from this prompt on the branch above:

- **@PyAutoHeart** — `readiness.compute` emits `stale_details` (each stale
  reason with the gate key that produced it; the flat lists, verdict, score and
  release gate untouched). `dashboard.py` keys `STALE_REMEDIES` off that: a
  stale row gains `command` (⌨ chip on html, fenced line in md, `command` in
  json), a prompt that names the check AND the gap, and the tier gains
  `stale_plan` — one prompt walking every gap, plus the shell chain when every
  gap has a command (withheld when one needs a rehearsal). `pyauto-heart fix
  stale` is the terminal door; `readiness` points at it; json → schema v3.
- **@PyAutoBrain** — `board/_board.py` forwards each gap's `command` and
  renders the plan verbatim: a 📋 row with the prompt, a ⌨ row with the chain,
  one digest line for the tier.

Two deviations from the spec below, both deliberate:

- The README strip stays one line for STALE — `test_md_brief_is_one_line_unless_something_is_wrong`
  pins that on purpose, and a glance surface is the wrong place for a plan.
- `skew_pypi_unknown` carries a prompt but no command: the deep PyPI leg has no
  `pyauto-heart` verb, and inventing one here would have been a fake remedy.

## The spec it was built from

## The complaint

The Heart board's whole promise is the one in its own lede — "📋 copies a
ready-to-paste prompt or command for a Claude Code chat". That holds for RED
and YELLOW: a blocker row carries a `/bug Heart board: <text> — failing run:
<url>` prompt, and a section row can carry a real command (`pyauto-heart fix
drift`, `pyauto-heart fix timing <project>`). It does **not** hold for STALE.
Every evidence gap gets the same generic string from `_reason_item()`
(`heart/dashboard.py:1031`):

    /health re-run the stale evidence: install verification not run

That names the gap the human just read and stops. It contains no command, no
repo, no artifact path, no next step — copying it just hands the sentence back
to a Claude session that then has to work out the remedy from scratch. A reason
row has no command chip at all, on any surface; commands exist only on section
rows. So on a STALE morning there is nothing on the board to copy that actually
closes the gap.

This matters more than a RED chip would, because STALE is the board's steady
state: the cloud verdict has been `STALE · score 65` on every `heart-health.yml`
run since 2026-08-19 (alternating only with a transient `RED · 45` when a repo's
CI goes red), with exactly three gaps, all of which have a known remedy nobody
can copy:

| stale reason | gate key | weight | remedy today (undiscoverable) |
|---|---|---|---|
| `install verification not run` | `install_unknown` | 10 | `pyauto-heart verify_install --report-json` then `pyauto-heart tick` |
| `test run status unknown (no report.json)` | `test_unknown` | 10 | a workspace validation run (Hands `run_logs/latest/report.json`) then `pyauto-heart tick` |
| `no release validation for current source` | `validation_absent` | 15 | `/release rehearse`, then `pyauto-heart validate --ingest <artifacts>` |

## What to build

Give every stale reason a **remedy of its own** — a copyable command where one
exists, and a targeted prompt where it does not — keyed by the readiness gate
key, never sniffed out of the reason string.

STALE's rule holds throughout: a remedy **re-runs a check, it never fixes
code**. Nothing here may emit a `/bug` door for a stale reason.

1. **Carry the key out of readiness.** `heart/readiness.py` already knows the
   identity of each gap — it calls `hit("install_unknown")` beside every
   `stale.append(...)` (and `scope_local(msg, key)` does both at
   `readiness.py:263`). Emit it: an additive `reason_details` list of
   `{text, severity, key}` alongside the existing flat `red_reasons` /
   `yellow_reasons` / `stale_reasons`. The flat lists and the verdict/score
   contract stay byte-for-byte unchanged, so every existing consumer — and an
   older Heart's persisted `release_ready.json` — behaves exactly as before.

2. **A remedy table in the dashboard**, keyed by that key, covering the gate
   keys that actually occur (`install_unknown`, `install_stale`,
   `install_non_release`, `test_unknown`, `test_stale`, `validation_absent`,
   `validation_stale`, `validation_stale_sha`, `validation_profile`,
   `validation_unknown`, `lib_unknown`, `lib_ci_unavailable`, `skew_unknown`).
   Each entry is `{command, prompt}`; `command` may be `None` when the remedy is
   genuinely a conversation (e.g. a rehearsal that needs a human's go-ahead),
   and then the prompt must still be specific — `/release rehearse` for the
   validation family, not `/health re-run the stale evidence: …`.

3. **Fall back, never guess.** A reason that arrives without a key (an older
   snapshot) keeps today's generic prompt. No string matching on reason text.

4. **Render it on every surface**, each in its own idiom, all from the same
   structured item:
   - `--html`: the reason row gains a command chip beside the existing prompt
     📋 (two payloads, distinct titles — "copy the command" / "copy the fix
     prompt"), so the Evidence-gaps block is finally actionable.
   - `--md`: the collapsed `📋 fix prompts` block gains the command as its own
     fenced line per gap (GitHub's copy button makes it one-tap).
   - `--json`: `blockers[]` gains `command` (additive; bump `schema_version`).
   - `--oneline`: unchanged.
   - README strip (`_render_md_brief`): today it deliberately prints no reasons
     for STALE. Reconsider *only* to the extent of one line naming the gap count
     and the single highest-value command; if that reads as noise on a glance
     surface, leave it alone and say so in the PR.

5. **A CLI door to match**, in the same family as the existing topics:
   `pyauto-heart fix stale` — read the persisted verdict and print each current
   gap with its command and prompt. This is what a terminal-first morning
   copies, and it keeps `heart/fix.py`'s "bundle context, emit a command"
   contract (it must not mutate anything).

6. **Brain leg (PyAutoBrain).** `board/_board.py:245 extract_heart_blockers()`
   forwards a fixed key set; add `command` and render it as a second chip in the
   Readiness & release rows. Same invariant as today — the Brain renders what
   the Heart sends and never re-derives a remedy.

## Acceptance

- On a board whose only reasons are the three gaps above, each Evidence-gaps row
  offers a command that, run on the dev box, clears that row on the next tick.
- `pyauto-heart fix stale` prints the same commands the board shows, from the
  same verdict — the two surfaces cannot disagree.
- `--json` blockers carry `command`; the Brain board renders it verbatim.
- No stale reason anywhere emits a `/bug` prompt.
- Verdict, score, `red_reasons` / `yellow_reasons` / `stale_reasons` and the
  release gate are unchanged: `tests/test_readiness.py` passes untouched, and
  new coverage lands in `tests/test_dashboard.py` (remedy per key, fallback for
  a keyless reason, json/md/html rendering).

## Out of scope

What counts as stale, the weights, the profiles, and the GREEN-for-release gate.
This prompt is about the *hand* the board offers once a gap exists, not about
which gaps exist.
