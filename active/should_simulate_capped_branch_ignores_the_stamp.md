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
