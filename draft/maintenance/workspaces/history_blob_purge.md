# History blob purge — rewrite pushed history to drop dead dataset/render bytes

Type: maintenance
Target: workspaces
Repos:
- autolens_workspace
- autocti_workspace
- autogalaxy_workspace
- autofit_workspace
- HowToLens
- HowToGalaxy
- HowToFit
Difficulty: hard
Autonomy: human-required
Priority: normal
Status: formalised

Leg 7 (final coda) of the dataset-bulk series, **explicitly requested by the human
2026-07-27** — this is the sanctioned exception to the never-rewrite-pushed-history
rule, which otherwise stands absolute. Purpose: the purged dataset blobs and stale
render PNGs still bulk out `.git` history, making clones slow and history hard to
navigate; remove them with `git filter-repo` and force-push rewritten history.

## Hard gates (non-negotiable)

1. **Per-repo explicit human confirmation immediately before each rewrite** — the
   standing rule is suspended only for the repos the human names, one at a time.
2. **No rewrite while another session holds a worktree/claim on the repo**
   (check `worktree_list_claimed` + `PyAutoLabs-wt/`) — rewrites orphan their bases.
3. **Mirror backup first**: `git clone --mirror` of each repo to a dated local
   backup (and keep until the human confirms post-rewrite health) — this replaces
   the PyAutoGut recover-point promise, because...
4. **Condemned recover-point SHAs die.** Every `condemned.md` entry whose
   archive-ref says "bytes live in remote history at <SHA>" becomes void for the
   rewritten repo. The rewrite IS the Gut sweep for those entries — update
   condemned.md accordingly (early void, human-authorized).
5. Tags are rewritten by filter-repo — Colab URLs pin to tags, so tags must
   survive with the same NAMES (pointing at rewritten SHAs) and be force-pushed.
6. Open PRs on a rewritten repo break — confirm none open (or accept).
7. After force-push: every local checkout re-synced via fetch + reset --hard
   (never merge old into new), stale local branches pruned, `git gc --prune=now
   --aggressive` locally to realize the size win.

## Execution sketch (per confirmed repo)

fresh `--mirror` clone → `git filter-repo --invert-paths` with the exact dead
path list (purged dataset dirs from legs 1/2/6 + PR#356 + historical purge legs
#272/#129/#151, and optionally stale markdown PNG paths that no longer exist at
HEAD) → verify HEAD tree is BYTE-IDENTICAL to pre-rewrite HEAD tree (`git
diff --stat old-head new-head` must be empty — the rewrite may only change
history, never the present) → verify tags exist and Colab links resolve →
force-push branches+tags → local re-sync → measure packed size before/after →
update condemned.md → post summary.

Measurement first: a read-only sizing pass decides which repos are worth the
disruption (a repo with <10 MB reclaimable is not worth breaking clones over).
