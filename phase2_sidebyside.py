"""Phase 2 side-by-side: author's original engines (tar) vs the al.pc port.

Usage: python phase2_sidebyside.py <experiment>
  parity      — dpsi mesh points + Matern reg-matrix parity (fast)
  oneshot     — one-shot joint inversion, both engines, c=2000/s=4
  iter_tar    — tar iterative, cold start, author demo-2 params
  iter_port   — port iterative, cold start, same params (Marquardt damping)
  iter_port_iddamp — port iterative, cold start, same params, identity damping patch
  iter_tar_c2000    — tar iterative, cold start, c=2000/s=4
  iter_port_c2000   — port iterative, cold start, c=2000/s=4

All experiments load the identical 200x200 demo dataset shipped in the tar and
write results to <OUT>/<experiment>.npz.
"""
import json
import logging
import sys
import time
from pathlib import Path

import numpy as np

TAR_ROOT = Path(
    "/tmp/claude-1000/-home-jammy-Code-PyAutoLabs/0100b7de-da01-4c18-a8b0-9d0080d5e07f/"
    "scratchpad/pt_jax_ref/for_qiuhan/lensing_potential_correction"
)
OUT = Path(
    "/tmp/claude-1000/-home-jammy-Code-PyAutoLabs/0100b7de-da01-4c18-a8b0-9d0080d5e07f/"
    "scratchpad/phase2_results"
)
OUT.mkdir(exist_ok=True)
sys.path.insert(0, str(TAR_ROOT))

logging.basicConfig(level=logging.INFO, format="%(message)s")

import autolens as al

from demo.common import (
    DATA_DIR,
    load_json,
    load_main_lens_galaxy,
    load_masked_imaging,
    load_source_factory,
)
from potential_correction import covariance_reg, dpsi_inv, dpsi_mesh, dpsi_src_inv
from potential_correction.iterative import IterFitDpsiSrcImaging as TarIterFit
from potential_correction.misc.non_classify import source_overlay_mesh_shape_from

AUTHOR_C, AUTHOR_S = 803465.5508338724, 0.44972885281383235
CAL_C, CAL_S = 2000.0, 4.0

metadata = load_json(DATA_DIR / "simulation_metadata.json")
SUB = metadata["lens"]["subhalo"]
SUB_CENTRE = tuple(SUB["centre"])

masked_imaging = load_masked_imaging()
lens_start = load_main_lens_galaxy()
source_shape = source_overlay_mesh_shape_from(masked_imaging, 2)
src_pixelization = al.Pixelization(
    mesh=al.mesh.KNearestNeighbor(pixels=int(np.prod(source_shape))),
    regularization=al.reg.Constant(coefficient=3.8),
)
src_image_mesh = al.image_mesh.Overlay(shape=source_shape)

true_subhalo = al.mp.NFWMCRLudlowSph(
    centre=SUB_CENTRE,
    mass_at_200=SUB["mass_at_200"],
    redshift_object=SUB["redshift_object"],
    redshift_source=SUB["redshift_source"],
)


def tar_dpsi_pix(c, s):
    return dpsi_inv.DpsiPixelization(
        mesh=dpsi_mesh.RegularDpsiMesh(factor=2),
        regularization=covariance_reg.MaternRegularization52(coefficient=c, scale=s),
    )


def port_dpsi_pix(c, s):
    return al.pc.DpsiPixelization(
        mesh=al.pc.RegularDpsiMesh(factor=2),
        regularization=al.reg.MaternKernel(coefficient=c, scale=s, nu=2.5),
    )


def metrics(points_yx, dkappa_rec, tag):
    dkappa_true = np.asarray(
        true_subhalo.convergence_2d_from(grid=al.Grid2DIrregular(values=points_yx))
    )
    corr = float(np.corrcoef(dkappa_rec, dkappa_true)[0, 1])
    peak = points_yx[int(np.argmax(dkappa_rec))]
    dist = float(np.hypot(peak[0] - SUB_CENTRE[0], peak[1] - SUB_CENTRE[1]))
    print(f"[{tag}] corr(dkappa)={corr:.4f} peak_dist={dist:.3f}\"", flush=True)
    return corr, dist, dkappa_true


def save(name, **arrs):
    np.savez(OUT / f"{name}.npz", **arrs)
    print(f"saved {OUT / name}.npz", flush=True)


def run_iter_tar(c, s, name):
    fit = TarIterFit(
        masked_imaging=masked_imaging,
        lens_start=lens_start,
        dpsi_pixelization=tar_dpsi_pix(c, s),
        src_pixelization=src_pixelization,
        src_image_mesh=src_image_mesh,
        gauge_constraints=True,
        n_iter=5,
        tol=1.0e-6,
        verbose=True,
    )
    t0 = time.time()
    s_opt, dpsi_opt = fit.solve_joint_optimization()
    dt = time.time() - t0
    pts = np.vstack(
        [fit.pair_dpsi_data_obj.ygrid_dpsi_1d, fit.pair_dpsi_data_obj.xgrid_dpsi_1d]
    ).T
    dk = np.asarray(fit.pair_dpsi_data_obj.hamiltonian_dpsi @ dpsi_opt)
    corr, dist, dk_true = metrics(pts, dk, name)
    print(f"[{name}] runtime {dt:.0f}s", flush=True)
    save(name, s_opt=s_opt, dpsi_opt=dpsi_opt, points=pts, dkappa=dk,
         dkappa_true=dk_true, corr=corr, dist=dist, runtime=dt)


