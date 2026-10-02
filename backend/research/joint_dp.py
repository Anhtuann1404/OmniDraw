"""TV4 single-objective DEV DP for Docs 31; no TV3 oracle/sign-off claims.

Both modes use the same recurrence. no-forget retains all assignments;
safe-forget drops completed owners only after pending and future interactions
close. Endpoint descriptors remain independent. Never imports product solvers.
Offline use only: memory guarding uses process-wide tracemalloc.
"""

from dataclasses import dataclass
from heapq import heappop, heappush
from math import dist, fsum, isfinite
from time import monotonic
import tracemalloc

from .geometry import compile_geometry
from .schedule_checker import ScheduleReplay, check_schedule_cost
from .schemas import Budget, ResearchCase, Schedule, ScheduleAction, StrokeRef, Theta

TIE_POLICY = "tv4-dev-float-lex-actions-v1"


@dataclass(frozen=True)
class State:
    i: int = 0
    t: int = 0
    A: tuple = ()
    P: tuple = ()
    e: tuple | None = None  # (owner,candidate,stroke,orientation), never resolved through A


@dataclass(frozen=True)
class JointRun:
    outcome: str
    search_complete: bool
    schedule: Schedule | None
    replay: ScheduleReplay | None
    diagnostics: dict
    mode: str
    tie_policy_id: str = TIE_POLICY
    independent_validation: str = "NOT_RUN"
    scope: str = "full_candidate_set"
    candidate_set_sha256: str = ""
    configuration_candidate_ids: tuple[str, ...] | None = None


class BudgetExceeded(Exception):
    def __init__(self, outcome):
        self.outcome = outcome


def solve_joint(case: ResearchCase, theta: Theta, budget: Budget, *, safe_forget=False) -> JointRun:
    """Solve the full finite candidate set under explicitly supported DEV policies.

    max_states bounds all distinct stored states; wall-time/memory include geometry
    preprocessing. No Cartesian enumeration is performed, so max_configurations
    is not consumed. Budget interruption retains a completed incumbent, if found.
    OPTIMAL is a DEV float-model search claim, not independent acceptance.
    """
    return _solve(case, theta, budget, safe_forget=safe_forget, configuration=None)


def solve_fixed_configuration(case: ResearchCase, candidate_ids: list[str] | tuple[str, ...],
                              theta: Theta, budget: Budget, *, safe_forget=False) -> JointRun:
    """Minimize schedules for one configuration, keeping the original case/hash.

    IDs must select exactly one variant per owner, in owner order. INFEASIBLE
    and OPTIMAL refer only to this configuration. No ranking, prefix verdict or
    independent validation is supplied. TV2 owns aggregate top-m budgets/status.
    """
    if not isinstance(candidate_ids, (list, tuple)) or any(type(cid) is not str for cid in candidate_ids):
        raise ValueError("candidate_ids must be a list/tuple of candidate ID strings in owner order")
    return _solve(case, theta, budget, safe_forget=safe_forget,
                  configuration=tuple(candidate_ids))


