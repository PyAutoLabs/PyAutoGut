# Notebook kernel cwd + two guard follow-ups — 3 PRs, 3 repos

Issue: https://github.com/PyAutoLabs/PyAutoHands/issues/204 (CLOSED)
PRs (all MERGED 2026-07-28):
- PyAutoHands#205 (`ef0f5a3`) — notebook kernel cwd → workspace root
- PyAutoBrain#173 (`8e4cb5b`) — bug agent fix-locus no longer forbids the script body
- autogalaxy_workspace#176 (`1611f93`) — gitignore `notebooks/plot/`

Follow-ups from [[auto-simulate-guard-targets]]. **One PR cannot span three
repos** — the request was "fix those 3 things in one PR"; they lived in three
repos, so it became one PR each.

## #204 — both of its own fix options were WRONG

The prompt said "decide before implementing / do not pick at implementation
time". Investigating first is what saved this: **neither documented option is
implementable.**

1. *"Central — force the kernel's working directory"* is **not** a `cwd=`
   kwarg. The launcher's cwd is *already* the workspace root; nbconvert
   overrides the **kernel's** cwd regardless, and exposes **no CLI flag** for
   it. The only knob is `resources['metadata']['path']`, which nbclient turns
   into the kernel `cwd` (`nbclient/client.py:535`) — Python API only.
2. *"Per-script — resolve off `__file__`"* is impossible: **`__file__` is not
   defined in a notebook kernel** (verified empirically). It exists in the
   `.py` scripts, which already worked, and is missing in exactly the notebook
   context that is broken.

**Shipped 1b:** `execute_notebook` subprocesses a new
`autohands/run_notebook.py` that sets the resource path. The subprocess
boundary is kept *deliberately* — process isolation, `BUILD_SCRIPT_TIMEOUT`
and per-notebook env unchanged; only the kernel's cwd moves. No tutorial
scripts touched.

**The near-miss.** `build_util.is_clean_skip_exit` distinguishes an intentional
`sys.exit(0)` optional-dependency skip from a genuine failure by
**string-parsing the run's stderr** for a `CellExecutionError` marker whose
last line is `SystemExit: 0`. A naive in-process rewrite (option 1c) would have
broken it silently — the skip idiom would start reporting as failure. The
runner therefore leaves `CellExecutionError` **uncaught** so Python's own
traceback reproduces that exact shape. Verified `sys.exit(0)`→True,
`sys.exit(1)`→False, `ValueError`→False. Documented in the module so it is not
"tidied up" later.

Proof on a real workspace notebook:
`OLD jupyter nbconvert → exit 1 CalledProcessError` / `NEW run_notebook.py →
exit 0`. Two regression tests added; suite 234 → 236.

## CI GAP found (worth its own issue)

**PyAutoHands has no PR-level test gate.** `python_matrix.yml` is
`workflow_dispatch` + weekly cron only, so the repo that generates and executes
every notebook runs its 236 tests weekly or never. PyAutoBrain is the same
(`docs.yml` fires only on `docs/**` pushes to main), so **#173 had no CI path
at all**.

The matrix was **hand-dispatched on the branch** for #205 rather than merging
on local evidence alone; it came back green (0 non-success jobs across
unit_tests 3.9–3.13 and workspace smoke_tests). On merge the branch was kept
(no `--delete-branch`) precisely so that dispatched run would not be cancelled,
then deleted after it reported.

## Bug Agent fix-locus (#173)

`fix_locus` returned, for *any* workspace-only `config-error`:
"workspace config (config/build/*.yaml) … never inline edits to the script
body" — an absolute. But `config-error` matches on generic signals (`yaml`,
`config/build`) and ranks **above** `runtime-error` in `TYPE_ORDER`, so a
prompt that merely *mentions* a profile lands there. On #359 that routed a
`FileNotFoundError` caused by hard-coded paths *in script bodies* to a locus
that cannot contain the defect, with the only real fix forbidden.

Now conditional: knobs when the **environment** is wrong; script body when the
**value in the script** is wrong. Invariant preserved and sharpened — never
*mask* a symptom in a user-facing script, but do correct a value that is simply
wrong. `TYPE_ORDER` deliberately **not** touched (reordering affects every
triage; separate change).

## Traps

- `gh api -X DELETE .../git/refs/heads/<b>` returned 422 on the *second* call
  because the first had already succeeded; and `gh api .../git/ref/heads/<b>`
  is an unreliable existence check. Settle branch existence with
  `gh api repos/<r>/branches`.
- Concurrent sessions were editing `active.md` and had checked
  `autogalaxy_workspace` out onto their own branch — committed only explicit
  paths, and left their checkout alone.

## Unrelated find (not actioned)

`~/venv/PyAuto` has **`pathlib==1.0.1`** installed — the dead Python-2 backport
of the stdlib module. It already breaks `jupyter execute --help`. It does not
shadow stdlib `pathlib` on normal import, so nothing here is affected, but it
is a live hazard worth removing.
