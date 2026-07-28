- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1414 (closed)
- completed: 2026-07-28
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1427, https://github.com/PyAutoLabs/PyAutoGalaxy/pull/533 (both MERGED)
- summary: `AbstractPaths.preserve_in_zip` only wrote a member absent from a completed search's zip, so a post-completion artifact rewritten on disk (the adapt-image cache invalidated by a changed dataset mask, PyAutoGalaxy#516) left stale bytes in the archive and `restore()` resurrected them — the search missed its cache every run instead of once. Now an existing member is compared against the file on disk via the `file_size`+`CRC` in the central directory (chunk-streamed `zlib.crc32`, archived bytes never decompressed) and replaced when it differs; byte-identical stays a no-op so the common resume path never pays a rewrite. `zipfile` cannot overwrite in place, so `_replace_zip_member` streams the other members into a temp archive in the same directory (preserving each `ZipInfo` + `compress_type`) and swaps with `os.replace`; a mid-way failure leaves the original intact. Tests: replacement survives `restore()` and keeps sibling members; identical content leaves the zip byte-identical. The new test fails on pre-fix source. PyAutoGalaxy rider: `galaxy_name_image_dict_via_result_from`'s docstring documented the un-repairable stale cache as standing behaviour — corrected.
- gotchas: (1) The related config knobs `force_pickle_overwrite`/`force_visualize_overwrite` are NOT an existing lever for this — they act on the search whose `fit()` is re-invoked, which always brackets the run with `paths.restore()` (which DELETES the zip, abstract.py:365) and `post_fit_output` → `zip_remove()` → `zip_directory(..., "w")` (full rebuild). `preserve_in_zip` exists for the opposite seam: a write into an UPSTREAM completed search never fitted this run, whose zip is never rebuilt. (2) Reusing `zip_directory` for a full re-zip is unsafe here: with `remove_files: true` the completed dir is deleted after zipping, so a later post-completion write recreates only `files/<cache>` and a full re-zip would truncate the archive to that one file — the test config has `remove_files: true`, which is why the new tests must re-`mkdir` the files dir after `zip_remove()`. (3) `autolens/analysis/result.py`'s positions cache writes only when the loose file is absent, so it never depended on replacement. (4) Smoke: 56 passed / 6 failed, ALL 6 reproduced identically on unmodified `main` (5 JAX-parity mismatches in `autolens_workspace_test/*/jax_likelihood/`, byte-identical numbers; `imaging/subhalo_recovery.py` is not broken — it passes on `main` in 8m25s, just past the 300s smoke cap, and carries no `# SLOW` marker → filed as `draft/maintenance/autolens_workspace_test/subhalo_recovery_exceeds_smoke_cap.md`). Suites 1559p/1009p; PR CI green 3.12+3.13+docs; Heart YELLOW (4 unrelated reasons) acknowledged by the human at ship time.

## Original prompt

# preserve_in_zip never replaces an existing archive member

Type: bug
Target: autofit
Repos:
- @PyAutoFit
- @PyAutoGalaxy
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

Filed as GitHub issue @PyAutoFit#1414 (spun out of @PyAutoGalaxy#516). Original
issue body verbatim below.

## Overview

`Paths.preserve_in_zip` (`autofit/non_linear/paths/abstract.py:316`) adds a file to a completed search's
`.zip` only when that member is **absent**:

```python
with zipfile.ZipFile(self._zip_path, "a") as f:
    if arcname not in f.namelist():
        f.write(file_path, arcname)
```

When the member already exists but its on-disk counterpart has been rewritten, the archive keeps the old
bytes. Because `restore()` deletes the output directory and re-extracts the zip, the rewritten file is
discarded on the next resume and the stale member comes back.

## How it was found

Spun out of PyAutoGalaxy#516. The per-galaxy adapt-image cache (`files/galaxy_images_snr.fits`) can go stale
when a rerun's dataset mask changes while the model stays identical — the search identifier does not encode
the dataset, so the run lands on the previous run's output directory. PyAutoGalaxy#516 fixes the correctness
half: the cached mask is validated on load and a mismatch becomes a cache miss, so the images are recomputed
on the current mask.

The recomputed images are then written back via `_galaxy_image_dict_to_cache` -> `preserve_in_zip`. Verified
end-to-end that the archived copy is **not** updated: after a run that successfully invalidated and
recomputed four stale caches, three upstream searches' zips still held the 15x15 stale member (only the one
search whose zip was newly created held the correct 16x16 member).

Consequence is a performance wart, not a correctness one: such a search misses its cache on *every* run
rather than once, paying the max-log-likelihood-fit rebuild each time, until its output directory is cleared.

## Plan

- Make `preserve_in_zip` replace an existing member whose content differs, instead of skipping it. `zipfile`
  cannot overwrite a member in place, so the archive needs rewriting when a replacement is required — keep
  the no-op fast path for the already-identical case so the common path does not pay a rewrite.
- Preserve the existing no-op when the zip does not yet exist (the search is still running and everything is
  zipped at completion).
- Add a unit test: write a member, rewrite the on-disk file, `preserve_in_zip` again, assert the archive
  carries the new bytes and that `restore()` yields them.

## Notes

- Not urgent for the PyAutoGalaxy#516 fix, which is correct without it — this only restores the caching win.
- Worth checking the other `preserve_in_zip` callers for the same silently-stale assumption.
