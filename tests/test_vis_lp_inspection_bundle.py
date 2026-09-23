"""A bundle can combine vis_lp-only normal results with a separate SED tree."""

import csv
import importlib.util
import os
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image

from test_catalogue_latent_columns import (
    CATALOGUE_SCRIPTS,
    SAMPLE,
    _write_result,
    pipeline_config,  # noqa: F401
)


PROJECT_ROOT = Path(__file__).parent.parent


def _image(path: Path, colour=(20, 30, 40)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", (16, 12), colour).save(path)


def _result_dir(root: Path, stage: str, search: str) -> Path:
    result = root / stage / search / "result"
    (result / "image").mkdir(parents=True)
    (result / "files").mkdir()
    return result


def test_vis_lp_images_do_not_require_vis_pix_and_use_separate_sersic_root(tmp_path):
    from scripts.tools.build_inspect import process_dataset

    lens = "TileAAA"
    normal = tmp_path / "output" / lens
    vis_lp = _result_dir(normal, "initial_lens_model", "vis_lp")
    for name in ("fit.png", "image_with_positions.png", "rgb.png"):
        _image(vis_lp / "image" / name)
    (vis_lp / "files" / "coolest.json").write_text('{"stage": "vis_lp"}')

    sersic = tmp_path / "output_sed" / lens
    sersic_result = _result_dir(sersic, "sersic_lens_model", "vis")
    _image(sersic_result / "image" / "fit.png", colour=(50, 60, 70))
    (sersic_result / "files" / "coolest.json").write_text('{"stage": "sersic"}')

    dataset = tmp_path / "dataset"
    _image(dataset / lens / "segmentation.png")
    inspect = tmp_path / "inspect"

    assert (
        process_dataset(
            normal,
            dataset,
            inspect,
            sersic_dataset_dir=sersic,
            initial_search_name="vis_lp",
        )
        == "built"
    )
    products = {path.name for path in (inspect / lens).iterdir()}
    assert products == {
        "vis_lp_fit.png",
        "vis_lp_image_with_positions.png",
        "rgb.png",
        "segmentation.png",
        "coolest_vis_lp.json",
        "fit_sersic.png",
        "coolest_sersic.json",
    }
    assert "vis_pix_fit.png" not in products
    assert "coolest.json" not in products
    assert (
        process_dataset(
            normal,
            dataset,
            inspect,
            sersic_dataset_dir=sersic,
            initial_search_name="vis_lp",
        )
        == "already"
    )


def test_vis_lp_missing_optional_asset_skips_one_lens_and_recovers(tmp_path, capsys):
    from scripts.tools.build_inspect import process_dataset

    lens = "TileMissing"
    normal = tmp_path / "output" / lens
    vis_lp = _result_dir(normal, "initial_lens_model", "vis_lp")
    _image(vis_lp / "image" / "fit.png")
    _image(vis_lp / "image" / "rgb.png")
    (vis_lp / "files" / "coolest.json").write_text('{"stage": "vis_lp"}')
    dataset = tmp_path / "dataset"
    _image(dataset / lens / "segmentation.png")
    inspect = tmp_path / "inspect"

    assert (
        process_dataset(
            normal,
            dataset,
            inspect,
            initial_search_name="vis_lp",
        )
        == "skipped"
    )
    assert (inspect / lens / "vis_lp_fit.png").exists()
    assert "vis_lp_image_with_positions.png" in capsys.readouterr().out

    _image(vis_lp / "image" / "image_with_positions.png")
    assert (
        process_dataset(
            normal,
            dataset,
            inspect,
            initial_search_name="vis_lp",
        )
        == "built"
    )


def test_lens_mass_vis_lp_selection_uses_completed_results_only(
    tmp_path,
    monkeypatch,
    pipeline_config,  # noqa: F811 - imported pytest fixture
):
    import autofit as af
    import autolens as al

    model = af.Collection(
        galaxies=af.Collection(
            lens=af.Model(
                al.Galaxy,
                redshift=0.5,
                mass=af.Model(al.mp.Isothermal, centre=(0.12, -0.05)),
            )
        ),
        fields=af.Model(
            al.MassField,
            redshift=0.5,
            shear=al.mp.ExternalShear,
        ),
    )
    for index, lens in enumerate(("TileAAA", "TileBBB", "TileCCC")):
        _write_result(
            model,
            path_prefix=Path(SAMPLE) / lens,
            name="vis_lp",
            unique_tag="initial_lens_model",
            offset=1.0 + index,
        )

    selection = tmp_path / "selection"
    for lens in ("TileAAA", "TileCCC"):
        (selection / lens).mkdir(parents=True)

    spec = importlib.util.spec_from_file_location(
        "_lens_mass_vis_lp_under_test", CATALOGUE_SCRIPTS / "lens_mass.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    inspect = tmp_path / "inspect"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "lens_mass.py",
            f"--sample={SAMPLE}",
            f"--output_path={pipeline_config}",
            f"--inspect_dir={inspect}",
            "--search_name=vis_lp",
            f"--dataset_names_path={selection}",
        ],
    )
    module.main()

    with (inspect / "lens_mass.csv").open() as stream:
        rows = list(csv.DictReader(stream))
        assert [row["lens_name"] for row in rows] == [
            "TileAAA",
            "TileCCC",
        ]
    assert all(value for row in rows for value in row.values())
    for row in rows:
        assert row["centre_0"] == row["centre_0_lower_3_sigma"]
        assert row["centre_1"] == row["centre_1_upper_3_sigma"]
    assert not (inspect / "TileBBB" / "lens_mass.csv").exists()


