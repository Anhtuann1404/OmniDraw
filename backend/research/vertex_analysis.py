"""TV4 four-vertex DEV regret diagnostic, never independent certification."""

from time import monotonic

from .geometry import check_selected_geometry
from .joint_dp import solve_joint
from .schedule_checker import check_schedule_cost
from .schemas import Budget, Domain, ResearchCase, Schedule, Theta, canonical_hash


def analyze_fixed_schedule(case: ResearchCase, schedule: Schedule, domain: Domain, budget: Budget):
    """Keep pi fixed; competitors may choose all candidates at every vertex.

    Returns NOT_CERTIFIED even if every DEV DP search completes. Independent
    validation, numerical error bounds and owner review are still required.
    wall_time/max_states are shared across the four vertex searches.
    """
    started = monotonic()
    case = ResearchCase.model_validate(case.model_dump(mode="json"))
    schedule = Schedule.model_validate(schedule.model_dump(mode="json"))
    domain = Domain.model_validate(domain.model_dump(mode="json"))
    budget = Budget.model_validate(budget.model_dump(mode="json"))
    if case.split not in {"dev", "synthetic"}:
        raise ValueError("Only dev/synthetic cases can be analyzed")
    check_selected_geometry(case, schedule)
    vertices = []
    remaining_states = budget.max_states
    for rho, lam in ((domain.rho_min, domain.lambda_min_mm), (domain.rho_min, domain.lambda_max_mm),
                     (domain.rho_max, domain.lambda_min_mm), (domain.rho_max, domain.lambda_max_mm)):
        theta = Theta(rho=rho, lambda_mm=lam)
        fixed = check_schedule_cost(case, schedule, theta)
        remaining_ms = int(budget.wall_time_ms - (monotonic() - started) * 1000)
        optimum = None
        if remaining_ms <= 0:
            outcome = "TIMEOUT"
        elif remaining_states <= 0:
            outcome = "RESOURCE_LIMIT"
        else:
            local_budget = budget.model_copy(update={"wall_time_ms": remaining_ms, "max_states": remaining_states})
            run = solve_joint(case, theta, local_budget, safe_forget=True)
            remaining_states -= run.diagnostics["peak_states"]
            outcome = run.outcome
            if run.search_complete and run.replay is not None:
                optimum = run.replay.J_mm
        vertices.append({"theta": theta.model_dump(mode="json"), "J_pi_mm": fixed.J_mm,
                         "outcome": outcome, "dev_optimum_J_mm": optimum,
                         "dev_regret_mm": None if optimum is None else fixed.J_mm - optimum})
    regrets = [v["dev_regret_mm"] for v in vertices]
    return {"usage": "DEV_ONLY", "certificate_status": "NOT_CERTIFIED",
            "candidate_set_sha256": case.candidate_set_sha256,
            "schedule_sha256": canonical_hash(schedule.model_dump(mode="json")),
            "domain": domain.model_dump(mode="json"), "vertices": vertices,
            "modeled_vertex_max_regret_mm": max(regrets) if all(r is not None for r in regrets) else None,
            "independent_validation": "NOT_RUN", "numerical_error_bound": "PENDING",
            "total_wall_time_ms": (monotonic() - started) * 1000}
