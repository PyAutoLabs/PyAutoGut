# Refactor: remove the pynufft dependency from the PyAuto stack entirely

Type: refactor
Target: PyAutoArray
Repos:
- PyAutoArray
- PyAutoGalaxy
- autogalaxy_workspace
- PyAutoLens
- autolens_workspace
- autolens_workspace_test
- pyautohands
- PyAutoHeart
Difficulty: too-large
Autonomy: supervised
Priority: normal
Status: formalised

Refactor: remove the pynufft dependency from the PyAuto stack entirely and restructure the NUFFT surface onto nufftax alone. Investigate first, then restructure — the issue owns the investigation. Current state: pynufft is an optional dependency of PyAutoArray, PyAutoGalaxy and PyAutoLens; it backs aa.TransformerNUFFTPyNUFFT in autoarray/operators/transformer.py; and it carries three different pins across the org — unpinned in the optional extras, ==2022.2.2 in the PyAutoArray dev extra, ==2025.1.1 in PyAutoHeart workspace-validation.yml and three places in PyAutoHands release.yml. The 2022.2.2 pin is already broken: it calls scipy.linalg.pinv2, removed in SciPy 1.7, while PyAutoArray allows scipy<=1.17.1, so pip install -e PyAutoArray[dev] — the command in PyAutoArray AGENTS.md — yields three failing TransformerNUFFTPyNUFFT tests. CI is blind to it because the reusable lib-tests workflow installs the optional extra, where pynufft is unpinned and resolves to 2025.2.1. The JAX-native nufftax-backed aa.TransformerNUFFT is already the default for Interferometer and the documented recommendation everywhere; TransformerNUFFTPyNUFFT survives only as the documented non-JAX fallback. Investigate before deciding: does nufftax cover the non-JAX numpy path the pynufft fallback exists to serve, or does removal mean non-JAX users fall back to TransformerDFT; do the three pynufft tests in test_autoarray/operators/test_transformer.py become nufftax tests or get deleted; how much replacement code does the nufftax path need, and can the _patch_nufftax_batchers rank-guard shim for nufftax <0.7 be retired at the same time. Restructuring then covers deleting the class and its exports from autoarray __init__ and type.py, the autogalaxy and autolens re-exports, workspace prose in autolens_workspace and autogalaxy_workspace start_here, simulator, using_jax and linear-light-profile modeling scripts plus generated markdown, the autolens_workspace_test scripts/interferometer/nufft.py comparison script, and the pynufft install lines in the Heart and Hands workflows.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
