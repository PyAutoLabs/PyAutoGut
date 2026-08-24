- library-prs: https://github.com/PyAutoLabs/PyAutoArray/pull/489, https://github.com/PyAutoLabs/PyAutoGalaxy/pull/587
- merge-commits: PyAutoArray `b690c3e59894942a999142525453799d1894d347`; PyAutoGalaxy `0c7bc627de888554f5bcc315f6726215b71774bc`
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/488
- summary: Collapsed three copies of the matplotlib colour-norm construction into
  one helper, `autoarray.plot.utils.norm_from`, called by `plot/array.py`,
  `plot/inversion.py` and (by delegation) `autogalaxy.util.plot_utils.norm_from`.
  The task was filed as a refactor but the point was a live behaviour bug the
  duplication had let drift in: `plot_inversion_reconstruction` hardcoded the
  `1e-4` log floor and never read `visualize.general.general.log10_min_value`, so
  a user who changed the configured floor had it honoured on array plots and
  silently ignored on inversion plots. The config read now lands once, as
  `_conf_log10_min_value` alongside the other `_conf_*` readers.
- validation: PyAutoArray 1157 passed 55 skipped (+11 new), CI green on
  3.12/3.13/nojax; PyAutoGalaxy 1119 passed 1 skipped, CI green on
  3.12/3.13/nojax/docs. Eight PyAutoArray sparse-operator inversion failures in
  the authoring environment are pre-existing, verified identical on a stashed
  clean tree, and absent from CI.
- release: not performed; both merged PRs remain in the pending-release queue.

## Three divergences, decided rather than assumed

The prompt was explicit that the copies disagreed in more than one way and that
each difference had to be decided deliberately — *"do not assume `array.py` wins
on all three"*. The decisions are recorded in the helper's docstring so the next
reader does not have to re-derive them:

| # | The divergence | Decision |
|---|---|---|
| 1 | `array.py` read the configured floor and clipped; `inversion.py` hardcoded `1e-4` and did not clip | **`array.py` wins.** The helper always reads config (fallback `1.0e-4`) and clips before deriving `vmax`. This is the bug fix. |
| 2 | `array.py` derived `vmax` from the clipped image; `inversion.py` from `pixel_values`, falling back to `vmin * 10` | **Not a divergence at all.** The two call sites colour different data. `array` means "the values being coloured"; `array=None` takes the same fallback as an all-`NaN` array, which is exactly what inversion's separate `else` branch did. |
| 3 | `array.py` widened a degenerate `vmax <= vmin` even when passed explicitly; `inversion.py` only inside its `elif pixel_values` branch | **`array.py` wins.** `LogNorm(vmin=10, vmax=1)` is unusable whoever supplied the numbers. |

Decisions 1 and 3 change behaviour, both on `plot_inversion_reconstruction`
only; `plot_array` and the autogalaxy GUI path are untouched. Decision 2 is the
one worth remembering as a *non*-change: the obvious reflex on a dedup task is
to reconcile every difference, and one of these three should not be reconciled.

## The test that had to have teeth

This is a plotting path with thin coverage, so a green suite proves little on
its own — the bug being fixed had lived in it undetected. The regression test
therefore exercises **both call sites end-to-end** rather than unit-testing the
helper alone: a spy wrapping the shared helper records the norm each of
`plot_array` and `plot_inversion_reconstruction` actually applied, with
`log10_min_value` moved to `3.0e-3` for the duration.

It was then checked against the old behaviour rather than assumed to bite:
reverting `plot_inversion_reconstruction` to the hardcoded floor makes it fail
with `assert 0.0001 == 0.003`. A structural "does it call the helper" assertion
would have passed the same revert.

`test_autogalaxy/gui/test_plot_norm.py`, added by PyAutoGalaxy#586 to pin the
autogalaxy behaviour, stayed green **unmodified** — which is the evidence that
the delegation is faithful rather than merely convenient.

## The prompt was not on `main`

