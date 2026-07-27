- issue: none (same-session continuation of the 2026-07-27 /wake_up red-jobs sweep)
- prs: PyAutoLens#658 — MERGED
- summary: |
    SECOND cause of PyAutoHands/python_matrix being red, pre-existing (present
    in the 2026-07-20 and 2026-07-27 runs) and MISSED in the morning digest
    because `gh run view | head -25` truncated the job list to the smoke jobs.

    unit_tests (3.9, PyAutoLens) and (3.10, PyAutoLens): 5 potential_correction
    tests died with ModuleNotFoundError: No module named 'jax', from
    PyAutoArray inversion_interferometer_util.py:654 in
    from_nufft_precision_operator, reached via the public
    Interferometer.apply_sparse_operator (dataset.py:280).

    Diagnosis: the sparse-operator subsystem is JAX-ONLY BY DESIGN —
    InterferometerSparseOperator has 3 jax sites (FFT kernel via jax.numpy,
    apply_operator, and curvature_matrix_diag_from using jax.lax +
    jax.ops.segment_sum); the imaging counterpart has 8+ and types a field as
    "jax.Array". autonerves[jax] gates jax to python>=3.11. The 5 failing cases
    are exactly those calling apply_sparse_operator() — i.e. tests OF the JAX
    feature, running in matrix legs that deliberately have no jax. A test
    PLACEMENT problem, not a library bug.

    A numpy fallback was considered and REJECTED: it would mean reimplementing
    the whole sparse-operator path (segment_sum -> np.add.at/bincount, dropping
    lax), a substantial new feature with numerical-parity risk, to serve Pythons
    the feature is not gated for.

    Fixed with a find_spec-based skipif on exactly those 5 cases, matching the
    pytest.importorskip idiom already in test_autolens/interop/test_coolest.py.
    Also restores the standing "library unit tests are numpy-only" rule here.
- verification: |
    jax present -> 9 passed, 0 skipped. jax absent (find_spec shimmed to None)
    -> 4 passed, 5 skipped — exactly the 5 CI failures, no more, no less.
- traps: |
    TRAP: skip PER-TEST, not module-level. The same two files hold dense-route
    cases that are numpy-only and MUST keep running on 3.9/3.10 — that is what
    those legs exist to prove. A module-level importorskip would have silently
    dropped that coverage while looking like a fix.
    TRAP: `gh run view --job <id> --json conclusion` returns the RUN's
    conclusion, not the job's. It reported "failure" for a job whose steps were
    all green. Use `gh api .../runs/<id>/jobs` and read per-job conclusions.
    TRAP: the OTHER half of python_matrix red (nufftax on the 3.11 leg) was
    already fixed upstream by autolens_workspace#351, which merged AFTER the
    failing run. Verified by dispatch rather than re-fixed.
    OPEN: only 2 of 29 scripts invoking interferometer/simulator.py carry a
    nufftax guard. The other 27 are not smoke-listed so they do not take CI red,
    but they break for any py3.11 user. Not fixed.