def _run_bundle_shell(tmp_path, extra_env):
    """Run build_inspection_bundle.sh on a 3-lens main / 2-lens SED tree with a
    fake ``python`` that logs each producer invocation; return (root, calls)."""
    root = tmp_path / "bundle"
    (root / "scripts").mkdir(parents=True)
    shutil.copyfile(
        PROJECT_ROOT / "scripts" / "build_inspection_bundle.sh",
        root / "scripts" / "build_inspection_bundle.sh",
    )
    sample = "sample"
    for lens in ("TileAAA", "TileBBB", "TileCCC"):
        (root / "output" / sample / lens).mkdir(parents=True)
    for lens in ("TileAAA", "TileCCC"):
        (root / "output_sed" / sample / lens).mkdir(parents=True)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python"
    fake_python.write_text(
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$CALL_LOG"\n'
    )
    fake_python.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = {
        key: value
        for key, value in os.environ.items()
        if key not in ("DATASET_NAMES_PATH", "TAR_TO")
    }
    env.update(
        {
            "PATH": f"{fake_bin}:{os.environ['PATH']}",
            "CALL_LOG": str(call_log),
            "INITIAL_SEARCH_NAME": "vis_lp",
            "CREATE_ARCHIVE": "0",
            **extra_env,
        }
    )
    run = subprocess.run(
        ["bash", "scripts/build_inspection_bundle.sh", sample, "vislp"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    return root, call_log.read_text().splitlines()


def test_shell_dataset_names_path_can_be_disabled(tmp_path):
    """``all``/``none``/explicit-empty drop the default SED-subset selection so
    the full main tree is bundled; no producer receives --dataset_names_path."""
    for value in ("all", "none", ""):
        case = tmp_path / (value or "empty")
        case.mkdir()
        _, calls = _run_bundle_shell(case, {"DATASET_NAMES_PATH": value})
        assert len(calls) == 11, calls  # stage 2 runs twice
        assert not any("--dataset_names_path" in call for call in calls)


def test_shell_tar_to_is_passed_to_stage_one_only(tmp_path):
    _, calls = _run_bundle_shell(tmp_path, {"TAR_TO": "inspect/pngs.tar"})
    tar_calls = [call for call in calls if "--tar_to=" in call]
    assert len(tar_calls) == 1
    assert "scripts/tools/build_inspect.py" in tar_calls[0]
    assert "--tar_to=inspect/pngs.tar" in tar_calls[0]

    no_tar = tmp_path / "no_tar"
    no_tar.mkdir()
    _, calls = _run_bundle_shell(no_tar, {})
    assert not any("--tar_to" in call for call in calls)


def test_shell_routes_vis_lp_and_sersic_roots_with_exact_selection(tmp_path):
    root = tmp_path / "bundle"
    (root / "scripts").mkdir(parents=True)
    shutil.copyfile(
        PROJECT_ROOT / "scripts" / "build_inspection_bundle.sh",
        root / "scripts" / "build_inspection_bundle.sh",
    )
    sample = "sample"
    for lens in ("TileAAA", "TileBBB", "TileCCC"):
        (root / "output" / sample / lens).mkdir(parents=True)
    for lens in ("TileAAA", "TileCCC"):
        (root / "output_sed" / sample / lens).mkdir(parents=True)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_python = fake_bin / "python"
    fake_python.write_text(
        '#!/usr/bin/env bash\nprintf \'%s\\n\' "$*" >> "$CALL_LOG"\n'
    )
    fake_python.chmod(0o755)
    call_log = tmp_path / "calls.log"
    env = {
        **os.environ,
        "PATH": f"{fake_bin}:{os.environ['PATH']}",
        "CALL_LOG": str(call_log),
        "INITIAL_SEARCH_NAME": "vis_lp",
        "CREATE_ARCHIVE": "0",
    }
    run = subprocess.run(
        ["bash", "scripts/build_inspection_bundle.sh", sample, "vislp"],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
    )
    assert run.returncode == 0, run.stdout + run.stderr
    calls = call_log.read_text().splitlines()
    assert any(
        "scripts/tools/build_inspect.py" in call
        and "--output_path=output" in call
        and "--sersic_output_path=output_sed" in call
        and "--initial_search_name=vis_lp" in call
        for call in calls
    )
    assert any(
        "catalogue/scripts/deblending.py" in call
        and "--output_path=output" in call
        and "--search_name=vis_lp" in call
        and "--product_prefix=vis_lp_" in call
        for call in calls
    )
    selection_argument = f"--dataset_names_path={root / 'output_sed' / sample}"
    assert all(selection_argument in call for call in calls)
