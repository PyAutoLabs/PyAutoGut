# Notebooks execute from their own directory, so every auto-simulate subprocess fails

Type: bug
Target: workspaces
Repos:
- @PyAutoHands
- @autofit_workspace
- @autogalaxy_workspace
- @autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: high
Status: planned
Issue: https://github.com/PyAutoLabs/PyAutoHands/issues/204

## Symptom

Nearly every `run_notebooks (3.12, …)` shard of
`PyAutoHeart/workspace-validation` fails. It is the single largest contributor
to that job being red — ~20 of the 29 failing jobs in the 2026-07-27 06:15
scheduled run (`30242158468`).

Every failure is the same:

```
FAIL (6.8s) CalledProcessError: Command '[python, 'scripts/simulators/simulators.py']'
            returned non-zero exit status 2
```

Exit status **2** is Python's "can't open file" — the script path does not
resolve. It is not an error *inside* the simulator.

## Root cause (confirmed empirically)

`jupyter nbconvert --execute` runs the kernel with the **notebook's own
directory** as the working directory, not the directory nbconvert was launched
from. Demonstrated with a throwaway notebook printing `os.getcwd()`:

```
launcher cwd:  .../cwdtest
kernel cwd:    .../cwdtest/notebooks/sub
```

`autohands/build_util.py:execute_notebook` invokes:

```python
subprocess.run(["jupyter", "nbconvert", "--to", "notebook", "--execute",
                "--output", f, f], ...)
```

with no `cwd=` override, and nbconvert then sets the kernel cwd per notebook.

The workspaces' documented convention is the opposite — `autolens_workspace/AGENTS.md`:

> Scripts are run **from the repository root** so relative paths to `dataset/`
> and `output/` resolve correctly.

So the auto-simulate guard, which shells out to a **root-relative** path:

```python
if al.util.dataset.should_simulate(str(dataset_path)):
    subprocess.run([sys.executable, "scripts/imaging/.../simulator.py"], check=True)
```

works from a script run at the root and cannot work from a notebook run in
`notebooks/<topic>/`.

The `.py` scripts are fine; only the generated notebooks break. That is why
`run_scripts` shards mostly pass while `run_notebooks` shards mostly fail.

## Fix options (decide before implementing)

1. **Central, in PyAutoHands** — make `execute_notebook` force the kernel's
   working directory to the workspace root. This is one change covering all
   three workspaces and matches the documented convention, but it alters
   notebook execution semantics everywhere, so any notebook that *relies* on
   its own directory must be checked. Note `--output f` is currently the same
   path as the input; a cwd change interacts with that.
2. **Per-script** — resolve the simulator path relative to the script/notebook
   file rather than the cwd (e.g. off `__file__`, or a helper in
   `al.util.dataset`). Touches the ~116 scripts the `should_simulate`
   migration already swept (autolens_workspace#354 and siblings), but leaves
   the execution model alone.

Option 1 is the smaller diff; option 2 is the more local blast radius. This
needs a human call — do not pick at implementation time.

## Verification

- Reproduce first: execute one affected notebook directly with
  `jupyter nbconvert --to notebook --execute` and confirm exit 2.
- After the fix, that notebook runs clean, **and** a notebook that does *not*
  auto-simulate still passes (guard against a cwd change breaking relative
  `dataset/` reads that currently work).
- Full proof is a `workspace-validation` dispatch: the `run_notebooks` shard
  count should drop to near zero.

## Notes

- Pre-existing; unrelated to the 2026-07-27 red-jobs sweep
  (`complete/2026/07/validation-searches-env-optax.md`), which fixed a
  different shard (`run_scripts (3.12, autofit_test, searches)`).
- **`gh run view` truncates its job list.** The morning `/wake_up` digest
  reported this job as a single failing shard because of that truncation; it
  was 29. Read failures via
  `gh api repos/<org>/<repo>/actions/runs/<id>/jobs?per_page=100`.
- Sibling finding filed separately:
  `draft/bug/workspaces/auto_simulate_guard_wrong_simulator_target.md`.
