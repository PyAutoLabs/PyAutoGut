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
