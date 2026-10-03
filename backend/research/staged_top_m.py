"""TV2 DEV H_ref/top-m baseline; no API adapter or independent certification."""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from math import prod
from time import monotonic
import tracemalloc

from .cost_arithmetic import COST_POLICY
from .geometry import compile_geometry
from .joint_dp import JointRun, solve_fixed_configuration
from .schedule_checker import check_schedule_cost
from .schemas import Budget, ResearchCase, Schedule, ScheduleAction, StrokeRef, Theta

MIB = 1024 * 1024
RANKER = "H_ref-immediate-mark-forward-lift-v1-dev"


@dataclass(frozen=True)
class StagedRun:
    outcome: str
    scope: str
    enumeration_complete: bool
    ranking_complete: bool
    search_complete: bool
    ranked_prefix: tuple[tuple[str, ...], ...]
    best_inner: JointRun | None
    configurations_seen: int
    invalid_reference_count: int
    diagnostics: dict
    candidate_set_sha256: str
    cost_policy_id: str
    theta: Theta
    rank_at_theta0: Theta
    m_requested: int
    ranker_id: str = RANKER


def _reference_schedule(case: ResearchCase, ids: tuple[str, ...]) -> Schedule:
    actions = []
    for owner, cid in enumerate(ids):
        variant = next(v for v in case.candidates[owner].variants if v.candidate_id == cid)
        order = list(variant.body_order)
        order.extend(sorted(stroke.stroke_id for stroke in variant.strokes if stroke.role == "mark"))
        for sid in order:
            actions.append(ScheduleAction(stroke=StrokeRef(owner_index=owner, candidate_id=cid,
                                                           stroke_id=sid),
                                          orientation="forward", transition="LIFT"))
    return Schedule(candidate_ids=list(ids), actions=actions,
                    boundary_convention_id=case.boundary.convention_id)


def staged_top_m_h_ref(case: ResearchCase, theta: Theta, theta0: Theta,
                       m: int, budget: Budget, *, safe_forget=True) -> StagedRun:
    """Rank all G at theta0, then solve the certified prefix at theta.

    This exhaustive DEV version deliberately has an O(|G|) ranking ceiling.
    No quality filtering is performed here: the caller supplies the *same*
    prepared case to joint and staged methods after a shared gate.
    """
    case = ResearchCase.model_validate(case.model_dump(mode="json"))
    theta = Theta.model_validate(theta.model_dump(mode="json"))
    theta0 = Theta.model_validate(theta0.model_dump(mode="json"))
    budget = Budget.model_validate(budget.model_dump(mode="json"))
    if type(m) is not int or m < 1:
        raise ValueError("m must be a positive integer of complete configurations")
    if case.split not in {"dev", "synthetic"}:
        raise ValueError("DEV baseline accepts only dev/synthetic cases; HOLDOUT remains closed")
    started = monotonic()
    owned_tracer = not tracemalloc.is_tracing()
    if owned_tracer:
        tracemalloc.start()
    initial_bytes = tracemalloc.get_traced_memory()[0]
    peak_bytes = 0
    scores: list[tuple[bool, Fraction, tuple[str, ...]]] = []
    prefix: tuple[tuple[str, ...], ...] = ()
    invalid = states_used = 0
    best: JointRun | None = None
    outcome = "RESOURCE_LIMIT"
    enumeration_complete = ranking_complete = search_complete = False
    scope = "explored_subset"
    ranking_ms = 0.0

    def remaining():
        nonlocal peak_bytes
        used = max(0, tracemalloc.get_traced_memory()[0] - initial_bytes)
        peak_bytes = max(peak_bytes, used)
        wall_ms = int(budget.wall_time_ms - (monotonic() - started) * 1000)
        memory_mb = (budget.memory_limit_mb * MIB - used) // MIB
        if wall_ms < 1:
            return "TIMEOUT", None
        if memory_mb < 1 or states_used >= budget.max_states:
            return "RESOURCE_LIMIT", None
        return None, Budget(wall_time_ms=wall_ms,
                            max_states=budget.max_states - states_used,
                            max_configurations=budget.max_configurations,
                            memory_limit_mb=memory_mb)

    try:
        error, _ = remaining()
        if error:
            outcome = error
        else:
            index = compile_geometry(case)
            options = [tuple(sorted(v.candidate_id for v in row.variants)) for row in case.candidates]
            total = prod(map(len, options))
            for ids in product(*options):
                error, _ = remaining()
                if error or len(scores) >= budget.max_configurations:
                    outcome = error or "RESOURCE_LIMIT"
                    break
                selected = []
                feasible_geometry = True
                for owner, cid in enumerate(ids):
                    if not index.compatible(owner, cid, selected):
                        feasible_geometry = False
                        break
                    selected.append((owner, cid))
                value = None
                if feasible_geometry:
                    try:
                        value = check_schedule_cost(case, _reference_schedule(case, ids), theta0).objective_exact
                    except ValueError:
                        pass  # Invalid reference schedule ranks last; geometry stays in G.
                if value is None:
                    invalid += 1
                scores.append((value is None, value if value is not None else Fraction(0), ids))
            else:
                enumeration_complete = True
            ranking_ms = (monotonic() - started) * 1000
            if enumeration_complete:
                scores.sort()
                prefix = tuple(ids for _, _, ids in scores[:m])
                ranking_complete = True
                scope = "declared_prefix"
                search_complete = True
                for ids in prefix:
                    error, inner_budget = remaining()
                    if error:
                        outcome, search_complete = error, False
                        break
                    inner = solve_fixed_configuration(case, ids, theta, inner_budget,
                                                      safe_forget=safe_forget)
                    states_used += inner.diagnostics["peak_states"]
                    if inner.replay is not None and (best is None or best.replay is None or
                                                     (inner.objective_exact, ids) <
                                                     (best.objective_exact, best.configuration_candidate_ids)):
                        best = inner
                    if not inner.search_complete:
                        outcome, search_complete = inner.outcome, False
                        break
                if search_complete:
                    outcome = "OPTIMAL" if best is not None else "NO_FEASIBLE_IN_PREFIX"
    finally:
        elapsed_ms = (monotonic() - started) * 1000
        if owned_tracer:
            peak_bytes = max(peak_bytes, max(0, tracemalloc.get_traced_memory()[1] - initial_bytes))
            tracemalloc.stop()
    return StagedRun(outcome, scope, enumeration_complete, ranking_complete, search_complete,
                     prefix, best, len(scores), invalid,
                     {"total_wall_time_ms": elapsed_ms, "ranking_wall_time_ms": ranking_ms,
                      "inner_wall_time_ms": elapsed_ms - ranking_ms,
                      "peak_allocated_mb": peak_bytes / MIB, "states_used": states_used,
                      "G_size": total if enumeration_complete else None,
                      "ranking_evidence": "exhaustive_cartesian" if ranking_complete else None},
                     case.candidate_set_sha256,
                     COST_POLICY, theta, theta0, m)
