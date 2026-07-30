# PyAutoFit docs/api/plot.rst lists three removed Plotter classes

Type: docs
Target: autofit
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: safe
Priority: low
Status: draft

The 2026-07-30 /audit_docs sweep (26/27 files clean) found one stale page:
`PyAutoFit/docs/api/plot.rst` still autosummary-lists `autofit.plot.NestPlotter`,
`MCMCPlotter` and `MLEPlotter`, which no longer exist — `autofit.plot` now
exposes the function-style API only (`corner_cornerpy`, `corner_anesthetic`,
`subplot_parameters`, `log_likelihood_vs_iteration`, `output_figure`). Update
the page to the functional API, mirroring how PyAutoGalaxy/PyAutoLens
`docs/api/plot.rst` present theirs.
