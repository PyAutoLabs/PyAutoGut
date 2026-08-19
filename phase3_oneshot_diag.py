"""Diagnostics on the one-shot evidence surface: recovery metrics at selected points.

For each (coefficient, scale) probed: fast-path solution -> dkappa -> corr/dist,
plus corr after Gaussian-smoothing the recovered dkappa on the native dpsi mesh
(tests whether the low corr at the evidence max is roughness, not mislocation).
"""
import sys
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter

import autolens as al
from autolens.potential_correction import dense_util

OUT = Path(__file__).resolve().parent

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
source_start = al.pc.AnalyticSrcFactory(source_galaxy=source_true)
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

ref_fit = al.pc.FitDpsiSrcImaging(
    masked_imaging=masked_imaging,
    lens_start=lens_smooth,
    source_start=source_start,
    dpsi_pixelization=al.pc.DpsiPixelization(
        mesh=al.pc.RegularDpsiMesh(factor=2),
        regularization=al.reg.MaternKernel(coefficient=2000.0, scale=4.0, nu=2.5),
    ),
    src_pixelization=src_pixelization,
    src_image_mesh=src_image_mesh,
)
_ = ref_fit.log_evidence

data = np.asarray(masked_imaging.data)
noise = np.asarray(masked_imaging.noise_map)
mapping = np.asarray(ref_fit.mapping_matrix)
src_reg = np.asarray(ref_fit.src_regularization_matrix)
pair = ref_fit.pair_dpsi_data_obj
points = np.vstack([pair.ygrid_dpsi_1d, pair.xgrid_dpsi_1d]).T
n_src = src_reg.shape[0]
dpsi_linear_obj = al.pc.DpsiLinearObj(mask=pair.mask_dpsi, points=points)
hamiltonian = pair.hamiltonian_dpsi

inv_var = 1.0 / noise**2
curvature = mapping.T @ (mapping * inv_var[:, None])
data_vector = mapping.T @ (inv_var * data)
noise_term = -0.5 * float(np.sum(np.log(2 * np.pi * noise**2)))

dkappa_true = np.asarray(true_subhalo.convergence_2d_from(grid=al.Grid2DIrregular(values=points)))
mask_dpsi = np.asarray(pair.mask_dpsi)


def to_native(vec):
    out = np.zeros(mask_dpsi.shape)
    out[~mask_dpsi] = vec
    return out


def metrics(vec):
    corr = float(np.corrcoef(vec, dkappa_true)[0, 1])
    peak = points[int(np.argmax(vec))]
    dist = float(np.hypot(peak[0] - subhalo_centre[0], peak[1] - subhalo_centre[1]))
    return corr, dist


true_native = to_native(dkappa_true)
probes = [
    (1000.0, 1.0, "one-shot evidence MAX"),
    (2000.0, 4.0, "hand-calibrated (smoke)"),
    (1.0e5, 10**-0.2, "iterative-leader params"),
    (10.0**3.5, 10**0.4, "ridge probe"),
]
for c, s, tag in probes:
    dpsi_reg = np.asarray(
        al.reg.MaternKernel(coefficient=c, scale=s, nu=2.5).regularization_matrix_from(
            linear_obj=dpsi_linear_obj
        )
    )
    res = dense_util.log_evidence_from_fixed_curvature(
        curvature_matrix=curvature, data_vector=data_vector, data_slim=data,
        mapping_matrix=mapping, inv_var=inv_var, noise_term=noise_term,
        src_reg_matrix=src_reg, dpsi_reg_matrix=dpsi_reg,
    )
    dpsi_sol = np.asarray(res["solution"])[n_src:]
    dkappa = np.asarray(hamiltonian @ dpsi_sol)
    corr, dist = metrics(dkappa)
    sm_native = gaussian_filter(to_native(dkappa), sigma=2.0)
    sm = sm_native[~mask_dpsi]
    corr_sm, dist_sm = metrics(sm)
    print(
        f"[{tag}] c={c:g} s={s:g}: evidence={float(res['evidence']):.4f} "
        f"corr={corr:.4f} dist={dist:.3f}\" | smoothed(sig=2px): corr={corr_sm:.4f} dist={dist_sm:.3f}\""
    )
