"""DEV artifact integrity, entry points and isolation from product/hardware code."""

import ast
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import pytest

from backend.research import dev_solve
from backend.research.joint_dp import solve_joint
from backend.research.render_dev import render_dev_svg
from backend.research.schemas import Budget, ResearchCase, SolveResult, Theta, canonical_hash
from backend.research.service import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "solver_dev_cases.json"
BUDGET = Budget(wall_time_ms=10000, max_states=100000, max_configurations=1, memory_limit_mb=64)


def test_svg_traversals_match_selected_geometry():
    case = load_manifest(FIXTURE)[0]
    theta = Theta(rho=.5, lambda_mm=2)
    run = solve_joint(case, theta, BUDGET, safe_forget=True)
    svg = ET.fromstring(render_dev_svg(case, run.schedule, theta))
    ns = {"s": "http://www.w3.org/2000/svg"}
    metadata = json.loads(svg.find("s:metadata", ns).text)
    assert metadata["independent_validation"] == "NOT_RUN"
    assert metadata["schedule_sha256"] == canonical_hash(run.schedule.model_dump(mode="json"))
    assert metadata["candidate_set_sha256"] == case.candidate_set_sha256
    paths = svg.findall("s:g/s:path", ns)
    assert len(paths) == len(run.schedule.actions)
    for action, path in zip(run.schedule.actions, paths):
        character = case.candidates[action.stroke.owner_index]
        variant = next(v for v in character.variants if v.candidate_id == action.stroke.candidate_id)
        stroke = next(s for s in variant.strokes if s.stroke_id == action.stroke.stroke_id)
        expected = list(reversed(stroke.polyline_mm)) if action.orientation == "reverse" else stroke.polyline_mm
        numbers = [float(token) for token in path.attrib["d"].split() if token not in {"M", "L"}]
        assert list(zip(numbers[::2], numbers[1::2])) == expected
        assert path.attrib["data-transition"] == action.transition


def cli_args(tmp_path):
    return ["--manifest", str(FIXTURE), "--case-id", "tv4-solver-dev-stacked-3",
            "--rho", ".5", "--lambda-mm", "2", "--wall-time-ms", "10000",
            "--max-states", "100000", "--memory-limit-mb", "64",
            "--output", str(tmp_path / "result.json"), "--svg-output", str(tmp_path / "dev.svg")]


def test_cli_two_modes_transport_and_provenance(tmp_path, monkeypatch):
    monkeypatch.setattr(dev_solve, "git_snapshot", lambda: ("a" * 40, "b" * 64))
    assert dev_solve.main(cli_args(tmp_path)) == 0
    packet = json.loads((tmp_path / "result.json").read_text())
    assert packet["usage"] == "DEV_ONLY" and packet["compare_modes"] == "PASS"
    for entry in packet["runs"]:
        result = SolveResult.model_validate(entry["result"])
        assert result.validation.status == "NOT_RUN"
        assert result.provenance.dirty_patch_sha256 == "b" * 64
        assert result.provenance.config_sha256 == canonical_hash(entry["config"])
        assert entry["trace"][-1]["kind"] == "END"
    assert (tmp_path / "dev.svg").is_file()


def test_cli_never_overwrites_existing_output(tmp_path):
    target = tmp_path / "result.json"
    target.write_text("preserve")
    with pytest.raises(FileExistsError):
        dev_solve.main(cli_args(tmp_path))
    assert target.read_text() == "preserve"
    assert not (tmp_path / "dev.svg").exists()


def test_cli_input_error_has_no_artifact_side_effect(tmp_path):
    args = cli_args(tmp_path)
    args[args.index(".5")] = "nan"
    with pytest.raises(ValueError):
        dev_solve.main(args)
    assert not list(tmp_path.iterdir())


def test_research_core_imports_neither_product_solver_nor_hardware():
    root = Path(dev_solve.__file__).parent
    for path in root.glob("*.py"):
        tree = ast.parse(path.read_text())
        imports = [n.module or "" for n in ast.walk(tree) if isinstance(n, ast.ImportFrom)]
        imports.extend(alias.name for n in ast.walk(tree) if isinstance(n, ast.Import) for alias in n.names)
        assert not any("handwriting" in name or "hardware" in name or "backup" in name for name in imports), path
