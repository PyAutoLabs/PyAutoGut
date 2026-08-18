# pre_build stages untracked files, publishing uncommitted human work

Type: bug
Target: PyAutoHands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

`pre_build.sh`'s `run_workspace` runs, for each of 13 workspace repos:

```bash
for d in scripts slam_pipeline; do black "$d/"; done
...
for d in notebooks scripts; do git add "$d/"; done
```

Both operations reach **untracked** files. `git add <dir>/` stages them, so any
uncommitted human work under `scripts/` or `notebooks/` is reformatted by black
and pushed inside the `"pre build"` commit — to a public repo, with no prompt
and exit status 0.

This is the same leak class as PyAutoBuild#126, which was fixed for `dataset/`
and `config/` by deleting their staging lines (#156). The `scripts/` path kept
the hole; the comment above the staging block asserts "Releases require clean
mains (Heart gates on it)" but nothing in the script enforces it for the 13
repos it actually commits to — the clean-main gate at the top covers PyAutoHands
alone.

## How it surfaced

A near-miss during the 2026-08-07 release drive (see `active.md`
→ `release-drive-2026-08-07`, `pre_build-trap`): an uncommitted WIP script in
`autolens_assistant/scripts/` would have been reformatted and published. It was
caught only because the operator noticed and moved the file out of the repo by
hand, restoring it afterwards and verifying it byte-identical by md5. The record
notes it is "worth a real fix so it is not left to operator vigilance."

Reproduced against the pre-fix script on throwaway fixture repos: the private
file was committed as `"pre build"` and pushed to the remote, exit 0, silently.

## The fix

1. **Fail-fast preflight over every repo, before the first is touched.**
   `run_workspace` commits *and pushes* each repo before moving to the next, so
   a per-repo check aborting midway would leave earlier repos already
   published. This also answers the open atomicity question in
   `docs/pre_build_failure_audit.md` §6 ("worth a fail-fast pre-pass?").
   Uses `git ls-files --others --exclude-standard`, which honours `.gitignore`
   and tolerates pathspecs matching nothing.
2. **Narrow the staging** to `git add -u` (tracked edits and deletions) plus
   newly created files added by explicit path, so the directory-wide form
   cannot return. New notebooks from `generate.py` must still be staged — that
   is why plain `git add -u` alone is insufficient.
3. The repo list moves from `run_workspace "..."` call lines into a
   `WORKSPACE_SPECS` array, because two passes now read it and a second
   hand-maintained list would drift.

No `--allow-dirty` override: an override is exactly the operator vigilance the
change replaces.

## Verification

Text assertions cannot prove a gate fires, so `tests/test_pre_build_staging.py`
runs the real script against a throwaway `PYAUTOBASE` of fixture git repos with
`black`/`python`/`gh` stubbed and real bare remotes — covering the WIP abort,
multi-repo reporting, gitignored files not blocking a release, new generated
notebooks still being staged, tracked deletions, and the missing-checkout abort.

## Related

`draft/bug/pyautobuild/root_level_git_add_stages_nothing_on_unmatched_glob.md`
is **obsolete** — the root-level glob `git add` line it describes no longer
exists; #156 deleted it as a measured no-op in all 13 repos. Retired to
`complete/archive/shelved/` alongside this task.

<!-- filed 2026-08-08 from the release-drive-2026-08-07 pre_build-trap record -->
