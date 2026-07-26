## delaunay-frozen-tables-gradient
- completed: 2026-07-26
- branch: `claude/rectangular-mesh-gradients-mh1j0z` (PyAutoArray + autolens_workspace_test + autolens_workspace_developer; PR/merge pending with the rest of the session's mesh-gradients work — no issue was opened, the task was conceived and executed in the same session)
- key commits: PyAutoArray `feat: unlock jax.grad through the Delaunay mesh via frozen integer tables` + `docs: state the sense in which the Delaunay mesh is autodifferentiable`; autolens_workspace_test `test: jax_grad FD certification for the Delaunay mesh`
- verdict: SHIPPED — the Delaunay mesh is autodifferentiable (a.e.-exact frozen-tables gradient)
- summary: |
    The 2026-07-09 audit's "Delaunay is hard-undifferentiable" verdict was
    stale: the visibility-walk refactor had moved every differentiable
    quantity (point location, barycentric weights, dual areas, split points)
    in-graph, leaving the host qhull `pure_callback` returning only int32
    connectivity tables. Those tables are piecewise-constant in the vertex
    positions — their true derivative is zero between triangle-flip events —
    so wrapping the callback input in `jax.lax.stop_gradient` (one line in
    `_jax_delaunay_tables`) yields the EXACT almost-everywhere derivative,
    not an approximation. Values are bit-identical (primal untouched): the
    jax_likelihood delaunay regression literal passes unchanged.

    Certification (new `autolens_workspace_test/scripts/imaging/jax_grad/delaunay.py`,
    production shape: Hilbert image mesh + circle edge zeroing +
    reg.AdaptSplit(0.1, 10), 14-param truth-centred lens): all params live,
    eager==jit, FD-step-sweep with lens light at 1e-8..1e-10 and mass/shear
    at 1e-5..2e-3 (documented rtol=1e-2 — the scatter is FD steps straddling
    flip events, the measure-zero jump seams where no method has a gradient;
    AD differentiates the branch the point is on).

    THE SENSE IN WHICH IT IS AUTODIFFERENTIABLE (now in the Delaunay class
    docstring): ReLU-network territory — piecewise-smooth, smooth within
    each triangulation topology, measure-zero jump discontinuities at flips.
    Contrast the kernel-CDF rectangular meshes: C-infinity by construction,
    no seams — still the cleanest gradient-inference choice; Delaunay is the
    scientifically exact piecewise-smooth alternative.

    REMAINING TRADE (documented, not fixed): the tables callback is
    `vmap_method="sequential"` — one host qhull call per vmap lane — so the
    KNN meshes keep the batched-throughput niche until the callback is
    batched (delaunay_research.md option B territory).

    Lore: the audit README's "Why Delaunay gradients are infeasible" section
    assessed the PRE-walk architecture (callback returned float split_points
    /mappings, where freezing would have dropped real terms); its point 3
    (the frozen gradient is the correct a.e. derivative) is what this ships.
    Probe pattern for the unlock: monkeypatch stop_gradient, value_and_grad,
    FD sweep — 30 minutes from hypothesis to evidence.

## Original prompt

# Delaunay frozen-tables gradient — unlock jax.grad with stop_gradient on the tables callback

Type: feature
Target: autoarray
Repos:
- PyAutoArray
- autolens_workspace_test
- autolens_workspace_developer
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## The finding (probed 2026-07-26, wrap-up of the mesh-gradients assessment)

The Delaunay mesh's "hard-undifferentiable" verdict (2026-07-09 audit) is
**stale**: since the visibility-walk landed, the JAX path
(`jax_delaunay` in `autoarray/inversion/mesh/interpolator/delaunay.py`) runs
everything differentiable **in-graph** — point location, barycentric weights,
dual areas, split points — and the `pure_callback` returns only int32
triangulation tables (`simplices`, `neighbors`, `vertex_simplex`). Those
tables are piecewise-constant in the vertex positions (their true derivative
is zero between re-wiring events), so freezing them is NOT an approximation:
it is the exact almost-everywhere derivative of the likelihood.

The unlock is one line — the callback input just needs to be excluded from
differentiation:

```python
def _tables_stopgrad(points):
    return _orig_tables(jax.lax.stop_gradient(points))
```

Probe (monkeypatch, jax_test 14-param fiducial, full production shape:
Hilbert image mesh + circle edge zeroing + `reg.AdaptSplit(0.1, 10)`):

- `value_and_grad` finite, non-zero, mass/shear live on all 14 params.
- eager == jit (rtol 1e-10).
- FD-step-sweep: **median rel err 9.6e-6, max 2.1e-3** (worst:
  `mass.ell_comps_0`) — the residual scatter on mass params is FD stepping
  across re-wiring events (measure-zero discontinuities, same class as the
  KNN meshes' neighbour swaps and the certified branch flips of
  PyAutoArray#377), while lens-light params match at 1e-8–1e-10.

Probe script pattern: `jax_grad/knn.py` composition with
`mesh=al.mesh.Delaunay(pixels, zeroed_pixels)`; the monkeypatch above.

## Task

1. Ship the unlock in `_jax_delaunay_tables` (stop_gradient on `points`
   before the callback — or an equivalent `custom_jvp` zero rule if
   stop_gradient interacts badly with anything). Values are bit-identical
   (the primal is untouched); only differentiation behaviour changes, from
   "raises" to "exact a.e. gradient".
2. Certification: add a Delaunay variant to
   `autolens_workspace_test/scripts/imaging/jax_grad/` (mirror `knn.py`;
   FD-step-sweep, documented tolerance for the re-wiring FD scatter —
   probe suggests rtol 3e-3 or per-param exclusions à la the os_pix=1
   einstein_radius precedent). Re-run the delaunay jax_likelihood scripts
   (imaging, interferometer, datacube, multi) to confirm values unchanged.
3. Update `imaging/jax_grad/knn.py`'s docstring + the audit README's
   Delaunay narrative ("Why Delaunay gradients are infeasible today" —
   points 1–2 are superseded; point 3's a.e. analysis is what the probe
   confirms) — partially done 2026-07-26 (row + findings-log updated;
   the section prose still says infeasible).
4. Samplers caveat to document: gradient-based searches see measure-zero
   value discontinuities at re-wiring events (the interpolant jumps when a
   containing triangle's diagonal flips) — same practical class as the
   XLA branch flips (#377), but geometric in origin and mesh-density
   dependent.

## Why this matters

Delaunay is the flagship source reconstruction (exact spatial locality,
every vertex guaranteed simplex membership — the property whose absence
sank the KNN-barycentric wildcard, PyAutoArray#317). This makes it
gradient-capable at zero science cost. The remaining Delaunay-vs-KNN trade
is batched throughput only: the tables callback is
`vmap_method="sequential"` (one host qhull call per vmap lane), so KNN
meshes stay preferable for heavily-vmapped samplers until the callback is
batched (delaunay_research.md option B territory).

## Constraints

- The unlock must not change values (it cannot — primal untouched); the
  jax_likelihood regression literals are the gate.
- Library unit tests numpy-only; JAX validation via workspace_test jax_grad.
