"""One iterative evidence-grid point of subhalo_recovery_evidence.py, isolated per process.

Usage: python phase3_iter_point.py <log10_coefficient> <log10_scale> <out_dir>
Writes <out_dir>/iter_point_<log10c>_<log10s>.npz with evidence + recovery metrics.
"""
import sys
from pathlib import Path

import numpy as np

import autolens as al

log10_c, log10_s = float(sys.argv[1]), float(sys.argv[2])
out_dir = Path(sys.argv[3])

grid = al.Grid2D.uniform(shape_native=(120, 120), pixel_scales=0.05, over_sample_size=2)
psf = al.Convolver.from_gaussian(shape_native=(11, 11), sigma=0.05, pixel_scales=0.05)
simulator = al.SimulatorImaging(
    exposure_time=840.0, psf=psf, background_sky_level=0.1,
    add_poisson_noise_to_data=True, noise_seed=1,
)
subhalo_centre = (1.41, 0.0)
true_subhalo = al.mp.NFWMCRLudlowSph(
    centre=subhalo_centre, mass_at_200=1.0e10, redshift_object=0.2, redshift_source=0.6
)
lens_true = al.Galaxy(
    redshift=0.2,
    mass=al.mp.Isothermal(
        centre=(0.0, 0.0), einstein_radius=1.4,
        ell_comps=al.convert.ell_comps_from(axis_ratio=0.9, angle=0.0),
    ),
    subhalo=true_subhalo,
)
source_true = al.Galaxy(
    redshift=0.6,
    bulge0=al.lp.Gaussian(centre=(0.0, 0.0), ell_comps=al.convert.ell_comps_from(axis_ratio=0.6, angle=45.0), intensity=5.0, sigma=0.15),
    bulge1=al.lp.Gaussian(centre=(0.0, 0.4), ell_comps=al.convert.ell_comps_from(axis_ratio=0.4, angle=135.0), intensity=3.0, sigma=0.1),
)
dataset = simulator.via_tracer_from(tracer=al.Tracer(galaxies=[lens_true, source_true]), grid=grid)
mask_array = al.pc.util.arc_mask_from(
    np.asarray(dataset.signal_to_noise_map.native), threshold=3.0, ignore_size=25, ext_size=5
)
masked_imaging = dataset.apply_mask(mask=al.Mask2D(mask=mask_array, pixel_scales=dataset.pixel_scales))

lens_smooth = al.Galaxy(redshift=0.2, mass=lens_true.mass)
grid_slim = masked_imaging.grid.slim
source_shape = (
    int(float(grid_slim[:, 0].max() - grid_slim[:, 0].min()) / 0.05 / 2.0),
    int(float(grid_slim[:, 1].max() - grid_slim[:, 1].min()) / 0.05 / 2.0),
)
src_pixelization = al.Pixelization(
    mesh=al.mesh.KNearestNeighbor(pixels=int(np.prod(source_shape))),
    regularization=al.reg.Constant(coefficient=3.8),
)
src_image_mesh = al.image_mesh.Overlay(shape=source_shape)

iter_fit = al.pc.IterFitDpsiSrcImaging(
    masked_imaging=masked_imaging,
    lens_start=lens_smooth,
    dpsi_pixelization=al.pc.DpsiPixelization(
        mesh=al.pc.RegularDpsiMesh(factor=2),
        regularization=al.reg.MaternKernel(coefficient=10.0**log10_c, scale=10.0**log10_s, nu=2.5),
    ),
    src_pixelization=src_pixelization,
    src_image_mesh=src_image_mesh,
    gauge_constraints=True,
    n_iter=8,
)
s_opt, dpsi_opt = iter_fit.solve_joint_optimization()
evidence = float(iter_fit.log_evidence())

points = np.vstack(
    [iter_fit.pair_dpsi_data_obj.ygrid_dpsi_1d, iter_fit.pair_dpsi_data_obj.xgrid_dpsi_1d]
).T
dkappa = np.asarray(iter_fit.pair_dpsi_data_obj.hamiltonian_dpsi @ dpsi_opt)
dkappa_true = np.asarray(true_subhalo.convergence_2d_from(grid=al.Grid2DIrregular(values=points)))
corr = float(np.corrcoef(dkappa, dkappa_true)[0, 1])
peak = points[int(np.argmax(dkappa))]
dist = float(np.hypot(peak[0] - subhalo_centre[0], peak[1] - subhalo_centre[1]))

np.savez(
    out_dir / f"iter_point_{log10_c:g}_{log10_s:g}.npz",
    log10_c=log10_c, log10_s=log10_s, evidence=evidence, corr=corr, dist=dist,
    dkappa=dkappa, dpsi_opt=dpsi_opt,
)
print(f"POINT log10c={log10_c:g} log10s={log10_s:g} evidence={evidence:.6e} corr={corr:.4f} dist={dist:.3f}", flush=True)
