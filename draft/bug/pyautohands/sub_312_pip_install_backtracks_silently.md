# Sub-3.12 `pip install` silently backtracks to the stale pre-floor release

Type: bug
Target: pyautohands
Repos:
- PyAutoHands
- PyAutoLens
- PyAutoGalaxy
- PyAutoFit
- PyAutoArray
- PyAutoNerves
- PyAutoHeart
Difficulty: medium
Autonomy: human-required
Priority: high
Status: formalised

## Original request

> 2. Python 3.10 fails silently rather than loudly. The docs say a sub-3.12
> install "will fail with a no matching distribution error". It doesn't — on
> this box's default 3.10, pip backtracked and cheerfully installed autolens
> 2026.7.29.1 with no JAX and no warning. A user on 3.10 gets a quietly stale,
> JAX-less install. That's worse than the documented hard failure.
>
> two issues here, one python3.10 should not backtrap to an old version, so it
> should raise an error and if a user has to use python 3.10 (which might still
> work, they should end up on the latest verison. Same issue for 3.11 and 3.9 I
> assume

## Confirmed behaviour

Reproduced on real interpreters (3.9/3.10/3.11 venvs, pip 26.2.1), not simulated:

| Python | `pip install autolens` |
|--------|------------------------|
| 3.9    | silently installs the **2026.7.29.1** stack, exit 0 |
| 3.10   | same |
| 3.11   | same |
| 3.12   | 2026.8.17.1 (current) |

The 3.10 dry-run resolves `autolens/autogalaxy/autoarray/autofit/autonerves ==
2026.7.29.1` — no JAX, no warning, three weeks stale, predating the JAX-default
install (PyAutoLens#702).

**Root cause.** `2026.7.29.2` was the first release published with
`Requires-Python >=3.12`. Every release at or below `2026.7.29.1` was published
with `>=3.9` and remains a permanently valid pip candidate; PyPI metadata is
immutable, so raising a floor never invalidates the back catalogue. pip
backtracking to it is correct pip behaviour, not a defect in our
`pyproject.toml`.

**Lowering the floor is not the fix.** It would reverse the fully shipped
`python-312-floor` campaign (complete/2026/07/python-312-floor.md — five phases,
~15 merged PRs, the request being "remove support for anything below
python3.12"). CI is `3.12/3.13/3.14`, and 3.11 is additionally hard-blocked by
nufftax (0.4.x needs >=3.12; 0.6.x is broken against jax 0.10). The second half
of the original request — land 3.10 users on the latest version — is therefore
out of scope; the fix is the loud failure.

**Yanking is not the fix either.** ~330 autolens releases x 5 packages, and PyPI
exposes no bulk-yank API.

## Scope

### 1. Tombstone releases (@PyAutoHands)

Publish one extra release per package — `autolens`, `autogalaxy`, `autoarray`,
`autofit`, `autonerves` — at version `2026.7.29.1.post1`: **sdist only**,
`Requires-Python <3.12`, whose `setup.py` raises a clear message naming the
user's Python version, stating that older PyPI releases are unsupported and
months out of date, and telling them to upgrade to 3.12+.

All five are required: the exact `==` inter-pins mean tombstoning `autolens`
alone still leaves `pip install autogalaxy` backtracking.

One-off publish, never republished: `post1` stays the highest sub-3.12 candidate
forever, and every future `>=3.12` release is invisible below 3.12.

Mechanism control-tested against a local PEP 503 index with
`data-requires-python`, four scenarios:

| scenario | result |
|----------|--------|
| py3.10 `pip install X` | **loud failure** carrying our message |
| py3.12 `pip install X` | latest; tombstone excluded by `Requires-Python`, never seen |
| py3.10 `X==<old version>` | old release still installs — reproducibility preserved |
| py3.10 `--only-binary=:all:` | silently falls back to the old wheel — the one hole |

Document that last hole rather than pretending it does not exist.

### 2. Correct the false install-doc notes

`docs/installation/pip.md` in **PyAutoLens**, **PyAutoGalaxy** and **PyAutoFit**
each carry two wrong facts:

- "`pip install autolens` will fail with a \"no matching distribution\" error"
  — it does not; see the table above. Replace with what the tombstone actually
  produces once published.
- "We dropped support for Python 3.9, 3.10, and 3.11 in release `2026.4.5.3`" —
  wrong release. The April floor was reverted on 2026-04-30 (PyAutoLens
  `62f893a`), and `2026.5.1.4` … `2026.7.29.1` all shipped `>=3.9` again. The
  real cut is **`2026.7.29.2`**.

### 3. Close the Heart gap (@PyAutoHeart)

`skills/verify_install/verify_install.md` Check B already records the behaviour
— *"An unpinned 3.11 install is not evidence because pip may select an older
compatible release"* — and then tests only the pinned rejection. Extend Check B
so the **unpinned** sub-3.12 install is asserted to fail, so this cannot
silently return.

## Done when

- `pip install autolens` (and the four siblings) on 3.9/3.10/3.11 fails with the
  tombstone message instead of installing 2026.7.29.1.
- `pip install autolens` on 3.12/3.13/3.14 is byte-for-byte unaffected.
- `pip install autolens==<old version>` on 3.10 still resolves, so pinned
  historical installs keep working.
- The three `pip.md` notes describe real behaviour and name `2026.7.29.2`.
- Heart Check B fails if the unpinned sub-3.12 install ever succeeds again.

## Follow-up filed separately

`autoreduce 0.9` (published 2026-08-12, *after* phase 4b of the 3.12 floor
campaign) still declares `Requires-Python >=3.9,<=3.14.7` on PyPI — the floor
never reached the published artifact, and the `<=3.14.7` cap is unexplained.
Separate prompt, separate repo. (`autocti` on PyPI is stale at 2024 with
`>=3.7`, so it is not a live install path.)
