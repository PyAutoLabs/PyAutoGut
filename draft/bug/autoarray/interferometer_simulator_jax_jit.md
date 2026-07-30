# Interferometer simulator `@jax.jit` path — two remaining blockers

Type: bug
Target: autoarray
Repos:
- PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: normal

Follow-up to PyAutoArray#420, which fixed the **imaging** simulator's `@jax.jit`
path (5 sites; verified jitted-vs-eager agreement, autolens *and* autogalaxy). The
interferometer path was deliberately left out of that PR because it needs two
further changes with their own correctness surface.

Measured 2026-07-30 on the #420 branch, after registration
(`register_tracer_classes(tracer)`):

| Transformer | Result |
|---|---|
| `TransformerDFT` | `TypeError` at the jit boundary — `Interferometer` is not a valid JAX type |
| `TransformerNUFFT` | `TracerArrayConversionError` at `autoarray/operators/transformer.py:660`, inside `_forward_native` |

## Blocker 1 — `Interferometer` is not a registered pytree

Exactly the analogue of #420's site 5. `Imaging` gained
`_register_imaging_pytrees()` in `autoarray/dataset/imaging/simulator.py`, called
from `via_image_from` when `xp` is not NumPy. The interferometer simulator needs
the same, registering `Interferometer`.

Attribute split will differ from `Imaging` — `Interferometer.__init__` takes
`data` (`Visibilities`), `noise_map` (`VisibilitiesNoiseMap`), `uv_wavelengths`,
`real_space_mask`, `transformer_class`. Dynamic: `data`, `noise_map`. Aux:
`uv_wavelengths` (fixed observation geometry), `real_space_mask`,
`transformer_class`, plus whatever derived/cached attributes the instance carries
— **introspect `vars(dataset)` rather than trusting the `__init__` signature**,
which is how #420 got the `Imaging` split right (it revealed `grids`,
`sparse_operator`, `convolve_over_sample_size_*` that the signature does not
show).

Note #420 also had to `register_instance_pytree(Mask2D)` because
`Array2D.instance_flatten` emits `mask` as a child; `Visibilities` will likely
need the same treatment for whatever it carries.

## Blocker 2 — `TransformerNUFFT._forward_native` hard-converts to NumPy

`autoarray/operators/transformer.py` already has a **jittable** chunked branch
using `jax.lax.scan` + `jax.lax.dynamic_slice`. The non-chunked branch does not:

```python
img = image_native_2d[::-1, :].astype(np.complex128)

if self.chunk_size is None or self.chunk_size >= K:
    out = _nufftax.nufft2d2(self._x, self._y, img, self.eps, -1) * self._shift
    return np.array(np.asarray(out))          # <-- hard NumPy conversion
```

`np.array(np.asarray(out))` on a traced value raises
`TracerArrayConversionError`. The `parts`-accumulating loop below it is likely
the same class of problem (Python-level `for` over chunk offsets with NumPy
concatenation).

So `TransformerNUFFT` supports `jax.jit` only via its `lax.scan` path today,
contradicting `autolens_workspace/scripts/interferometer/simulator.py`'s
unqualified claim that it "supports `jax.jit` and scales to large UV sets".
Either thread `xp` through `_forward_native` so the non-chunked branch returns
`jnp`, or make the jittable branch the one taken under tracing.

## Scope

**In scope:** both blockers, until
`jax.jit(lambda t: sim.via_image_from(image=t.image_2d_from(grid=grid, xp=jnp)))`
returns an `Interferometer` with `jax.Array` visibilities, for **both**
`TransformerDFT` and `TransformerNUFFT`.

**Out of scope:** `TransformerNUFFTPyNUFFT` — the legacy pynufft backend is not
JAX-traceable and is not expected to be.

## Validation

Unit tests are NumPy-only across the stack, so validate with a parity script:

1. Jitted vs eager agreement for a fixed `noise_seed`, both transformers —
   complex visibilities, so compare real and imaginary parts.
2. Both `chunk_size=None` and a chunk size smaller than `K`, since they take
   different branches.
3. `test_autoarray/`, `test_autogalaxy/`, `test_autolens/` stay green (#420
   showed the `_xp` and `Mask2D` changes have stack-wide reach: 929 / 1009 / 488).
4. NumPy path byte-identical.

## Docs follow-up

Once this lands, the interferometer `__JAX Variant__` sections in
`autolens_workspace/scripts/interferometer/simulator.py` and
`autogalaxy_workspace/scripts/interferometer/simulator.py` — currently saying the
jitted wrap "does not currently work" (autolens_workspace#379) — can restore the
recipe **and uncomment the call** so CI executes it. Same for the
`TransformerNUFFT` jit claim, which should be qualified until blocker 2 is fixed.
