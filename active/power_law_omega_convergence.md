# Bound PowerLaw omega-series accuracy and cost

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Source: `component.power-law.series-vs-hyp2f1-divergence`
Issue: https://github.com/PyAutoLabs/autolens_profiling/issues/125

The JAX PowerLaw deflection path uses a fixed 20-term Tessore–Metcalf omega series while NumPy uses SciPy hyp2f1. The stable detector measures a reachable, science-affecting relative deflection error of 0.297 at factor 0.99.

Map accuracy and cost over public slope, ellipticity factor, angular coordinates, term policy, and actual prior reachability. Exercise eager, jit, reverse-mode grad, and vmap. Include cold-compile and warm-runtime cost plus at least one complete likelihood sensitivity probe.

A constant term-count bump is not an adequate answer: the initial sweep shows ordinary factors converge quickly but factor 0.99 can need more than 1280 terms, depending on slope. Evaluate statically binned lax.cond/lax.switch scans, and reject dynamic-loop candidates that lose reverse-mode differentiation.

Retain the stable finding ID. Do not modify PyAutoGalaxy in this task. Open a bounded source issue only if the evidence identifies a defensible policy that improves accuracy without imposing worst-case cost on ordinary galaxy shapes.
