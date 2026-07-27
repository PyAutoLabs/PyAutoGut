# Auto-simulate guards point at a simulator that writes a different dataset

Type: bug
Target: autolens_workspace
Repos:
- @autolens_workspace
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: planned
Issue: https://github.com/PyAutoLabs/autolens_workspace/issues/359

## Symptom

`run_scripts (3.12, autolens, imaging)` and `run_scripts (3.12, autogalaxy, multi)`
fail in `PyAutoHeart/workspace-validation`:

```
scripts/imaging/features/multi_gaussian_expansion/likelihood_function.py ...
  FAIL (7.7s) FileNotFoundError: [Errno 2] No such file or directory: 'dataset/imaging/simple/data.fits'
scripts/imaging/features/pixelization/likelihood_function.py ...
  FAIL (7.8s) FileNotFoundError: [Errno 2] No such file or directory: 'dataset/imaging/simple/data.fits'
```

## Root cause

The auto-simulate guard runs a simulator that writes a **different dataset**
than the one the script then loads.

`scripts/imaging/features/pixelization/likelihood_function.py`:

```python
dataset_path = Path("dataset", "imaging", "simple")          # line 83
...
if al.util.dataset.should_simulate(str(dataset_path)):        # line 91
    subprocess.run([sys.executable,
                    "scripts/imaging/features/no_lens_light/simulator.py"], check=True)
```

but `scripts/imaging/features/no_lens_light/simulator.py` writes:

```python
dataset_type = "imaging"
dataset_name = "simple__no_lens_light"
```

So the guard fires, simulates `imaging/simple__no_lens_light`, and the script
then loads `imaging/simple` — which still does not exist.

## Why it surfaced now

The mismatch is **old** — `git log -S` puts the `no_lens_light/simulator.py`
guard target at `1f39244f` ("Add auto-simulate snippet to all example
scripts"), well before the recent work. What changed is the guard *mechanism*:
autolens_workspace#354 ("migrate 116 raw auto-simulate guards to
should_simulate", merged 2026-07-27 15:00 BST) replaced the raw
`if not path.exists()` checks with `al.util.dataset.should_simulate`. These two
scripts were green in the 06:15 run and red in the post-#354 dispatch, so the
new predicate lets execution proceed where the old one did not.

Confirm which of the two is true before fixing:
 - the guard target was always wrong and the old check masked it, or
 - `should_simulate` returns `False` for a case the old check treated as
   "simulate" (e.g. directory exists but is empty/partial).

The second would be a `should_simulate` bug with a much wider blast radius than
these two scripts, so **establish which before editing anything**.

## Fix

If it is purely a wrong target: repoint each guard at the simulator that
actually writes the dataset the script loads (`imaging/simple` →
`scripts/imaging/simulator.py`, not the `no_lens_light` one).

**Sweep the siblings.** #354 touched 116 guards; audit all of them for the same
class of mismatch rather than fixing only the two the CI happened to surface —
a script whose dataset is already on disk locally will hide the bug. Suggested
check: for each guard, compare the script's `dataset_path` against the
`dataset_type`/`dataset_name` the invoked simulator writes, and report every
pair that disagrees.

## Verification

- Delete `dataset/imaging/simple/`, run each affected script from the repo root,
  and confirm it simulates and loads without a `FileNotFoundError`.
- Full proof is a `workspace-validation` dispatch with both shards green.

## Notes

- Pre-existing; unrelated to the 2026-07-27 red-jobs sweep.
- Sibling finding filed separately:
  `draft/bug/workspaces/notebook_kernel_cwd_breaks_auto_simulate.md` — the
  notebook-CWD bug that accounts for ~20 of the same job's failing shards.
