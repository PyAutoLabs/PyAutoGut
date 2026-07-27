## history-blob-purge
- issue: (none — human-directed operation)
- completed: 2026-07-27
- summary: Leg 7 (final) of the dataset-bulk series — the human-authorized exception to the never-rewrite-pushed-history rule, executed with git filter-repo on fresh mirror clones behind hard gates (HEAD tree byte-identical — verified equal pre/post on every repo; tag NAMES preserved so Colab pins keep resolving; non-peeled tag + branch counts unchanged; fsck clean; size-band abort gates; fsck-verified permanent backup mirror BEFORE any push). Results (reachable pack): autogalaxy_workspace 170.6→31.9 MiB (−81%), autofit_workspace 36.6→5.8 MiB (−84%), autolens_workspace 954.4→97.5 MiB (−90%; round 1 ABORTED at the size gate — the measurement's path bins missed the real bulk under top-level output/ ~411 MiB and the ancient howtolens/ tree ~134 MiB; round 2 with the corrected dead-prefix list passed all gates), autocti_workspace 110.4→32.5 MiB (−71%, run after leg-6 merged made its 78 MiB imaging_ci history dead). HowTo repos deliberately SKIPPED (0.5-2 MiB reclaimable, densest Colab-tag coupling). New main SHAs: autogalaxy 5f33e0bc, autofit 6b37f4ab, autolens d83af681, autocti 7a3298c2. Old history recoverable permanently from fsck-verified mirrors in ~/Code/PyAutoLabs-backups/ (old mains f0efa50a9/277164bc5/6be18d0cf/1929ff0c5); condemned.md recover-points reconciled to the mirrors. Local stashes preserved across resets (they pin some old objects locally — accepted). Accepted costs on record: 2026.7.27.1 tag content change in autolens+autogalaxy (purged datasets self-provision via guards), 17 autolens fork divergences, early void of the remote-history recover SHAs. Leftover flag: two local-only unmerged autocti branches (feature/cti-resurrection-phase{4,5}, 2026-07-17) pin ~75 MB of pre-rewrite objects locally — surfaced for a PyAutoGut condemn call, not deleted.

## Original prompt

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