def run_iter_port(c, s, name, identity_damping=False):
    if identity_damping:
        from autolens.potential_correction import dense_util as du

        def solve_identity(H, minus_gradient, mu, constraint_matrix=None, x=None, xp=np):
            H_d = du.as_dense(H, xp=xp)
            g = xp.asarray(minus_gradient)
            n_x = H_d.shape[0]
            H_lm = H_d + mu * xp.eye(n_x, dtype=H_d.dtype)
            if constraint_matrix is None:
                return xp.linalg.solve(H_lm, g)
            C = xp.asarray(constraint_matrix)
            n_c = C.shape[0]
            top = xp.concatenate([H_lm, C.T], axis=1)
            bottom = xp.concatenate([C, xp.zeros((n_c, n_c), dtype=H_d.dtype)], axis=1)
            H_kkt = xp.concatenate([top, bottom], axis=0)
            rhs = xp.concatenate([g, -(C @ xp.asarray(x))])
            return xp.linalg.solve(H_kkt, rhs)[:n_x]

        du.solve_lm_step_from = solve_identity
        print(f"[{name}] identity-damping patch ACTIVE", flush=True)

    fit = al.pc.IterFitDpsiSrcImaging(
        masked_imaging=masked_imaging,
        lens_start=lens_start,
        dpsi_pixelization=port_dpsi_pix(c, s),
        src_pixelization=src_pixelization,
        src_image_mesh=src_image_mesh,
        gauge_constraints=True,
        n_iter=5,
        tol=1.0e-6,
        verbose=True,
    )
    t0 = time.time()
    s_opt, dpsi_opt = fit.solve_joint_optimization()
    dt = time.time() - t0
    pts = np.vstack(
        [fit.pair_dpsi_data_obj.ygrid_dpsi_1d, fit.pair_dpsi_data_obj.xgrid_dpsi_1d]
    ).T
    dk = np.asarray(fit.pair_dpsi_data_obj.hamiltonian_dpsi @ dpsi_opt)
    corr, dist, dk_true = metrics(pts, dk, name)
    print(f"[{name}] runtime {dt:.0f}s", flush=True)
    save(name, s_opt=s_opt, dpsi_opt=dpsi_opt, points=pts, dkappa=dk,
         dkappa_true=dk_true, corr=corr, dist=dist, runtime=dt)


