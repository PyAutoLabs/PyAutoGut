# llms.txt census fixes — routing drift, navigator group order, cross-repo signposts

Shipped 2026-08-01 (issue autolens_workspace#451). A census of the llms.txt layer ahead of the
assistant paper release found the generated catalogues fully in sync (zero-diff regeneration in
all six navigator workspaces) but hand-curated routing drift, one broken cross-repo link, and a
generator ordering bug. Six PRs, all merged:

- **PyAutoHands#221** (merged FIRST) — `navigator.py` `GROUP_ORDER`: `multi` → `multi_dataset`
  (post-rename), added `multi_galaxy` + `ellipse`; those groups no longer fall through the
  alphabetical fallback to after `guides` in `llms-full.txt`.
- **autolens_workspace#452** — llms.txt: routed the previously-absent `multi_galaxy/` science
  case (start_here + modeling entries); fixed the stale-false `weak/` claim ("no start_here.py"
  — it exists); tail line refreshed + scopes `llms-full.txt` to local agents; scripts/README.md
  gained the missing `weak` entry; catalogue regenerated with the new group order.
- **autogalaxy_workspace#199** — scripts/README.md gained missing `multi_galaxy` + `cluster`
  entries; same tail-line scoping; catalogue regenerated.
- **autocti_assistant#20** — repointed the dead link to a non-existent
  `autocti_workspace/llms.txt` at the repo root (CTI navigator layer = future task).
- **PyAutoLens#684** — llms.txt now signposts autolens_assistant under "Use it".
- **autolens_assistant#106** — AGENTS.md scopes the `llms-full.txt` fetch instruction to local
  harnesses; connector chats route from the compact `llms.txt` (the census's performance
  finding: the ~30k-token catalogue ingested by a chat slows every subsequent turn — the
  likely cause of sluggish ChatGPT assistant sessions).

Shipped under a human-acknowledged Heart RED ("release validation FAILED (stage integrate)" —
corrective #449/#450 in flight; tenant-firewall manifest drift — PyAutoHeart#132; both
unrelated to these docs-only edits). Brain sized too-large (25); overridden as prose/repo-count
driven — one task, per-repo PRs.

Deliberately out of scope: euclid_assistant llms.txt (possibly deliberate absence),
autocti_workspace navigator layer, and the autogalaxy_assistant birth checklist (workspace
llms.txt INTERIM science section, capability-boundary assistant link, PyAutoGalaxy/llms.txt
signpost).

## Original prompt

# llms.txt census fixes: curated routing drift, navigator GROUP_ORDER, cross-repo signposts

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
- PyAutoHands
- autocti_assistant
- PyAutoLens
- autolens_assistant
Difficulty: easy
Autonomy: supervised
Priority: high (assistant paper goes live Monday 2026-08-03; feeds the pre-release rebuild)
Status: draft

## Original request (verbatim)

> __llms.txt file__
>
> The llms.txt file is used by the autolens_assistant to support conversation AI like ChatGPT.
>
> Can you do a census of this file against all the workspace updates we have done recently, and
> make sure it is up to date and fit for purpose.
>
> In particular, also make sure its paired to the autolens_assistant correctly (e.g. they are in
> sync).
>
> Soon, I will make the autogalaxy_assistant, therefore also make sure the llms.txt file in
> autogalaxy_workspace and other repos is ok.
>
> These may include making sure README.md files with contents are up to date, or any other API /
> docs / structure checks.
>
> Can you also do an assessment of whether the llms.txt file structure and general design might be
> leading to some sort of slow down? Some ChatGPT concersaiotns ive had with the assistant felt
> slow, but maybe thats just ChatGPT, but maybe as the index stuff grows we risk slow down.

## Census findings (2026-07-31, verified mechanically)

Green: all six generated catalogues (`llms-full.txt` + `workspace_index.json` in
autolens/autogalaxy/autofit workspaces and HowToLens/Galaxy/Fit) are byte-identical under
`regenerate_navigator.py`; `check_navigator.py` path + banner checks pass everywhere;
assistant ↔ workspace pairing links are correct both ways and share the routing answer shape;
root workspace READMEs are current.

Gaps (the fixes below). User approved the full plan including the optional performance item.

## Scope

1. **`autolens_workspace/llms.txt`** (hand-curated routing layer):
   - Add `multi_galaxy/` routing — a "Start here" entry for
     `scripts/multi_galaxy/start_here.py` and an "I want to…" entry for
     `scripts/multi_galaxy/modeling.py` (2+ co-dominant lens galaxies, no host halo; recent
     parity campaign made this a full science case: start_here, modeling, slam,
     source_science, subhalo-detection features).
   - Fix the `weak/` entry: `scripts/weak/start_here.py` and `modeling.py` now exist — the
     claim "this folder has no start_here.py" is false. Route to `start_here.py`.
   - Refresh the stale tail line "companion catalogue `llms-full.txt` (added in a later
     phase)" — the file exists.
2. **`autogalaxy_workspace/llms.txt`**: same stale tail-line refresh.
3. **`PyAutoHands/autohands/navigator.py`**: `GROUP_ORDER` still lists the pre-rename `multi`;
   replace with `multi_dataset` and add `multi_galaxy` (optionally `ellipse`) so those groups
   stop falling through to the after-`guides` alphabetical fallback. Regenerate both
   autolens/autogalaxy catalogues so the committed `llms-full.txt` group order updates.
4. **`autocti_assistant/llms.txt`**: the "autocti_workspace navigator" link points at
   `autocti_workspace/blob/main/llms.txt`, which does not exist (no navigator layer in that
   repo). Repoint at the repo root (`https://github.com/PyAutoLabs/autocti_workspace`) with
   wording that doesn't promise a routing file. (Adding a full CTI navigator layer is a
   separate future task.)
5. **`PyAutoLens/llms.txt`**: add a one-line autolens_assistant signpost under "Use it"
   (chat-driven science assistant; paper live Monday).
6. **`scripts/README.md` folder lists**: autolens_workspace missing `weak`;
   autogalaxy_workspace missing `multi_galaxy` and `cluster`; both have an "inculding" typo.
7. **Performance scoping (approved)**: `llms-full.txt` is 168KB (~30-40k tokens) and grows
   linearly with script count; a connector chat that ingests it pays a persistent per-turn
   cost. Scope it to non-chat harnesses: in `autolens_assistant/AGENTS.md`, qualify the
   "check the autolens_workspace catalogue (`llms-full.txt`) before writing a script from
   scratch" instruction so connector/chat sessions use `llms.txt` routing + targeted
   single-file reads instead of fetching the full catalogue; mirror the same caveat in the
   workspace llms.txt tail lines (autolens + autogalaxy) that advertise `llms-full.txt`.

Out of scope (flagged, not done here): euclid_assistant has no llms.txt (possibly deliberate —
collaboration-internal); autocti_workspace navigator layer; autogalaxy_assistant birth
checklist items (workspace llms.txt INTERIM science section + capability-boundary assistant
link + PyAutoGalaxy/llms.txt signpost) — those land with the autogalaxy_assistant task.

## Acceptance

- `check_navigator.py` path + banner checks green in autolens/autogalaxy workspaces after edits.
- `regenerate_navigator.py` produces zero diff after the GROUP_ORDER regeneration is committed
  (i.e. committed catalogues match the new group order).
- Every path/URL named in the edited llms.txt files resolves (workspace url_check CI green).
- No edits to generated files by hand (`llms-full.txt` / `workspace_index.json` only change via
  the generator).
- Notebooks are NOT regenerated (no script changes).
