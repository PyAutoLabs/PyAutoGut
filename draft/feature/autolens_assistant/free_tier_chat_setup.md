# Claude Development Prompt: Free-Tier Conversational AI Support for autolens_assistant

Type: feature
Target: autolens_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

Make the PyAutoLens Assistant usable from **free-tier browser chat** (claude.ai Free,
ChatGPT Free) — no paid subscription, no code execution, possibly no repo access.
This prompt contains the full research (2026-08-01) and the implementation plan.
Research was done in a prior session; this file is the durable record.

## Why the first attempt failed

The first attempt (Claude free) failed on GitHub repo connection and on reading
`llms.txt`. Root causes found in the repo itself:

1. `llms.txt:7` tells connector-less users to give up: *"without one it can't, so
   use a local coding agent instead."*
2. The bootstrap prompt in `llms.txt:9-17` points at the **`blob/` HTML URL**, not
   `raw.githubusercontent.com` — chat web-fetch gets a JS-gated GitHub page shell.
3. Every onward link in `llms.txt` / `AGENTS.md` / `skills/README.md` is
   **relative** — unfollowable even when the raw file is fetched.
4. Claude's consumer web-fetch only fetches URLs the user pasted or that appeared
   in search results; raw links discovered inside a fetched file fail with a
   permissions error.
5. Timing: **Anthropic moved connectors (incl. GitHub), custom skills, and memory
   to the Free plan in Feb–Mar 2026.** An attempt before then genuinely had no
   connector; a retry today should work once the user enables the GitHub connector.

## Platform capability research (as of 2026-08-01)

### claude.ai Free

| Capability | Free-plan status |
|---|---|
| GitHub connector | **Yes** (all plans since ~Feb 2026); custom remote-MCP connectors: 1 allowed |
| Projects | Yes, max 5; knowledge ~200K tokens, **full-context only (RAG mode is paid)** |
| Project sharing | **No** — Team/Enterprise only; each free user self-assembles |
| Web search + URL fetch | Yes; user-pasted raw URLs fetch, indirect raw links fail |
| Custom skills (zip upload) | Yes (Free since Feb 2026), private per-account |
| Custom instructions / styles / memory | Yes (memory free since 2026-03) |
| Published AI-powered artifacts | Yes — viewable by anyone; AI features bill the **viewer's** free account |
| Limits | 200K context; ~15–40 msgs / 5 h (load-dependent); Sonnet-tier model |

### ChatGPT Free

| Capability | Free-plan status |
|---|---|
| Use custom GPTs | **Yes** (creation/publishing requires Plus/Pro + verified builder profile) |
| GPT knowledge | 20 files, 512 MB / 2M tokens each; **RAG-chunked retrieval, not full context** |
| GPT Actions | Work for free users running the GPT (privacy-policy URL required to publish) |
| Connectors (incl. GitHub) | **No** — paid plans only |
| Projects | Yes (5 files/project) but per-account, not shareable |
| Browsing | Yes; raw URLs mostly OK, blob pages flaky/intermittent |
| Custom instructions / memory | Yes (1,500 chars; lightweight memory) |
| Limits | ~16K context for free (sources conflict); ~10 flagship msgs / 5 h then mini-model fallback |

Note: enterprise custom GPTs are on a deprecation path (Workspace Agents,
Apr 2026); consumer Plus-built GPTs + GPT Store remain supported — monitor.

## Content inventory (measured, ~4 chars/token)

- `AGENTS.md` 15.4 KB (~3.8k tok); `skills/` 47 files, 334 KB; 36 `al_*` skills
  = 234 KB (~58k tok), **12 of them stubs** with little API content;
  `wiki/core` 229 KB (~57k tok, of which `api/` 47.5 KB ≈ 12k tok is the real
  symbol catalogue); `wiki/literature` 915 KB (76% is the `.bib`) — exclude from
  any chat pack; `wiki/euclid` + `euclid_*` skills ~82 KB — separable module.
- Measured candidate packs:
  - **Pack C (pasteable floor)**: `AGENTS.md` + `skills/README.md` + `_style.md`
    + `wiki/core/index.md` + `wiki/core/api/*` = **~25k tokens**.
  - **Pack D (functional floor)**: C + 14 non-stub workhorse `al_*` skills =
    **~50k tokens** — fits a free Claude Project or GPT knowledge easily.
  - **Pack A (everything relevant)**: AGENTS + all `al_*` + all `wiki/core` =
    **~122k tokens** — upload-only (fits free Claude Project 200K; too big to paste).
- **No generated API-surface file exists.** `wiki/core/api_audit_baseline.json`
  holds only hashes + symbol counts (~655 public symbols across the stack, pinned
  `2026.7.29.2`). `autoassistant/audit_skill_apis.py` already enumerates the live
  surface via `dir()` — it just never emits names. No bundling/concat tooling
  exists (Makefile: `validate-literature-citations`, `audit`, `test` only).
- Precedent to copy: `autolens_workspace/llms.txt:1` — *"If your AI can't browse
  GitHub, paste this entire file into the chat as context."* (8 KB, ~2k tok).

