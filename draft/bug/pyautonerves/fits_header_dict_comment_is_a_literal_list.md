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
