# Imaging likelihood hazards

This directory contains imaging-specific fixtures and cells that wrap
the reusable detectors in [`scripts/misc/hazards/`](../../misc/hazards/README.md)
around a complete likelihood.

`pixelization.py` is the first tier-2 cell. It uses an in-memory 7x7 imaging
dataset, an Isothermal lens and a 3x3 rectangular source with constant
regularization. The bounded scan measures active-set support transitions,
matrix-floor scale, NumPy/JAX solver divergence, and the circular-profile
orientation degeneracy. Reusable detector logic remains in `misc/hazards`.

Run the cell directly to write its raw probe, or run the shared scanner to
write semantic findings:

```bash
python scripts/imaging/hazards/pixelization.py
python scripts/misc/hazards/scan.py --subject likelihood
```
