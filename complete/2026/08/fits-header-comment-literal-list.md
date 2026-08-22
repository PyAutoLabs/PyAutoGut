- issue: none — shipped directly as a PR (small, single-repo, cosmetic)
- completed: 2026-08-22
- library-pr: https://github.com/PyAutoLabs/PyAutoNerves/pull/155 (merged 0ecefa0)
- workspace-pr: none — no workspace change needed

`hdu_list_for_output_from` passed a LIST, `[""]`, as the FITS card comment.
astropy does not reject it — it `str()`s it — so every card written from a
`header_dict` landed on disk reading `PIXSCAY = 0.1 / ['']`. Four such cards on
every `Imaging` dataset the stack writes, rendering for anyone opening a PyAuto
FITS in DS9, astropy or any external tool. Found while implementing the regime
stamp (`complete/2026/08/small-datasets-regime-stamp.md`) and deliberately kept
out of that change so a cosmetic fix did not ride a behavioural one.

Fixed by passing `""`. Verified on disk: the card becomes a plain
`PIXSCAY = 0.1` — no comment, no trailing slash, byte-size unchanged. Both `""`
and dropping the third tuple element produce byte-identical output; `""` was
chosen to keep the intent explicit and the diff minimal.

**DECISION taken explicitly, not by omission.** The prompt raised adding REAL
per-key comments, since `PIXSCAY`/`ORIGINY` are not self-describing. Declined:
autonerves receives an opaque `header_dict` and does not know the key vocabulary
— those are autoarray's `Mask2DKeys`. Hardcoding their meanings in the base
serialization layer couples it to a downstream key set, the wrong direction for
the dependency. If descriptive comments are wanted the CALLER should supply them,
which is a separate API change to `header_dict`'s shape.

**TRAPS**
- astropy accepts a non-string comment silently and `str()`s it. It will not warn
  you that you passed the wrong type; the evidence is only visible on disk. Check
  rendered cards, not just `header[key]`.
- The `except ValueError: float(value)` fallback beside it is unrelated and was
  left alone — bool never raises there, so it is unreachable for the stamp.
- `test_autonerves/files/array_out.fits` is a tracked test WRITE TARGET, so its
  bytes change with the comment and it must be refreshed in the same commit.
  Verified byte-stable across repeated runs, and identical with
  PYAUTO_SMALL_DATASETS exported AND unset — the autouse conftest fixture from
  #154 is what makes that deterministic.

Tests: 166 passed, green both env states. CI green on 3.12 / 3.13 / nojax.

**Gate note.** Heart was not consulted — no PyAutoHeart checkout in this
web-github session; the per-repo suite fallback was used and CI agreed.

**Completes the three follow-ups** filed off the regime-stamp task, with
`complete/2026/08/should-simulate-capped-branch-reuse.md` and
`complete/2026/08/plot-utils-duplicate-modules.md`.

**STILL OPEN, and the stamp is NOT LIVE until it is done:** PyAutoNerves needs a
release. `autoarray/pyproject.toml` floors `autonerves>=2026.8.22.1`, which was
the newest release on PyPI and predates the stamp, so an installed-from-PyPI
autoarray sees no card and falls back to the shape heuristic. Also still unrun:
the workspace smoke suite, which has never exercised any of this.

## Original prompt

# Every header_dict FITS card carries the literal comment text ['']

Type: bug
Target: pyautonerves
Repos:
- @PyAutoNerves
Difficulty: small
Autonomy: supervised
Priority: low
Status: formalised

Found 2026-08-22 while implementing the regime stamp (PyAutoNerves#153,
`complete/2026/08/small-datasets-regime-stamp.md`). Pre-existing, cosmetic, and
deliberately left out of that change so a header-card fix did not ride along with
a behavioural one.

`autonerves/fitsable.py` (lines 138 and 140 on current main) passes a **list** as
the FITS comment:

```python
header.append((key_str, value, [""]))
except ValueError:
    header.append((key_str, float(value), [""]))
```

astropy does not reject it — it `str()`s the list. So every card written from a
`header_dict` lands on disk carrying the literal three-character comment `['']`:

```
PIXSCAY =                  0.1 / ['']
PIXSCAX =                  0.1 / ['']
ORIGINY =                  0.0 / ['']
ORIGINX =                  0.0 / ['']
```

Verified empirically with astropy 8.0.1. Every `Imaging` dataset the stack writes
has this on four cards.

## Impact

Cosmetic only. Nothing reads comments — the FITS header consumers across
PyAutoArray, PyAutoGalaxy, PyAutoLens and the workspaces all index values by key
name, verified during PyAutoNerves#153. It is visible to anyone opening a PyAuto
FITS in DS9, `astropy`, or any external tool, which is the argument for fixing it:
it reads as a serialization bug in output we hand to other people.

The intent was presumably an empty comment. `""` gives that; the list gives the
rendered repr of a list.

## Suggested scope

1. Replace `[""]` with `""` at both sites, or drop the third tuple element.
2. Consider whether `header_dict` should carry real comments — the four keys it
   writes (`PIXSCAY`/`PIXSCAX`/`ORIGINY`/`ORIGINX`) are not self-describing to an
   outside reader, and the slot is already there.
3. Note this changes the bytes of every FITS the stack writes, exactly as the
   regime stamp did. The same finding applies: no hash, golden-file or checksum
   pin exists over any `.fits` in the stack, and the change is byte-size neutral
   at current header sizes. But the tracked test fixtures that the suites rewrite
   will need refreshing, and the autouse conftest fixtures added in
   PyAutoNerves#154 / PyAutoArray#474 keep that deterministic.
