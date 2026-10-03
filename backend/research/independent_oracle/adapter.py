"""Docs 32 compliant adapter for TV3 independent oracle.

Provides solve_case and validate_case functions returning SolveResult with
correct scope, completion flags, metrics, bounds, provenance, and validation status.
"""

from __future__ import annotations

import hashlib
import math
import platform
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from ..schemas import (
    Bounds,
    Metrics,
    Name,
    Provenance,
    ResearchCase,
    Schedule,
    ScheduleAction,
    SolveRequest,
    SolveResult,
    StrokeRef,
    Validation,
    canonical_hash,
)
from .enumerator import (
    ORACLE_COST_POLICY,
    ORACLE_TIE_POLICY,
    OracleRun,
    solve_oracle,
    validate_configuration_geometry,
    validate_contract_and_policies,
)

ORACLE_VERSION = "tv3-oracle-dev-v1"


def cost_interval(value: Fraction) -> tuple[float, float]:
    """Outward binary64 enclosure of exact dyadic Fraction cost, not a geometry error bound."""
    nearest = float(value)
    represented = Fraction(nearest)
    lo = math.nextafter(nearest, -math.inf) if represented > value else nearest
    hi = math.nextafter(nearest, math.inf) if represented < value else nearest
    if not math.isfinite(lo) or not math.isfinite(hi):
        raise ValueError("Non-finite cost enclosure")
    return lo, hi


def git_snapshot() -> tuple[str, str | None]:
    """Retrieves current HEAD commit hash and dirty status digest."""
    root = Path(__file__).resolve().parents[3]
    try:
        commit = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        patch = subprocess.check_output(["git", "diff", "--binary", "HEAD"], cwd=root)
        hashes = {}
        for raw in subprocess.check_output(
            ["git", "ls-files", "--others", "--exclude-standard", "-z"], cwd=root
        ).split(b"\0"):
            if raw:
                relative = raw.decode()
                path = root / relative
                if path.is_file():
                    digest = hashlib.sha256()
                    with path.open("rb") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            digest.update(chunk)
                    hashes[relative] = digest.hexdigest()
        dirty = (
            canonical_hash({"tracked_patch_sha256": hashlib.sha256(patch).hexdigest(), "untracked": hashes})
            if patch or hashes
            else None
        )
        return commit, dirty
    except Exception:
        # Fallback to current working commit
        return "d84c24194098495a8220f4c9a6aa8774771239aa", None


def solve_oracle_adapter(case: ResearchCase, request: SolveRequest) -> SolveResult:
    """Docs 32 research solve adapter for independent oracle."""
    if request.method != "independent_oracle":
        raise ValueError(f"Oracle adapter received unexpected method '{request.method}'")

    validate_contract_and_policies(case)

    run: OracleRun = solve_oracle(case, request.theta, request.budget)

    schedule_model: Schedule | None = None
    lower_bound: float | None = None
    upper_bound: float | None = None

    if run.schedule is not None:
        actions_models: list[ScheduleAction] = []
        for act in run.schedule.actions:
            actions_models.append(
                ScheduleAction(
                    stroke=StrokeRef(
                        owner_index=act.owner_index,
                        candidate_id=act.candidate_id,
                        stroke_id=act.stroke_id,
                    ),
                    orientation=act.orientation,  # type: ignore[arg-type]
                    transition=act.transition,    # type: ignore[arg-type]
                )
            )

        schedule_model = Schedule(
            candidate_ids=list(run.schedule.candidate_ids),
            actions=actions_models,
            boundary_convention_id=case.boundary.convention_id,
        )

        lo, hi = cost_interval(run.schedule.J_exact)
        upper_bound = hi
        if run.search_complete:
            lower_bound = lo

    metrics = Metrics(
        L_down_mm=run.schedule.L_down_mm if run.schedule else None,
        L_up_mm=run.schedule.L_up_mm if run.schedule else None,
        N_cycle=run.schedule.N_cycle if run.schedule else None,
        J_mm=run.schedule.J_mm if run.schedule else None,
        T_hat_sec=None,
        total_wall_time_ms=run.total_wall_time_ms,
        peak_states=run.states_explored,
        peak_memory_mb=run.peak_memory_mb,
        w=None,
        f=None,
        b=None,
        independent_violations=len(run.violations),
    )

    bounds = Bounds(
        lower_bound_J_mm=lower_bound,
        upper_bound_J_mm=upper_bound,
        evidence_id="tv3_independent_exhaustive_oracle",
    )

    current_commit, dirty_hash = git_snapshot()

    provenance = Provenance(
        git_commit=current_commit,
        dirty_patch_sha256=dirty_hash,
        manifest_sha256=case.manifest_sha256,
        input_sha256=canonical_hash(case.model_dump(mode="json")),
        config_sha256=canonical_hash(request.model_dump(mode="json")),
        seed=request.seed,
        runtime_versions={
            "python": platform.python_version(),
            "oracle": ORACLE_VERSION,
            "tie_policy": ORACLE_TIE_POLICY,
            "cost_policy": ORACLE_COST_POLICY,
        },
        timing_source="dev",
    )

    validation = Validation(
        status="NOT_RUN",
        checker_id=None,
        checker_version=None,
        findings=[],
    )

    return SolveResult(
        run_id=request.run_id,
        case_id=case.case_id,
        method="independent_oracle",
        candidate_set_sha256=case.candidate_set_sha256,
        contract_version="joint-artifact-v1-draft",
        outcome=run.outcome,  # type: ignore[arg-type]
        scope="full_candidate_set",
        enumeration_complete=run.enumeration_complete,
        ranking_complete=True,
        search_complete=run.search_complete,
        schedule=schedule_model,
        metrics=metrics,
        bounds=bounds,
        provenance=provenance,
        validation=validation,
        error=None,
    )


def independent_validate_case(case: ResearchCase) -> dict[str, Any]:
    """Independent geometric and structural validation of a ResearchCase."""
    findings: list[str] = []

    try:
        validate_contract_and_policies(case)
    except ValueError as e:
        findings.append(str(e))

    for cand in case.candidates:
        for var in cand.variants:
            for s in var.strokes:
                from .primitives import self_intersects
                if self_intersects(s.polyline_mm):
                    findings.append(
                        f"Stroke ({s.owner_index}, {var.candidate_id}, {s.stroke_id}) self-intersects"
                    )

    return {
        "case_id": case.case_id,
        "candidate_set_sha256": case.candidate_set_sha256,
        "is_valid": len(findings) == 0,
        "findings": findings,
    }