def main():
    exp = sys.argv[1]

    if exp == "parity":
        tar_fit = TarIterFit(
            masked_imaging=masked_imaging, lens_start=lens_start,
            dpsi_pixelization=tar_dpsi_pix(CAL_C, CAL_S),
            src_pixelization=src_pixelization, src_image_mesh=src_image_mesh,
            gauge_constraints=True, n_iter=1,
        )
        port_fit = al.pc.IterFitDpsiSrcImaging(
            masked_imaging=masked_imaging, lens_start=lens_start,
            dpsi_pixelization=port_dpsi_pix(CAL_C, CAL_S),
            src_pixelization=src_pixelization, src_image_mesh=src_image_mesh,
            gauge_constraints=True, n_iter=1,
        )
        pt = np.vstack([tar_fit.pair_dpsi_data_obj.ygrid_dpsi_1d,
                        tar_fit.pair_dpsi_data_obj.xgrid_dpsi_1d]).T
        pp = np.vstack([port_fit.pair_dpsi_data_obj.ygrid_dpsi_1d,
                        port_fit.pair_dpsi_data_obj.xgrid_dpsi_1d]).T
        print(f"mesh points: tar {pt.shape} port {pp.shape}", flush=True)
        if pt.shape == pp.shape:
            print(f"  max|points diff| = {np.max(np.abs(pt - pp)):.3e}", flush=True)
        rt = np.asarray(tar_fit.dpsi_regularization_matrix)
        rp = np.asarray(port_fit.dpsi_regularization_matrix)
        print(f"reg matrix: tar {rt.shape} port {rp.shape}", flush=True)
        if rt.shape == rp.shape:
            print(f"  max|reg diff| = {np.max(np.abs(rt - rp)):.3e}"
                  f"  (max|reg| = {np.max(np.abs(rt)):.3e})", flush=True)
        ht = np.asarray(tar_fit.pair_dpsi_data_obj.hamiltonian_dpsi.todense()
                        if hasattr(tar_fit.pair_dpsi_data_obj.hamiltonian_dpsi, "todense")
                        else tar_fit.pair_dpsi_data_obj.hamiltonian_dpsi)
        hp = np.asarray(port_fit.pair_dpsi_data_obj.hamiltonian_dpsi.todense()
                        if hasattr(port_fit.pair_dpsi_data_obj.hamiltonian_dpsi, "todense")
                        else port_fit.pair_dpsi_data_obj.hamiltonian_dpsi)
        if ht.shape == hp.shape:
            print(f"hamiltonian: max|diff| = {np.max(np.abs(ht - hp)):.3e}", flush=True)
        else:
            print(f"hamiltonian shapes differ: tar {ht.shape} port {hp.shape}", flush=True)

    elif exp == "oneshot":
        source_start_tar = load_source_factory()
        src = metadata["source"]
        comps = {
            comp["name"]: al.lp.Gaussian(
                centre=tuple(comp["centre"]),
                ell_comps=al.convert.ell_comps_from(
                    axis_ratio=comp["axis_ratio"], angle=comp["angle"]
                ),
                intensity=comp["intensity"],
                sigma=comp["sigma"],
            )
            for comp in src["components"]
        }
        source_galaxy = al.Galaxy(redshift=src["redshift"], **comps)
        source_start_port = al.pc.AnalyticSrcFactory(source_galaxy=source_galaxy)

        t0 = time.time()
        tar_fit = dpsi_src_inv.FitDpsiSrcImaging(
            masked_imaging=masked_imaging, lens_start=lens_start,
            source_start=source_start_tar,
            dpsi_pixelization=tar_dpsi_pix(CAL_C, CAL_S),
            src_pixelization=src_pixelization, src_image_mesh=src_image_mesh,
            adapt_image=None,
        )
        ev_tar = float(tar_fit.log_evidence)
        print(f"[oneshot_tar] log_evidence = {ev_tar:.6e} ({time.time()-t0:.0f}s)", flush=True)
        pts_t = np.vstack([tar_fit.pair_dpsi_data_obj.ygrid_dpsi_1d,
                           tar_fit.pair_dpsi_data_obj.xgrid_dpsi_1d]).T
        dk_t = np.asarray(tar_fit.pair_dpsi_data_obj.hamiltonian_dpsi @ tar_fit.best_fit_dpsi)
        corr_t, dist_t, _ = metrics(pts_t, dk_t, "oneshot_tar")

        t0 = time.time()
        port_fit = al.pc.FitDpsiSrcImaging(
            masked_imaging=masked_imaging, lens_start=lens_start,
            source_start=source_start_port,
            dpsi_pixelization=port_dpsi_pix(CAL_C, CAL_S),
            src_pixelization=src_pixelization, src_image_mesh=src_image_mesh,
        )
        ev_port = float(port_fit.log_evidence)
        print(f"[oneshot_port] log_evidence = {ev_port:.6e} ({time.time()-t0:.0f}s)", flush=True)
        pts_p = np.vstack([port_fit.pair_dpsi_data_obj.ygrid_dpsi_1d,
                           port_fit.pair_dpsi_data_obj.xgrid_dpsi_1d]).T
        dk_p = np.asarray(port_fit.pair_dpsi_data_obj.hamiltonian_dpsi @ port_fit.best_fit_dpsi)
        corr_p, dist_p, _ = metrics(pts_p, dk_p, "oneshot_port")

        print(f"[oneshot] evidence diff = {ev_tar - ev_port:.6e}", flush=True)
        if dk_t.shape == dk_p.shape:
            print(f"[oneshot] corr(dk_tar, dk_port) = "
                  f"{np.corrcoef(dk_t, dk_p)[0, 1]:.6f}  max|dpsi diff| = "
                  f"{np.max(np.abs(np.asarray(tar_fit.best_fit_dpsi) - np.asarray(port_fit.best_fit_dpsi))):.3e}",
                  flush=True)
        save("oneshot", ev_tar=ev_tar, ev_port=ev_port, dk_tar=dk_t, dk_port=dk_p,
             dpsi_tar=np.asarray(tar_fit.best_fit_dpsi), dpsi_port=np.asarray(port_fit.best_fit_dpsi),
             points=pts_t)

    elif exp == "iter_tar":
        run_iter_tar(AUTHOR_C, AUTHOR_S, "iter_tar")
    elif exp == "iter_port":
        run_iter_port(AUTHOR_C, AUTHOR_S, "iter_port")
    elif exp == "iter_port_iddamp":
        run_iter_port(AUTHOR_C, AUTHOR_S, "iter_port_iddamp", identity_damping=True)
    elif exp == "iter_tar_c2000":
        run_iter_tar(CAL_C, CAL_S, "iter_tar_c2000")
    elif exp == "iter_port_c2000":
        run_iter_port(CAL_C, CAL_S, "iter_port_c2000")
    elif exp == "iter_port_iddamp_c2000":
        run_iter_port(CAL_C, CAL_S, "iter_port_iddamp_c2000", identity_damping=True)
    else:
        raise SystemExit(f"unknown experiment {exp}")


if __name__ == "__main__":
    main()
