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
