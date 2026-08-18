# `@PyAutoFit` `TransformedMessage.logpdf`/`pdf` omit the transform Jacobian

Type: bug
Target: priors
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised — issue filed (PyAutoFit#1498), awaiting adjudication

Found 2026-08-18 while implementing the #1497 property sweep (prompt
`bug/priors/09`). Same failure *shape* as census finding A4 (#1331-04): a
generic-interface density path is silently wrong while the direct paths are
right.

## The finding

`TransformedMessage` inherits `MessageInterface.logpdf` (the natural-parameter
path). Its overrides forward `natural_parameters`, `calc_log_base_measure` and
`to_canonical_form` to the base message — `to_canonical_form` is
`@transform`-decorated, so the physical input is mapped to base coordinates —
but **no `log_det` change-of-variables term is ever added**. `logpdf(x)` at a
physical `x` therefore returns the *base-space* density at the mapped point,
not the physical density. `TransformedMessage.factor(x)` does it correctly
(`base.logpdf(transform(x)) + log_det`).

Reproduction on `main` @ `7d4d931` (exact numbers):

- `af.UniformPrior(0,1).message.logpdf(0.7)` = −1.05644 (physical density is
  1.0 → expect 0.0); `factor(0.7)` = 0.0 ✓
- `∫ exp(logpdf)` over [0,1] = **0.282095 = 1/(2√π)**, not 1.0;
  `∫ exp(factor)` = 1.000000 ✓
- `LogUniformPrior(0.01, 100)`: generic-path pdf integrates to **15.83**.

Every `TransformedMessage`-wrapped prior (Uniform, LogUniform, LogGaussian) is
affected. `NormalMessage` / `TruncatedNormalMessage` priors are not.
`value_for`, `cdf`, `log_prior_from_value` and `factor` are all verified
correct — sampling and MCMC/MLE log-priors are unaffected; the exposure is
anything treating `transformed_message.pdf()` as a physical density.

## Doc contradiction

The `composed_transform.py` module docstring (added by #1334) claims `logpdf`
accumulates the log-Jacobian. The code does not. Either the docstring states
the intended contract (then `logpdf` needs the `log_det` term) or `logpdf` is
deliberately base-space for EP message arithmetic (then the docstring and
`pdf()` are misleading and should say so).

## What adjudication needs

1. Inventory callers of `TransformedMessage.logpdf`/`pdf` vs `factor` —
   especially whether any EP projection / `log_norm` path evaluates `logpdf`
   on transformed messages at physical coordinates.
2. `logpdf_gradient` returns the base `log_likelihood` with a
   Jacobian-corrected *gradient* (value base-space, gradient physical) — a
   third convention to settle in the same pass.
3. Decide: add `log_det` to the generic path, or document base-space `logpdf`
   as the contract and fix the module docstring + `pdf()`.

The #1497 property tests assert the physical density via `factor` and cite
#1498 at the site (`physical_log_density` helper in
`test_autofit/mapper/prior/test_prior_properties.py`); tighten them to
`logpdf` once resolved.

## Sequencing

Adjudicate alongside the parked single-source-density design (census C1/C4,
prompts `bug/priors/12`+`13`) — this is a fourth density-convention divergence
of exactly the kind that design exists to eliminate. The 12+13 design issue
should cite PyAutoFit#1498 as fresh evidence.
