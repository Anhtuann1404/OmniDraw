"""Independent exhaustive brute-force candidate and action enumerator.

Authored independently by TV3 following Docs 31 (joint solver contract) and Docs 32.
Exhaustively explores all candidate combinations, body progressions, mark precedence,
deadline constraints (k), reversible orientations, and CONNECT/LIFT transitions.
No imports from TV4 solver, DP, geometry, or schedule checker modules.
"""

from __future__ import annotations

import math
import time
import tracemalloc
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Sequence

from ..schemas import (
    Boundary,
    Budget,
    Contact,
    Point,
    ResearchCase,
    Schedule,
    ScheduleAction,
    Stroke,
    StrokeRef,
    Theta,
    Variant,
)
from .primitives import (
    C_MIN_MM,
    point_distance,
    polyline_clearance,
    self_intersects,
)

ORACLE_TIE_POLICY = "tv4-dev-dyadic-lex-actions-v2"
ORACLE_COST_POLICY = "tv4-dev-dyadic-primitive-cost-v1"

SUPPORTED_FLATTEN = "tv4-dev-polyline-v1"
SUPPORTED_NUMERIC = "tv4-dev-float-v1"
SUPPORTED_SEPARATION = "tv4-dev-all-pairs-v1"
SUPPORTED_CONTACT = "tv4-dev-exact-endpoint-v1"


class OracleBudgetExceeded(Exception):
    """Raised when oracle exploration budget is exhausted."""
    def __init__(self, message: str, outcome: str = "TIMEOUT"):
        super().__init__(message)
        self.outcome = outcome


@dataclass(frozen=True)
class EvaluatedAction:
    owner_index: int
    candidate_id: str
    stroke_id: str
    orientation: str  # "forward" or "reverse"
    transition: str   # "LIFT" or "CONNECT"

    def as_key(self) -> tuple[int, str, str]:
        return (self.owner_index, self.candidate_id, self.stroke_id)

    def tie_tuple(self) -> tuple[tuple[int, str, str], str, str]:
        return (self.as_key(), self.orientation, self.transition)


@dataclass
class OracleSchedule:
    candidate_ids: list[str]
    actions: list[EvaluatedAction]
    L_down_mm: float
    L_up_mm: float
    N_cycle: int
    J_mm: float
    J_exact: Fraction

    def tie_key(self) -> tuple[Fraction, tuple]:
        return (self.J_exact, tuple(a.tie_tuple() for a in self.actions))


@dataclass
class OracleRun:
    outcome: str  # "OPTIMAL", "INFEASIBLE", "TIMEOUT", "RESOURCE_LIMIT"
    search_complete: bool
    enumeration_complete: bool
    schedule: OracleSchedule | None
    configurations_explored: int
    states_explored: int
    peak_memory_mb: float
    total_wall_time_ms: float
    violations: list[str] = field(default_factory=list)


def calculate_stroke_length(polyline: Sequence[Point]) -> float:
    """Calculates cumulative Euclidean length of a polyline using exact float accumulation."""
    if len(polyline) < 2:
        return 0.0
    return math.fsum(point_distance(p1, p2) for p1, p2 in zip(polyline, polyline[1:]))


def validate_contract_and_policies(case: ResearchCase) -> None:
    """Enforces strict DEV contract, rejecting HOLDOUT and unsupported policies."""
    if case.split not in {"dev", "synthetic"}:
        raise ValueError("DEV oracle accepts only dev/synthetic cases; HOLDOUT remains closed")

    gp = case.geometry_policy
    if gp.flatten_policy_id != SUPPORTED_FLATTEN:
        raise ValueError(f"Unsupported flatten policy '{gp.flatten_policy_id}'; only {SUPPORTED_FLATTEN} is supported")
    if gp.numeric_policy_id != SUPPORTED_NUMERIC:
        raise ValueError(f"Unsupported numeric policy '{gp.numeric_policy_id}'; only {SUPPORTED_NUMERIC} is supported")
    if gp.separation_policy_id != SUPPORTED_SEPARATION:
        raise ValueError(f"Unsupported separation policy '{gp.separation_policy_id}'; only {SUPPORTED_SEPARATION} is supported")
    if gp.contact_policy_id != SUPPORTED_CONTACT:
        raise ValueError(f"Unsupported contact policy '{gp.contact_policy_id}'; only {SUPPORTED_CONTACT} is supported")
    if gp.c_min_mm != C_MIN_MM:
        raise ValueError(f"c_min_mm must be {C_MIN_MM:.2f} mm, got {gp.c_min_mm}")

    # Validate contacts
    all_strokes = {
        (cand.owner_index, var.candidate_id, stroke.stroke_id): stroke
        for cand in case.candidates
        for var in cand.variants
        for stroke in var.strokes
    }

    for c in case.contacts:
        if c.policy_id != SUPPORTED_CONTACT:
            raise ValueError(f"Unsupported contact policy '{c.policy_id}'")
        k1 = (c.first.owner_index, c.first.candidate_id, c.first.stroke_id)
        k2 = (c.second.owner_index, c.second.candidate_id, c.second.stroke_id)
        if k1 not in all_strokes or k2 not in all_strokes:
            raise ValueError(f"Contact references non-existent stroke: {k1} or {k2}")

        s1 = all_strokes[k1]
        s2 = all_strokes[k2]
        loc = tuple(c.location_mm)
        s1_ends = (tuple(s1.polyline_mm[0]), tuple(s1.polyline_mm[-1]))
        s2_ends = (tuple(s2.polyline_mm[0]), tuple(s2.polyline_mm[-1]))
        if loc not in s1_ends or loc not in s2_ends:
            raise ValueError(f"Contact location {loc} does not match endpoints of strokes {k1} and {k2}")


