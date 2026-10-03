"""Docs 32 compliant adapter for TV3 independent oracle.

Provides solve_case and validate_case functions returning SolveResult with
correct scope, completion flags, metrics, bounds, provenance, and validation status.
"""

from __future__ import annotations

import platform
import sys
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
)

ORACLE_VERSION = "tv3-oracle-dev-v1"
ORACLE_GIT_COMMIT = "965994645228c2e646279f53e6b772c728e85c2d"  # Ancestor base on codex/tv3-research-oracle-20261002


def solve_oracle_adapter(case: ResearchCase, request: SolveRequest) -> SolveResult:
    """Docs 32 research solve adapter for independent oracle."""
    if request.method != "independent_oracle":
        raise ValueError(f"Oracle adapter received unexpected method '{request.method}'")

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

        upper_bound = run.schedule.J_mm
        if run.search_complete:
            lower_bound = run.schedule.J_mm

    metrics = Metrics(
        L_down_mm=run.schedule.L_down_mm if run.schedule else None,
        L_up_mm=run.schedule.L_up_mm if run.schedule else None,
        N_cycle=run.schedule.N_cycle if run.schedule else None,
        J_mm=run.schedule.J_mm if run.schedule else None,
        T_hat_sec=None,
        total_wall_time_ms=run.total_wall_time_ms,
        peak_states=run.states_explored,
        peak_memory_mb=None,
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

    provenance = Provenance(
        git_commit=ORACLE_GIT_COMMIT,
        dirty_patch_sha256=None,
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

    # Check every variant in every candidate for self-intersections
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
