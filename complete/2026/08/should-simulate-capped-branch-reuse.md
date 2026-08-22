- issue: none — shipped directly as a PR (small, single-repo follow-up of the closed PyAutoNerves#153)
- completed: 2026-08-22
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/476 (merged dc0c273)
- workspace-pr: none — no workspace change needed

`should_simulate`'s `PYAUTO_SMALL_DATASETS=1` branch deleted and re-simulated
**every** dataset unconditionally, paying a full simulation pass per dataset per
smoke run across ~253 call sites for datasets that were already correct. That was
correct when written and the docstring said why: it "cannot know the capped
dataset on disk was produced by the SAME cap". The `SMALLDAT` stamp
(`complete/2026/08/small-datasets-regime-stamp.md`) removed that limitation.

**THE FIX IS NOT THE ONE-LINER THE PARENT RECORD PREDICTED.** That record — and
the filed prompt's parent framing — said `if stamp is not True:` was a cheap fix.
It is not, and shipping it would have been worse than doing nothing.

`SMALLDAT = T` means "capped at whatever `SMALL_DATASETS_SHAPE_NATIVE` was when
this file was written", NOT "capped at today's cap". If that constant ever
changes, every dataset on disk goes on claiming `T` at the old size, and reusing
on the stamp alone silently feeds stale wrong-sized data to a run that asked for
the new cap — the exact silent-stale-dataset bug the stamp exists to prevent,
reintroduced through the opposite branch.

Reuse therefore requires BOTH: stamped `T` **and** shape `== SMALL_DATASETS_SHAPE_NATIVE`
(`_is_capped_at_the_current_cap`).

**This is the mirror image of `_stamp_contradicted_by_shape`** on the
full-resolution branch, and exists for the same reason, which is the durable
lesson from this pair of tasks: **the stamp records the writer's ENVIRONMENT, not
a measured property of the data.** Neither branch may treat it as unfalsifiable.
Any future consumer of `SMALLDAT` must corroborate it before acting destructively
or before skipping work on its authority.

**TRAPS**
- Reuse on the stamp alone is the bug. Both halves are load-bearing.
- Interferometer datasets deliberately NEVER qualify: `data.fits` is
  `(n_visibilities, 2)`, its shape fixed by the committed uv file and unchanged by
  the cap, so shape cannot corroborate the stamp. Trusting the stamp alone for
  precisely the family whose corruption is invisible is the wrong trade. Written
  into the docstring, not left to fall out of the code.
- Anything with no readable top-level `data.fits` (JSON-only, datacubes nesting
  theirs in `channel_XXX/`, multi_dataset's prefixed names) fails the check and
  regenerates, preserving prior behaviour for the families this cannot speak about.
- The pre-existing test asserting unconditional deletion ENCODED the limitation
  being removed. It had to be rewritten, not deleted — a test that fails because
  the limitation it documents is gone is a signal, not an obstacle.

**Behaviour: exactly one row changes.** A dataset capped at the current cap is
reused; different-cap-stamped, unstamped legacy, full-resolution, interferometer
and no-`data.fits` all regenerate as before. Reuse requires positive evidence and
everything else fails to provide it.

Tests: 1106 passed / 0 failed, green with `PYAUTO_SMALL_DATASETS=1` exported AND
unset, tree clean both ways. CI green on 3.12 / 3.13 / nojax.

**Gate note.** Heart was not consulted — no PyAutoHeart checkout in this
web-github session; the documented per-repo suite fallback was used, and CI
subsequently agreed.

## Original prompt

# should_simulate's capped branch re-simulates every dataset, ignoring the stamp it now has

Type: maintenance
Target: libraries
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: formalised

Split out of PyAutoNerves#153 on 2026-08-22 (`complete/2026/08/small-datasets-regime-stamp.md`),
which added the `SMALLDAT` regime stamp and deliberately did not touch this branch.

`autoarray/util/dataset_util.py should_simulate` still does this when
`PYAUTO_SMALL_DATASETS=1`:

```python
if os.environ.get("PYAUTO_SMALL_DATASETS") == "1":
    if Path(dataset_path).exists():
        shutil.rmtree(dataset_path)
    return not Path(dataset_path).exists()
```

Unconditional. Every smoke run deletes and re-simulates **every** dataset, even
one already written by a capped run at the same cap.

That was correct when written — the docstring says so explicitly: *"The small
path is unconditional by design: it cannot know the capped dataset on disk was
produced by the SAME cap, so it always regenerates."* The stamp removes exactly
that limitation. `SMALLDAT = T` now says the writer capped it.

`if stamp is not True:` is the shape of the fix. The saving is one full
simulation pass per dataset per smoke run, across ~253 `should_simulate` call
sites in autolens_workspace.

## The trap that makes this not a one-liner

**A stamp of `T` does not mean "capped at the cap size in force now."** It means
"capped at whatever `SMALL_DATASETS_SHAPE_NATIVE` was when it was written." If
that constant ever changes, every dataset on disk still claims `T` while being
the wrong size, and skipping regeneration would silently reuse it — the same
class of silent-stale-dataset bug the stamp exists to prevent, reintroduced
through the other branch.

So the reuse condition is not `stamp is True` alone. It needs the on-disk shape
to also match the *current* cap, which `_on_disk_shape_native` already provides
and `_is_small_datasets_on_disk` already compares with `== SMALL_DATASETS_SHAPE_NATIVE`.
Reuse only when the stamp says capped **and** the shape matches today's cap;
anything else regenerates.

Note this is the mirror image of `_stamp_contradicted_by_shape` on the full-regime
branch, and for the same reason: the stamp records the writer's environment, not
a property of the data. Neither branch should treat it as unfalsifiable.

Interferometer datasets are shape-invariant under the cap, so a shape check
cannot corroborate them. Decide explicitly whether they reuse on the stamp alone
or always regenerate — do not leave it to fall out of the code.

## Suggested scope

1. Reuse a capped dataset only when the stamp says `T` **and** the shape matches
   the current cap. Everything else regenerates, as today.
2. Take the interferometer decision explicitly and write it in the docstring.
3. Test both directions: same-cap dataset is reused; a dataset stamped `T` at a
   different shape is regenerated.
4. Correct the docstring paragraph that says the small path cannot know.