## What breaks in a no-execution, no-repo chat (must be fixed or stripped)

- `AGENTS.md` instructions that are un-runnable in chat: session-start
  `audit_skill_apis.py --check-version` (:18-25); the code-gate fallback is
  itself a shell command (:43-49); `.maintainer` / `profile.md` reads and writes;
  the whole commit-cadence section; `sources/` clone-on-demand; skill symlinking.
- Maintenance/execution skills (~85 KB: `start-new-project`, `al_setup_environment`,
  `al_audit_skill_apis`, `al_update_wiki`, `contribute-upstream`, …) — exclude
  from any chat pack.
- 44 symlinks under `.claude/skills/` become 20-byte phantom files in any zip —
  dereference or exclude.
- Misleading content a chat will repeat: `README.md` points at
  `dataset/cosmos_web_ring` (actual: `dataset/imaging/cosmos_web_ring`);
  `wiki/core/external/workspace.md` advertises a `workspace_index.json` that does
  not exist in the workspace checkout.
- Keep verbatim (already chat-correct): engage-first posture (`llms.txt:19`),
  the functional-plot-API rule with the removed-symbol list (`AGENTS.md:214-227`),
  the real-data gate's no-execution branch (`AGENTS.md:38-41`), the three
  standard imports, the "never reconstruct from memory" rule (:197-205).

## Recommended setup

### Claude Free (primary: connector; fallback: paste/Project)

1. **Connector path (now free):** user enables the GitHub connector → creates a
   Project (free, 5 allowed) → pastes a short provided instruction block →
   attaches the repo. Fixes the original failure directly.
2. **No-connector fallback:** download the generated knowledge pack (Pack D/A)
   and drop it into a Project (200K budget, full-context on free), or paste the
   ~25k-token Pack C bundle into a chat.
3. **Optional:** packaged Claude skill zip (`SKILL.md` + pack) users upload under
   Settings → Skills (free); a published AI-powered artifact as a zero-setup demo
   surface (runs on the viewer's free account).

### ChatGPT Free (primary: custom GPT; fallback: paste)

1. **Custom GPT** built once on the maintainer's paid account, shared by link /
   GPT Store — the only first-class distribution channel to free users.
   - Instructions: distilled chat-mode rules (never-from-memory, functional plot
     API + removed symbols, real-data gate chat branch, engage-first, handoff-to-
     CLI-agent guidance).
   - Knowledge: the generated pack, structured for **chunked RAG** — one topic per
     distinctive heading, a dedicated current-API-surface file, ≤20 files.
   - Optional Action against `raw.githubusercontent.com` (GitHub contents API) for
     freshness; works for free users; needs a privacy-policy URL.
2. **Fallback:** same pasteable Pack C + a bootstrap prompt using **raw** URLs.

## Implementation tasks (for the Opus session)

1. **`make chat-bundle` generator** (new script, e.g.
   `autoassistant/chat_bundle.py`): emit (a) `llms-chat.txt` — the pasteable
   ~25k-token Pack C bundle, links inlined or rewritten to absolute raw URLs,
   pinned stack version stamped in the header; (b) a knowledge-pack directory
   (Pack D/A as a handful of concatenated topic files) for Claude Projects / GPT
   knowledge; dereference symlinks, exclude maintenance skills + `wiki/literature`.
2. **`audit_skill_apis.py --dump-symbols`**: emit the ~655-symbol current API
   surface as markdown; include it in the bundle so API currency is generated,
   not prose-maintained.
3. **Rewrite `llms.txt`** as a harness router: line 1 = the workspace's "paste
   this entire file" affordance; per-harness paths (Claude free/paid connector,
   ChatGPT GPT link, no-access paste fallback, CLI agents); all URLs absolute
   `raw.githubusercontent.com`; drop the "without a connector, give up" sentence.
4. **Chat-mode AGENTS variant** (generated section or `AGENTS_CHAT.md`): strip
   un-runnable instructions, keep the four chat-correct rules verbatim, state the
   pinned stack version explicitly.
5. **Build + publish the custom GPT** (manual, maintainer paid account) and a
   `FREE_TIER_SETUP.md` (or README section) with per-platform onboarding steps;
   replace the README cost table's CLI-only framing with a chat-tier matrix.
6. **Small fixes:** README dataset path (`dataset/imaging/cosmos_web_ring`);
   remove/repair the `workspace_index.json` claim in `wiki/core/external/`.
7. **QA:** extend `modes/maintainer.md` chat-surface smoke test (it already has a
   "ChatGPT without GitHub access" row) to cover: Claude free + connector, Claude
   free Project upload, pasted `llms-chat.txt`, and the GPT.

Caveats to carry into docs: free quotas are load-dependent and unpublished;
consumer URL-fetch policy is anecdotal; plan features change fast (Feb–Mar 2026
free-tier expansion is what made the Claude path viable) — describe observed
behaviour, don't promise plan features (per `modes/maintainer.md:121-125`).
