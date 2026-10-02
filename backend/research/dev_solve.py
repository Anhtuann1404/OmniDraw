"""Single-case TV4 DEV diagnostic CLI, not TV2's experiment runner.

No API registration, official freeze runs, HOLDOUT access or physical drawing.
Output includes transport-compatible results, full replay traces and DEV scope.
"""

import argparse
from dataclasses import asdict
import hashlib
import json
from math import isclose
from pathlib import Path
import platform
import subprocess
import sys

from .joint_dp import solve_joint
from .render_dev import render_dev_svg
from .schemas import Budget, Metrics, Provenance, SolveResult, Theta, VERSION, canonical_hash
from .service import load_manifest

ROOT = Path(__file__).resolve().parents[2]


def git_snapshot():
    commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    patch = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=ROOT)
    hashes = {}
    for raw in subprocess.check_output(["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=ROOT).split(b"\0"):
        if raw:
            relative = raw.decode()
            path = ROOT / relative
            if path.is_file():
                digest = hashlib.sha256()
                with path.open("rb") as stream:
                    for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(chunk)
                hashes[relative] = digest.hexdigest()
    dirty = canonical_hash({"tracked_patch_sha256": hashlib.sha256(patch).hexdigest(), "untracked": hashes}) if patch or hashes else None
    return commit, dirty


def result_packet(case, theta, budget, run, snapshot, seed):
    config = {"theta": theta.model_dump(mode="json"), "budget": budget.model_dump(mode="json"),
              "mode": run.mode, "seed": seed, "tie_policy_id": run.tie_policy_id}
    coefficients = ({key: getattr(run.replay, key) for key in ("L_down_mm", "L_up_mm", "N_cycle", "J_mm")}
                    if run.replay else {})
    j = coefficients.get("J_mm")
    result = SolveResult(
        run_id=f"dev-{case.case_id}-{run.mode}", case_id=case.case_id, method="joint_dp",
        candidate_set_sha256=case.candidate_set_sha256, contract_version=VERSION,
        outcome=run.outcome, scope="full_candidate_set", enumeration_complete=False,
        ranking_complete=False, search_complete=run.search_complete, schedule=run.schedule,
        metrics=Metrics(**coefficients, total_wall_time_ms=run.diagnostics["wall_time_ms"],
                        peak_states=run.diagnostics["peak_states"],
                        peak_memory_mb=run.diagnostics["tracked_peak_memory_mb"]),
        bounds={"lower_bound_J_mm": j if run.search_complete else None, "upper_bound_J_mm": j},
        provenance=Provenance(git_commit=snapshot[0], dirty_patch_sha256=snapshot[1],
                              manifest_sha256=case.manifest_sha256,
                              input_sha256=canonical_hash(case.model_dump(mode="json")),
                              config_sha256=canonical_hash(config), seed=seed,
                              runtime_versions={"python": platform.python_version(), "tv4-dev-dp": "1"},
                              timing_source="dev"),
        validation={"status": "NOT_RUN"}, error=None)
    return {"result": result.model_dump(mode="json"), "config": config,
            "trace": [asdict(step) for step in run.replay.trace] if run.replay else [],
            "diagnostics": run.diagnostics}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--case-id", required=True)
    parser.add_argument("--rho", type=float, required=True)
    parser.add_argument("--lambda-mm", type=float, required=True)
    parser.add_argument("--mode", choices=("no-forget", "safe-forget", "both"), default="both")
    parser.add_argument("--wall-time-ms", type=int, required=True)
    parser.add_argument("--max-states", type=int, required=True)
    parser.add_argument("--memory-limit-mb", type=int, required=True)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--svg-output", type=Path, help="DEV diagnostic SVG; independent validation NOT_RUN")
    args = parser.parse_args(argv)
    outputs = [p for p in (args.output, args.svg_output) if p is not None]
    if len({p.resolve() for p in outputs}) != len(outputs):
        raise ValueError("JSON and SVG outputs require distinct paths")
    if any(p.exists() for p in outputs):
        raise FileExistsError("DEV output exists; choose new paths")
    cases = load_manifest(args.manifest)
    case = next((c for c in cases if c.case_id == args.case_id), None)
    if case is None or case.split not in {"dev", "synthetic"}:
        raise ValueError("Only available dev/synthetic case IDs can be used")
    theta = Theta(rho=args.rho, lambda_mm=args.lambda_mm)
    budget = Budget(wall_time_ms=args.wall_time_ms, max_states=args.max_states,
                    max_configurations=1, memory_limit_mb=args.memory_limit_mb)
    modes = [False, True] if args.mode == "both" else [args.mode == "safe-forget"]
    snapshot = git_snapshot()
    runs = [solve_joint(case, theta, budget, safe_forget=mode) for mode in modes]
    comparison = "NOT_RUN"
    if len(runs) == 2:
        a, b = runs
        if not a.search_complete or not b.search_complete:
            comparison = "INCOMPLETE"
        elif a.outcome != b.outcome or bool(a.replay) != bool(b.replay):
            comparison = "FAIL"
        else:
            # This diagnostic tolerance does not set research epsilon_eq or freeze policy.
            comparison = "PASS" if not a.replay or isclose(a.replay.J_mm, b.replay.J_mm, rel_tol=1e-12, abs_tol=1e-9) else "FAIL"
    packet = {"schema_version": VERSION, "usage": "DEV_ONLY", "independent_validation": "NOT_RUN",
              "quality_gate": "PENDING", "owner_review": "PENDING", "compare_modes": comparison,
              "runs": [result_packet(case, theta, budget, run, snapshot, args.seed) for run in runs]}
    data = json.dumps(packet, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
    selected = next((r for r in reversed(runs) if r.schedule is not None), None)
    svg = None
    if args.svg_output:
        if selected is None:
            raise ValueError("No completed incumbent is available for DEV SVG")
        svg = render_dev_svg(case, selected.schedule, theta)
    if args.output:
        # An explicit path is required; immutable historical evidence has no default destination.
        if args.output.exists():
            raise FileExistsError("DEV output exists; choose a new path")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(data)
    else:
        sys.stdout.write(data)
    if svg is not None:
        args.svg_output.parent.mkdir(parents=True, exist_ok=True)
        with args.svg_output.open("x", encoding="utf-8") as stream:
            stream.write(svg)
    return 1 if comparison == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