def validate_configuration_geometry(
    case: ResearchCase,
    selected_variants: dict[int, Variant],
) -> tuple[bool, list[str]]:
    """Checks self-intersection and inter-stroke clearance for a candidate configuration.

    Returns (is_feasible, list_of_violations).
    """
    violations: list[str] = []

    # Map contacts by frozenset of StrokeRef keys for fast lookup
    contact_map: dict[frozenset[tuple[int, str, str]], Contact] = {}
    for c in case.contacts:
        k1 = (c.first.owner_index, c.first.candidate_id, c.first.stroke_id)
        k2 = (c.second.owner_index, c.second.candidate_id, c.second.stroke_id)
        contact_map[frozenset((k1, k2))] = c

    # Collect all strokes in configuration
    all_strokes: list[tuple[int, str, Stroke]] = []
    for owner_idx, variant in sorted(selected_variants.items()):
        for stroke in variant.strokes:
            all_strokes.append((owner_idx, variant.candidate_id, stroke))

    # 1. Self-intersection check
    for owner_idx, cid, stroke in all_strokes:
        if self_intersects(stroke.polyline_mm):
            violations.append(
                f"Self-intersection in stroke ({owner_idx}, {cid}, {stroke.stroke_id})"
            )

    if violations:
        return False, violations

    # 2. All-pairs clearance check
    num_strokes = len(all_strokes)
    for i in range(num_strokes):
        owner1, cid1, s1 = all_strokes[i]
        key1 = (owner1, cid1, s1.stroke_id)
        for j in range(i + 1, num_strokes):
            owner2, cid2, s2 = all_strokes[j]
            key2 = (owner2, cid2, s2.stroke_id)

            contact_spec = contact_map.get(frozenset((key1, key2)))
            clearance = polyline_clearance(s1.polyline_mm, s2.polyline_mm, contact_spec)

            if clearance is not None and clearance < case.geometry_policy.c_min_mm:
                violations.append(
                    f"Clearance violation between ({owner1}, {cid1}, {s1.stroke_id}) and "
                    f"({owner2}, {cid2}, {s2.stroke_id}): {clearance:.4f} mm < "
                    f"{case.geometry_policy.c_min_mm:.4f} mm"
                )

    is_feasible = (len(violations) == 0)
    return is_feasible, violations


def resolve_delay(case: ResearchCase, owner_idx: int, cid: str, stroke: Stroke) -> int:
    """Resolves delay k for a mark stroke from delay_policy."""
    qualified = f"{owner_idx}/{cid}/{stroke.stroke_id}"
    if qualified in case.delay_policy:
        return case.delay_policy[qualified]
    if stroke.mark_type and stroke.mark_type in case.delay_policy:
        return case.delay_policy[stroke.mark_type]
    raise ValueError(f"Missing delay policy for mark ({qualified}) or type '{stroke.mark_type}'")