Worth recording because it cost the first ten minutes of the task and will
recur. `/start_dev draft/refactor/autoarray/shared_log_norm_helper.md` found
nothing: the file had only ever been committed to
`claude/aplt-output-drift-repos-33n81z` (`dd7501f1`, "file the three
aplt-output-drift follow-ups + queue them"), and **no PR was ever opened for
that branch**. Three prompts filed that day plus the `queue.md` additions were
invisible to `main`, to `dashboard.md` and to the Brain router — the Mind
believed it had filed work it had not.

The prompt was recovered from that branch with `git checkout <branch> -- <path>`
and advanced through the lifecycle normally. **The stranding resolved itself
mid-task**: PR #311 landed that filing branch on `main` while this work was in
flight, which is why the close-out hit a merge conflict — `main` was adding the
prompt to `draft/` at the same moment this branch folded it into `complete/`.
The draft copy was removed in the merge (shipped work must not sit in two
lifecycle states) and its `queue.md` line marked `# DONE`.

The lesson survives the happy ending: for the hours between `dd7501f1` and PR
#311, the Mind believed it had filed work that no tool could see. A filing
branch with no PR is a silent loss, and nothing warns about one.

## Environment notes

- Ran as a `web-github` session: no worktree, the session clones are the working
  trees, and Python 3.12 built from scratch in a venv (the container's default
  is 3.11, below autoarray's `requires-python`). 3.13 was covered by CI only.
- The Heart readiness gate was consulted and returned **`stale`, score 35** —
  every reason `status unknown` (`no report.json`, `install verification not
  run`, five repos unknown). That is Heart with an empty sensor bank in a fresh
  container, not a health signal. The merge decision rested on real CI instead,
  which is the sensor Heart was missing.

## Original prompt

# One shared colour-norm helper — the three copies have already diverged

Type: refactor
Target: autoarray
Repos:
- PyAutoArray
- PyAutoGalaxy
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

Split out of `aplt-output-drift-remaining-repos` (PyAutoGalaxy#585, 2026-08-24),
which added the third copy rather than widen that task into a third repo.

## The duplication

Building the matplotlib colour norm from `use_log10` / `vmin` / `vmax` is written
out three times:

| Where | Notes |
|---|---|
| `autoarray/plot/array.py:164-188` | the reference implementation |
| `autoarray/plot/inversion.py:92-107` | **already divergent — see below** |
| `autogalaxy/util/plot_utils.py::norm_from` | added by PyAutoGalaxy#586, faithful to `array.py` |

## This is not a tidiness task — the copies disagree

`array.py` reads the configured floor:

```python
log10_min = _conf.instance["visualize"]["general"]["general"]["log10_min_value"]   # fallback 1.0e-4
clipped = np.clip(array, log10_min, None)
```

`inversion.py` **hardcodes `1e-4`** and never consults `autonerves` config, and
does not clip. So a user who changes `log10_min_value` gets it honoured on array
plots and silently ignored on inversion plots. That is a live behaviour bug, not
a style issue, and it is the thing to fix first — the deduplication is how you
stop it recurring.

They differ in a second way worth preserving deliberately rather than by
accident: `array.py` derives `vmax` from the clipped array, `inversion.py` from
`pixel_values` and falls back to `vmin_log * 10.0` when there are none. And
`inversion.py`'s `vmax_log <= vmin_log` guard sits inside its `elif pixel_values`
branch, so an explicitly-passed degenerate `vmax` is *not* widened there but *is*
in `array.py`.

**Decide which behaviour is correct for each difference before merging them** —
do not assume `array.py` wins on all three. Write the decision into the helper's
docstring.

## Shape of the fix

1. Add one helper in **PyAutoArray** — the lowest repo that owns this logic;
   `autoarray/plot/utils.py` sits alongside `auto_mask_edge` and the other
   shared plot helpers. Give it the `array`/`use_log10`/`vmin`/`vmax` signature
   plus whatever parameter reconciles the `pixel_values` difference.
2. Call it from `array.py` and `inversion.py`.
3. Make `autogalaxy.util.plot_utils.norm_from` **delegate** to it rather than
   reimplement — autogalaxy may import autoarray (dependency direction is fine;
   the reverse is not). Keep `norm_from` as the autogalaxy-facing name so the
   `Clicker`/`Scribbler` callers added in PyAutoGalaxy#586 keep working.

## Constraints

- **Behaviour-preserving except where you deliberately fix a divergence**, and
  each such fix is named in the PR body. This is a plotting path with thin test
  coverage, so an unnoticed change ships silently.
- Library-first: PyAutoArray merges before PyAutoGalaxy.
- `test_autogalaxy/gui/test_plot_norm.py` (added by #586) already pins the
  autogalaxy behaviour — it must stay green, or its change must be justified.

## Verification

Add tests in PyAutoArray covering the config-floor path (`log10_min_value` set to
something other than `1e-4`, asserting *both* call sites honour it), the
explicit-limits path, the derived-`vmax` path, and the degenerate `vmax <= vmin`
case. Then the full suites in both repos, on 3.12 and 3.13.