def _solve(case, theta, budget, *, safe_forget, configuration):
    started = monotonic()
    budget = Budget.model_validate(budget.model_dump(mode="json"))
    owned_tracer = not tracemalloc.is_tracing()
    if owned_tracer:
        tracemalloc.start()
    initial_memory = tracemalloc.get_traced_memory()[0]
    peak_memory = 0
    best = {}
    transitions = pair_checks = peak_A = peak_P = peak_frontier = 0
    incumbent = None
    incumbent_cost = None
    incumbent_tie = None

    def guard():
        nonlocal peak_memory
        memory = max(0, tracemalloc.get_traced_memory()[0] - initial_memory)
        peak_memory = max(peak_memory, memory)
        if (monotonic() - started) * 1000 >= budget.wall_time_ms:
            raise BudgetExceeded("TIMEOUT")
        if memory >= budget.memory_limit_mb * 1024 * 1024:
            raise BudgetExceeded("RESOURCE_LIMIT")

    def reconstruct(state):
        actions = []
        while best[state][2] is not None:
            previous, action = best[state][2:]
            actions.append(action)
            state = previous
        actions.reverse()
        ids = {}
        for key, orientation, transition in actions:
            ids[key[0]] = key[1]
        return Schedule(candidate_ids=[ids[i] for i in range(len(case.candidates))],
                        actions=[ScheduleAction(stroke=StrokeRef(owner_index=key[0], candidate_id=key[1],
                                                                stroke_id=key[2]),
                                                orientation=orientation, transition=transition)
                                 for key, orientation, transition in actions],
                        boundary_convention_id=case.boundary.convention_id)

    try:
        case = ResearchCase.model_validate(case.model_dump(mode="json"))
        theta = Theta.model_validate(theta.model_dump(mode="json"))
        if case.split not in {"dev", "synthetic"}:
            raise ValueError("DEV joint solver accepts only dev/synthetic cases; HOLDOUT remains closed")
        if configuration is not None:
            if len(configuration) != len(case.candidates):
                raise ValueError("candidate_ids must select exactly one candidate per owner")
            for row, cid in zip(case.candidates, configuration):
                if cid not in {variant.candidate_id for variant in row.variants}:
                    raise ValueError(f"Unknown candidate ID for owner {row.owner_index}: {cid}")
        index = compile_geometry(case, guard)
        pair_checks = index.pair_checks
        lengths = {}
        for key, stroke in index.strokes.items():
            guard()
            lengths[key] = fsum(dist(a, b) for a, b in zip(stroke.polyline_mm, stroke.polyline_mm[1:]))
            if not isfinite(lengths[key]):
                raise ValueError("Non-finite stroke length")
        n = len(case.candidates)

        def endpoint(e):
            if e is None:
                return case.boundary.p0_mm
            points = index.strokes[e[:3]].polyline_mm
            return points[-1] if e[3] == "forward" else points[0]

        def delay(key):
            qualified = "/".join(map(str, key))
            return case.delay_policy[qualified] if qualified in case.delay_policy else case.delay_policy[index.strokes[key].mark_type]

        def available(state):
            if state.i < n and (state.t or not any(p[0] + delay(p) + 1 <= state.i for p in state.P)):
                choices = ([(state.i, dict(state.A)[state.i])] if state.t else
                           ([(state.i, configuration[state.i])] if configuration is not None else
                            sorted((owner, cid) for owner, cid in index.variants if owner == state.i)))
                for owner, cid in choices:
                    guard()
                    if state.t or index.compatible(owner, cid, state.A):
                        variant = index.variants[(owner, cid)]
                        yield (owner, cid, variant.body_order[state.t]), "BODY"
            for key in state.P:
                variant = index.variants[key[:2]]
                if all((key[0], key[1], before) not in state.P
                       for before, after in variant.mark_precedence if after == key[2]):
                    yield key, "MARK"

        def successor(state, key, kind, orientation):
            i, t, assignments, pending = state.i, state.t, state.A, set(state.P)
            if kind == "BODY":
                if t == 0:
                    assignments = assignments + (key[:2],)
                variant = index.variants[key[:2]]
                t += 1
                if t == len(variant.body_order):
                    pending.update((i, key[1], s.stroke_id) for s in variant.strokes if s.role == "mark")
                    i, t = i + 1, 0
            else:
                pending.remove(key)
            if safe_forget:
                pending_owners = {p[0] for p in pending}
                unchosen = i + bool(t)
                assignments = tuple((owner, cid) for owner, cid in assignments
                                    if owner >= i or owner in pending_owners
                                    or any(j >= unchosen for j in index.future_neighbors[owner]))
            return State(i, t, assignments, tuple(sorted(pending)), key + (orientation,))

        def consider_end(state):
            nonlocal incumbent, incumbent_cost, incumbent_tie
            if state.i == n and state.t == 0 and not state.P:
                cost, tie = best[state][:2]
                cost += theta.rho * dist(endpoint(state.e), case.boundary.p_end_mm)
                if not isfinite(cost):
                    raise ValueError("Non-finite END cost")
                if incumbent_cost is None or (cost, tie) < (incumbent_cost, incumbent_tie):
                    incumbent, incumbent_cost, incumbent_tie = state, cost, tie

        start = State()
        best[start] = (0.0, (), None, None)
        queue = [(0, 0, 0, 0, start)]
        serial = 0
        processed = set()
        consider_end(start)
        while queue:
            guard()
            *_, state = heappop(queue)
            if state in processed:
                continue
            processed.add(state)
            cost, tie = best[state][:2]
            for key, kind in available(state):
                stroke = index.strokes[key]
                for orientation in (("forward", "reverse") if stroke.reversible else ("forward",)):
                    points = stroke.polyline_mm
                    startpoint = points[0] if orientation == "forward" else points[-1]
                    choices = ["LIFT"]
                    if state.e is not None and endpoint(state.e) == startpoint:
                        contact = index.contacts.get(frozenset((state.e[:3], key)))
                        if contact is not None and contact.location_mm == startpoint:
                            choices.insert(0, "CONNECT")
                    for transition in choices:
                        guard()
                        transitions += 1
                        delta = lengths[key]
                        if transition == "LIFT":
                            delta += theta.rho * dist(endpoint(state.e), startpoint) + theta.lambda_mm
                        value = cost + delta
                        if not isfinite(value):
                            raise ValueError("Non-finite DP cost")
                        action = (key, orientation, transition)
                        path_tie = tie + (action,)
                        other = successor(state, key, kind, orientation)
                        transient = state.A + ((key[:2],) if kind == "BODY" and state.t == 0 else ())
                        unchosen_before = state.i + bool(state.t or kind == "BODY")
                        frontier_before = sum(owner == state.i or any(j >= unchosen_before for j in index.future_neighbors[owner])
                                              for owner, cid in transient)
                        peak_A = max(peak_A, len(transient))
                        peak_frontier = max(peak_frontier, frontier_before)
                        old = best.get(other)
                        if old is not None and (old[0], old[1]) <= (value, path_tie):
                            continue
                        if old is None and len(best) >= budget.max_states:
                            raise BudgetExceeded("RESOURCE_LIMIT")
                        best[other] = (value, path_tie, state, action)
                        serial += 1
                        heappush(queue, (other.i, other.t, -len(other.P), serial, other))
                        peak_A, peak_P = max(peak_A, len(other.A)), max(peak_P, len(other.P))
                        unchosen = other.i + bool(other.t)
                        frontier = sum(owner == other.i or any(j >= unchosen for j in index.future_neighbors[owner])
                                       for owner, cid in other.A)
                        peak_frontier = max(peak_frontier, frontier)
                        consider_end(other)
        outcome, complete = ("OPTIMAL" if incumbent is not None else "INFEASIBLE"), True
    except BudgetExceeded as error:
        outcome, complete = error.outcome, False
    except Exception:
        if owned_tracer:
            tracemalloc.stop()
        raise

    try:
        schedule = reconstruct(incumbent) if incumbent is not None else None
        replay = check_schedule_cost(case, schedule, theta) if schedule is not None else None
        # Retain a verified incumbent on late replay overrun, but never claim an
        # in-budget optimum. The cooperative guard includes replay allocations.
        try:
            guard()
        except BudgetExceeded as error:
            outcome, complete = error.outcome, False
    finally:
        if owned_tracer:
            tracemalloc.stop()
    return JointRun(outcome, complete, schedule, replay,
                    {"wall_time_ms": (monotonic() - started) * 1000, "peak_states": len(best),
                     "transitions": transitions, "geometry_pair_checks": pair_checks,
                     "peak_assignments": peak_A, "peak_pending": peak_P,
                     "peak_frontier": peak_frontier, "tracked_peak_memory_mb": peak_memory / (1024 * 1024),
                     "enumeration_complete": False, "ranking_complete": False,
                     "configuration_enumeration": "NOT_PERFORMED"},
                    "safe-forget" if safe_forget else "no-forget",
                    scope="fixed_configuration" if configuration is not None else "full_candidate_set",
                    candidate_set_sha256=case.candidate_set_sha256,
                    configuration_candidate_ids=configuration)
