Sub-3.12 `pip install` of the PyAuto stack no longer backtracks silently to the
last pre-floor release. It now fails with an explanation naming the user's own
Python version.

- parent issue: https://github.com/PyAutoLabs/PyAutoHands/issues/238 (closed
  2026-08-19)
- phase 1 (mechanism + publish): PyAutoHands#240 (`2ddab4a`), PyAutoHands#242
  (`8724b05`)
- phase 2 (docs + the check that should have caught it): PyAutoLens#706
  (`84c4602`), PyAutoGalaxy#576 (`4577a01`), PyAutoFit#1507 (`8ccb4e0`),
  PyAutoHeart#155 (`7557182`), autogalaxy_assistant#17 (`85f7e13`)
- follow-up filed: PyAutoReduce#71

## The bug

Reproduced on real 3.9/3.10/3.11 venvs with pip 26.2.1 before any change: all
three resolved `autolens/autogalaxy/autoarray/autofit/autonerves ==
2026.7.29.1` — exit 0, no warning, three weeks stale, no JAX. The docs promised
a "no matching distribution" error that never happened.

Not a defect in our metadata. `2026.7.29.2` was the first release published
declaring `Requires-Python >=3.12`; everything at or below `2026.7.29.1` was
published with `>=3.9`, and PyPI metadata is immutable. **Raising a floor never
retracts a back catalogue** — this is the durable lesson, and it applies to
every future floor bump.

## The fix

One sdist-only release per package at `2026.7.29.1.post1`, `Requires-Python
<3.12`, whose build raises. It outranks every sub-floor candidate and is
invisible at or above the floor. Built by `PyAutoHands/autohands/tombstone.py`,
published by a `workflow_dispatch`-only workflow (the PyPI tokens are Actions
secrets and stay there; the real index additionally requires a typed confirm
phrase). Deliberately **not** wired into `release.yml` — one-off, since every
future release declares `>=3.12` and is invisible below the floor.

Verified against the real PyPI index on real interpreters: 3.9/3.10/3.11 fail
loudly for all five packages; 3.12 still resolves `2026.8.17.1`; and
`autolens==2026.7.29.1` still resolves on 3.10, so reproducing an old result was
never collateral damage.

## Rejected, with reasons

- **Lower the floor so 3.10 gets the latest** (half of the original request):
  reverses the shipped `python-312-floor` campaign; CI is 3.12/3.13/3.14 and
  3.11 is hard-blocked by nufftax.
- **Yank the pre-floor catalogue**: ~330 releases per package, and PyPI exposes
  no bulk-yank API.

## What the sweep found beyond the brief

- **The docs described a plan as though it had happened.** "Pre-`2026.4.5.3`
  releases have been yanked, so they will not install" — 396 of 421 `autolens`
  releases are live. Someone intended to yank the catalogue so resolver fallback
  would be blocked, wrote the docs for that world, and the yank never ran. That
  is why the fallback the page called blocked was wide open.
- **Wrong cut release**: docs said `2026.4.5.3`; that floor was reverted
  2026-04-30 (`62f893a`) and `2026.5.1.4` … `2026.7.29.1` all shipped `>=3.9`
  again. Real cut: `2026.7.29.2`.
- **A fifth surface**: `autogalaxy_assistant` told the assistant 3.11 "fails
  with no matching distribution rather than silently resolving to an ancient
  version" — the exact inverse of reality.
- **Support range**: `overview.md` in the three libraries said "3.12 - 3.13"
  though 3.14 has been a required matrix leg since 2026-07-31.

## Checked and deliberately NOT changed

- PyAutoCTI's "Python 3.12 or 3.13" is accurate — its classifiers stop at 3.13,
  so it genuinely was never promoted to 3.14. Editing it would have introduced a
  false claim.
- Workspace `AGENTS.md` files claiming CI gates on "3.12 and 3.13" are accurate:
  PyAutoHeart's reusable `smoke-tests.yml` defaults to `["3.12", "3.13"]` and
  none override it.

## The gap that let it live

PyAutoHeart Check B had the failure written into its own description — *"An
unpinned 3.11 install is not evidence because pip may select an older
compatible release"* — and then tested only the pinned rejection. Install
verification was green throughout. `check_b_unpinned_refused` now requires the
unpinned install to be refused, and a success reads `the sub-floor backtrack is
back`. The classifier was validated against real captured pip output in both
directions, not hand-written strings.

## Traps hit, worth remembering

- `--no-isolation` needs setuptools *installed*, and Python 3.12 dropped it from
  the default environment. It did not reproduce locally because this machine's
  3.12 carries setuptools; a bare 3.12 venv does not. **The TestPyPI rehearsal
  caught it at build, before any upload** — no version was burned.
- The tenant firewall rejected `url="https://github.com/PyAutoLabs"` in the
  generated `setup()`. Removing the field beat allowlisting the file.
- Editing an assistant wiki body requires `--write-provenance`; `content_sha256`
  binds prose to the pinned-commit claim and the check fails otherwise, by
  design.
- test.pypi.org's JSON API lagged the upload — a first read showed 4 of 5
  packages and looked like a partial publish. Resolution against the simple
  index is the reliable check, not the JSON API.

## Known limit, documented not hidden

`pip install --only-binary=:all:` skips sdists, steps past the tombstone, and
installs the old wheel silently. No packaging mechanism closes it short of
retracting the back catalogue. Stated plainly in all three install pages.

## Original prompt

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
