# Bug in PyAutoGalaxy: the MGE bitwise sigma-ladder tests fail on

Type: test
Target: PyAutoGalaxy
Repos:
- PyAutoGalaxy
Difficulty: medium
Autonomy: safe
Priority: high
Status: formalised

Bug in PyAutoGalaxy: the MGE bitwise sigma-ladder tests fail on AVX-512 hardware. In PyAutoGalaxy, test__mge_model_from__default_sigma_list_is_bitwise_unchanged and test__mge_point_model_from__default_sigma_list_is_bitwise_unchanged in test_autogalaxy/analysis/test_model_util.py assert exact equality between two different numpy code paths. The PyAutoGalaxy implementation builds each sigma with a per-element scalar power, gaussian.sigma = 10 ** log10_sigma_list[i] at autogalaxy/analysis/model_util.py line 190, while the test builds its expectation with a vectorised 10 ** np.linspace(...). numpy does not guarantee the scalar and SIMD power loops agree bit for bit; on an x86-64-v4 / AVX-512 CPU they differ by 1 ULP at index 18, exactly the index pytest reports. Reproduced in isolation with numpy 2.4.6. The effect is cosmetic, not functional: the run identifier quantizes at RESOLUTION 1e-8 and this drift is ~1e-16 relative, so no identifier moves and no archived fit is orphaned. But the tests are green on GitHub runners and red on AVX-512 developer machines, so the regression guard added with PyAutoGalaxy#549 is not portable. Fix in PyAutoGalaxy by building the expected ladder element by element the way the implementation does, or by comparing with a tolerance far below the 1e-8 identifier resolution.

<!-- formalised by the Intake (Conception) Agent on 2026-08-05 from user-intake -->