def solve_oracle(
    case: ResearchCase,
    theta: Theta,
    budget: Budget | None = None,
) -> OracleRun:
    """Exhaustively solves the joint geometry and scheduling problem independently."""
    validate_contract_and_policies(case)

    start_time = time.perf_counter()

    wall_limit_ms = budget.wall_time_ms if budget else 30000
    max_states = budget.max_states if budget else 200000
    max_configs = budget.max_configurations if budget else 100000
    memory_limit_mb = budget.memory_limit_mb if budget else 512

    owned_tracer = not tracemalloc.is_tracing()
    if owned_tracer:
        tracemalloc.start()
    initial_memory = tracemalloc.get_traced_memory()[0]
    peak_memory = 0

    def check_budget(configs: int, states: int):
        nonlocal peak_memory
        current_mem = max(0, tracemalloc.get_traced_memory()[0] - initial_memory)
        if current_mem > peak_memory:
            peak_memory = current_mem

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if elapsed_ms >= wall_limit_ms:
            raise OracleBudgetExceeded(f"Wall time limit {wall_limit_ms} ms exceeded", outcome="TIMEOUT")
        if current_mem >= memory_limit_mb * 1024 * 1024:
            raise OracleBudgetExceeded(f"Memory limit {memory_limit_mb} MB exceeded", outcome="RESOURCE_LIMIT")
        if configs > max_configs:
            raise OracleBudgetExceeded(f"Max configurations {max_configs} exceeded", outcome="RESOURCE_LIMIT")
        if states > max_states:
            raise OracleBudgetExceeded(f"Max states {max_states} exceeded", outcome="RESOURCE_LIMIT")

    # Contacts lookup
    contact_map: dict[frozenset[tuple[int, str, str]], Contact] = {}
    for c in case.contacts:
        k1 = (c.first.owner_index, c.first.candidate_id, c.first.stroke_id)
        k2 = (c.second.owner_index, c.second.candidate_id, c.second.stroke_id)
        contact_map[frozenset((k1, k2))] = c

    n_owners = len(case.candidates)

    # Empty case handling
    if n_owners == 0:
        up_dist = point_distance(case.boundary.p0_mm, case.boundary.p_end_mm)
        j_exact = Fraction(theta.rho) * Fraction(up_dist)
        j_float = float(j_exact)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        empty_sched = OracleSchedule(
            candidate_ids=[],
            actions=[],
            L_down_mm=0.0,
            L_up_mm=up_dist,
            N_cycle=0,
            J_mm=j_float,
            J_exact=j_exact,
        )
        if owned_tracer:
            tracemalloc.stop()
        return OracleRun(
            outcome="OPTIMAL",
            search_complete=True,
            enumeration_complete=True,
            schedule=empty_sched,
            configurations_explored=1,
            states_explored=1,
            peak_memory_mb=peak_memory / (1024 * 1024),
            total_wall_time_ms=elapsed_ms,
        )

    # Generate all Cartesian configurations of variants
    owner_variants: list[list[Variant]] = [c.variants for c in case.candidates]

    configs: list[dict[int, Variant]] = []
    def build_configs(owner_idx: int, current: dict[int, Variant]):
        if owner_idx == n_owners:
            configs.append(dict(current))
            return
        for variant in owner_variants[owner_idx]:
            current[owner_idx] = variant
            build_configs(owner_idx + 1, current)
            del current[owner_idx]

    build_configs(0, {})

    best_schedule: OracleSchedule | None = None
    best_tie_key: tuple | None = None
    configurations_explored = 0
    states_explored = 0

    try:
        for config in configs:
            configurations_explored += 1
            check_budget(configurations_explored, states_explored)

            # Check geometry feasibility
            is_feasible, violations = validate_configuration_geometry(case, config)
            if not is_feasible:
                continue

            # Prepare stroke lookup & lengths using math.fsum for exact binary64 accumulation
            stroke_dict: dict[tuple[int, str, str], Stroke] = {}
            stroke_lengths: dict[tuple[int, str, str], float] = {}
            body_strokes_per_owner: dict[int, list[str]] = {}
            marks_per_owner: dict[int, list[str]] = {}
            mark_precedences: dict[int, list[tuple[str, str]]] = {}
            mark_deadlines: dict[tuple[int, str, str], int] = {}

            for owner_idx, variant in config.items():
                cid = variant.candidate_id
                body_strokes_per_owner[owner_idx] = list(variant.body_order)
                marks_per_owner[owner_idx] = [s.stroke_id for s in variant.strokes if s.role == "mark"]
                mark_precedences[owner_idx] = list(variant.mark_precedence)

                for stroke in variant.strokes:
                    key = (owner_idx, cid, stroke.stroke_id)
                    stroke_dict[key] = stroke
                    stroke_lengths[key] = calculate_stroke_length(stroke.polyline_mm)
                    if stroke.role == "mark":
                        mark_deadlines[key] = resolve_delay(case, owner_idx, cid, stroke)

            total_strokes_count = sum(len(v.strokes) for v in config.values())

            def search(
                owner_body_idx: int,
                body_step: int,
                completed_marks: set[tuple[int, str, str]],
                pen_loc: Point | None,
                actions: list[EvaluatedAction],
                step_downs: list[float],
                step_ups: list[float],
                step_cycles: list[int],
            ):
                nonlocal states_explored, best_schedule, best_tie_key
                states_explored += 1
                check_budget(configurations_explored, states_explored)

                # Base case: all strokes drawn
                if len(actions) == total_strokes_count:
                    # Final transition to p_end
                    end_pt = case.boundary.p_end_mm
                    final_up = point_distance(pen_loc, end_pt) if pen_loc else point_distance(case.boundary.p0_mm, end_pt)

                    all_downs = step_downs
                    all_ups = step_ups + [final_up]
                    all_cycles = step_cycles

                    total_down_mm = math.fsum(all_downs)
                    total_up_mm = math.fsum(all_ups)
                    total_cycles = sum(all_cycles)

                    # Compute exact Fraction cost
                    deltas = [
                        Fraction(d) + Fraction(theta.rho) * Fraction(u) + Fraction(theta.lambda_mm) * c
                        for d, u, c in zip(step_downs, step_ups, step_cycles)
                    ]
                    deltas.append(Fraction(theta.rho) * Fraction(final_up))
                    j_exact = sum(deltas, Fraction(0))
                    j_float = float(j_exact)

                    candidate_ids = [config[i].candidate_id for i in range(n_owners)]
                    sched = OracleSchedule(
                        candidate_ids=candidate_ids,
                        actions=list(actions),
                        L_down_mm=total_down_mm,
                        L_up_mm=total_up_mm,
                        N_cycle=total_cycles,
                        J_mm=j_float,
                        J_exact=j_exact,
                    )

                    sched_key = sched.tie_key()
                    if best_tie_key is None or sched_key < best_tie_key:
                        best_tie_key = sched_key
                        best_schedule = sched
                    return

                # Branch 1: Next BODY stroke
                if owner_body_idx < n_owners:
                    can_start_body = True
                    if body_step == 0:
                        for prev_owner in range(owner_body_idx):
                            prev_cid = config[prev_owner].candidate_id
                            for m_id in marks_per_owner[prev_owner]:
                                m_key = (prev_owner, prev_cid, m_id)
                                if m_key not in completed_marks:
                                    k_val = mark_deadlines[m_key]
                                    if prev_owner + k_val + 1 <= owner_body_idx:
                                        can_start_body = False
                                        break
                            if not can_start_body:
                                break

                    if can_start_body:
                        cid = config[owner_body_idx].candidate_id
                        sid = body_strokes_per_owner[owner_body_idx][body_step]
                        b_key = (owner_body_idx, cid, sid)
                        stroke = stroke_dict[b_key]
                        b_len = stroke_lengths[b_key]

                        next_body_step = body_step + 1
                        next_owner_body = owner_body_idx
                        if next_body_step == len(body_strokes_per_owner[owner_body_idx]):
                            next_owner_body += 1
                            next_body_step = 0

                        orientations = ("forward", "reverse") if stroke.reversible else ("forward",)
                        for orient in orientations:
                            pts = stroke.polyline_mm
                            start_pt = pts[0] if orient == "forward" else pts[-1]
                            end_pt = pts[-1] if orient == "forward" else pts[0]

                            # LIFT
                            lift_up_dist = point_distance(pen_loc if pen_loc else case.boundary.p0_mm, start_pt)
                            lift_action = EvaluatedAction(
                                owner_index=owner_body_idx,
                                candidate_id=cid,
                                stroke_id=sid,
                                orientation=orient,
                                transition="LIFT",
                            )
                            actions.append(lift_action)
                            step_downs.append(b_len)
                            step_ups.append(lift_up_dist)
                            step_cycles.append(1)

                            search(
                                next_owner_body,
                                next_body_step,
                                completed_marks,
                                end_pt,
                                actions,
                                step_downs,
                                step_ups,
                                step_cycles,
                            )

                            step_downs.pop()
                            step_ups.pop()
                            step_cycles.pop()
                            actions.pop()

                            # CONNECT
                            if pen_loc is not None and pen_loc == start_pt and len(actions) > 0:
                                prev_key = actions[-1].as_key()
                                contact_spec = contact_map.get(frozenset((prev_key, b_key)))
                                if contact_spec is not None and tuple(contact_spec.location_mm) == start_pt:
                                    conn_action = EvaluatedAction(
                                        owner_index=owner_body_idx,
                                        candidate_id=cid,
                                        stroke_id=sid,
                                        orientation=orient,
                                        transition="CONNECT",
                                    )
                                    actions.append(conn_action)
                                    step_downs.append(b_len)
                                    step_ups.append(0.0)
                                    step_cycles.append(0)

                                    search(
                                        next_owner_body,
                                        next_body_step,
                                        completed_marks,
                                        end_pt,
                                        actions,
                                        step_downs,
                                        step_ups,
                                        step_cycles,
                                    )

                                    step_downs.pop()
                                    step_ups.pop()
                                    step_cycles.pop()
                                    actions.pop()

                # Branch 2: Available MARK strokes
                for owner_m in range(min(owner_body_idx, n_owners)):
                    cid_m = config[owner_m].candidate_id
                    for m_id in marks_per_owner[owner_m]:
                        m_key = (owner_m, cid_m, m_id)
                        if m_key in completed_marks:
                            continue

                        precedences = mark_precedences[owner_m]
                        preds_satisfied = True
                        for before_id, after_id in precedences:
                            if after_id == m_id:
                                before_key = (owner_m, cid_m, before_id)
                                if before_key not in completed_marks:
                                    preds_satisfied = False
                                    break
                        if not preds_satisfied:
                            continue

                        stroke_m = stroke_dict[m_key]
                        m_len = stroke_lengths[m_key]
                        orientations_m = ("forward", "reverse") if stroke_m.reversible else ("forward",)

                        for orient in orientations_m:
                            pts = stroke_m.polyline_mm
                            start_pt = pts[0] if orient == "forward" else pts[-1]
                            end_pt = pts[-1] if orient == "forward" else pts[0]

                            # LIFT
                            lift_up_dist = point_distance(pen_loc if pen_loc else case.boundary.p0_mm, start_pt)
                            lift_action = EvaluatedAction(
                                owner_index=owner_m,
                                candidate_id=cid_m,
                                stroke_id=m_id,
                                orientation=orient,
                                transition="LIFT",
                            )
                            actions.append(lift_action)
                            completed_marks.add(m_key)
                            step_downs.append(m_len)
                            step_ups.append(lift_up_dist)
                            step_cycles.append(1)

                            search(
                                owner_body_idx,
                                body_step,
                                completed_marks,
                                end_pt,
                                actions,
                                step_downs,
                                step_ups,
                                step_cycles,
                            )

                            step_downs.pop()
                            step_ups.pop()
                            step_cycles.pop()
                            completed_marks.remove(m_key)
                            actions.pop()

                            # CONNECT
                            if pen_loc is not None and pen_loc == start_pt and len(actions) > 0:
                                prev_key = actions[-1].as_key()
                                contact_spec = contact_map.get(frozenset((prev_key, m_key)))
                                if contact_spec is not None and tuple(contact_spec.location_mm) == start_pt:
                                    conn_action = EvaluatedAction(
                                        owner_index=owner_m,
                                        candidate_id=cid_m,
                                        stroke_id=m_id,
                                        orientation=orient,
                                        transition="CONNECT",
                                    )
                                    actions.append(conn_action)
                                    completed_marks.add(m_key)
                                    step_downs.append(m_len)
                                    step_ups.append(0.0)
                                    step_cycles.append(0)

                                    search(
                                        owner_body_idx,
                                        body_step,
                                        completed_marks,
                                        end_pt,
                                        actions,
                                        step_downs,
                                        step_ups,
                                        step_cycles,
                                    )

                                    step_downs.pop()
                                    step_ups.pop()
                                    step_cycles.pop()
                                    completed_marks.remove(m_key)
                                    actions.pop()

            search(
                owner_body_idx=0,
                body_step=0,
                completed_marks=set(),
                pen_loc=None,
                actions=[],
                step_downs=[],
                step_ups=[],
                step_cycles=[],
            )

    except OracleBudgetExceeded as exc:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        if owned_tracer:
            tracemalloc.stop()
        return OracleRun(
            outcome=exc.outcome,
            search_complete=False,
            enumeration_complete=False,
            schedule=best_schedule,
            configurations_explored=configurations_explored,
            states_explored=states_explored,
            peak_memory_mb=peak_memory / (1024 * 1024),
            total_wall_time_ms=elapsed_ms,
        )

    if owned_tracer:
        tracemalloc.stop()

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    if best_schedule is not None:
        outcome = "OPTIMAL"
    else:
        outcome = "INFEASIBLE"

    return OracleRun(
        outcome=outcome,
        search_complete=True,
        enumeration_complete=True,
        schedule=best_schedule,
        configurations_explored=configurations_explored,
        states_explored=states_explored,
        peak_memory_mb=peak_memory / (1024 * 1024),
        total_wall_time_ms=elapsed_ms,
    )
