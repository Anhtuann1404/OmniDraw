"""TV4 schedule/cost replay for Docs 31 §§2,4,5; NOT an independent oracle.

No clearance, self-intersection, quality-gate or optimum claims. CONNECT support
is deliberately limited to the explicit DEV exact-endpoint policy below.
Nothing here registers an API adapter or upgrades independent validation.
"""

from dataclasses import dataclass
from math import dist, fsum, isfinite

from .schemas import ResearchCase, Schedule, Theta, check_schedule_structure

CHECKER_ID = "tv4-schedule-cost-replay"
CHECKER_VERSION = "dev-v2"
EXACT_CONTACT_POLICY = "tv4-dev-exact-endpoint-v1"

StrokeKey = tuple[int, str, str]


@dataclass(frozen=True)
class ReplayStep:
    kind: str
    stroke: StrokeKey | None
    orientation: str | None
    transition: str | None
    i: int
    t: int
    assignments: tuple[tuple[int, str], ...]
    pending: tuple[StrokeKey, ...]
    endpoint_mm: tuple[float, float]
    delta_down_mm: float
    delta_up_mm: float
    delta_cycles: int
    delta_J_mm: float


@dataclass(frozen=True)
class ScheduleReplay:
    L_down_mm: float
    L_up_mm: float
    N_cycle: int
    J_mm: float
    trace: tuple[ReplayStep, ...]
    checker_id: str = CHECKER_ID
    checker_version: str = CHECKER_VERSION
    geometric_validation: str = "NOT_RUN"
    independent_validation: str = "NOT_RUN"


def check_schedule_cost(case: ResearchCase, schedule: Schedule, theta: Theta) -> ScheduleReplay:
    """Raise ValueError on invalid ordering/transition or unsupported CONNECT.

    Revalidate typed inputs to catch mutation/model_construct bypasses. Returned
    coefficients describe this schedule only, not geometric feasibility or an
    optimum. All chosen assignments are retained in the trace (no forgetting).
    """
    case = ResearchCase.model_validate(case.model_dump(mode="json"))
    schedule = Schedule.model_validate(schedule.model_dump(mode="json"))
    theta = Theta.model_validate(theta.model_dump(mode="json"))
    check_schedule_structure(case, schedule)
    variants = [next(v for v in c.variants if v.candidate_id == cid)
                for c, cid in zip(case.candidates, schedule.candidate_ids)]
    strokes = {(owner, v.candidate_id, s.stroke_id): s
               for owner, v in enumerate(variants) for s in v.strokes}
    contacts = {frozenset((c.first.key(), c.second.key())): c for c in case.contacts}
    pending = set()
    drawn = set()
    assignments = []
    trace = []
    i = t = 0
    endpoint = case.boundary.p0_mm
    previous = None

    def delay(key):
        qualified = "/".join(map(str, key))
        if qualified in case.delay_policy:
            return case.delay_policy[qualified]
        return case.delay_policy[strokes[key].mark_type]

    for action in schedule.actions:
        key = action.stroke.key()
        owner, cid, sid = key
        stroke = strokes[key]
        variant = variants[owner]
        if stroke.role == "body":
            if owner != i or sid != variant.body_order[t]:
                raise ValueError("BODY must follow owner order and declared body_order")
            if t == 0:
                if any(p[0] + delay(p) + 1 <= i for p in pending):
                    raise ValueError("Pending MARK deadline forbids starting this BODY")
                assignments.append((owner, cid))
            t += 1
            if t == len(variant.body_order):
                pending.update((owner, cid, s.stroke_id) for s in variant.strokes if s.role == "mark")
                i += 1
                t = 0
            kind = "BODY"
        else:
            if key not in pending:
                raise ValueError("MARK requires its completed owner BODY")
            if any((owner, cid, before) not in drawn
                   for before, after in variant.mark_precedence if after == sid):
                raise ValueError("MARK predecessor has not been drawn")
            pending.remove(key)
            kind = "MARK"

        points = stroke.polyline_mm
        start, end = (points[-1], points[0]) if action.orientation == "reverse" else (points[0], points[-1])
        down = fsum(dist(a, b) for a, b in zip(points, points[1:]))
        if action.transition == "CONNECT":
            contact = contacts.get(frozenset((previous, key)))
            if contact is None:
                raise ValueError("CONNECT requires an explicit stroke-pair contact")
            if (case.geometry_policy.contact_policy_id != EXACT_CONTACT_POLICY
                    or contact.policy_id != EXACT_CONTACT_POLICY):
                raise ValueError("Unsupported CONNECT policy; only DEV exact endpoints are implemented")
            if endpoint != start or start != contact.location_mm:
                raise ValueError("CONNECT endpoints must equal the declared contact location")
            up, cycles = 0.0, 0
        else:
            up, cycles = dist(endpoint, start), 1
        delta = down + theta.rho * up + theta.lambda_mm * cycles
        if not all(isfinite(v) for v in (down, up, delta)):
            raise ValueError("Non-finite replay cost")
        endpoint, previous = end, key
        drawn.add(key)
        trace.append(ReplayStep(kind, key, action.orientation, action.transition, i, t,
                                tuple(assignments), tuple(sorted(pending)), endpoint,
                                down, up, cycles, delta))

    if i != len(variants) or t != 0 or pending:
        raise ValueError("END requires every BODY and MARK to be complete")
    end_up = dist(endpoint, case.boundary.p_end_mm)
    trace.append(ReplayStep("END", None, None, None, i, t, tuple(assignments), (),
                            case.boundary.p_end_mm, 0.0, end_up, 0, theta.rho * end_up))
    down = fsum(step.delta_down_mm for step in trace)
    up = fsum(step.delta_up_mm for step in trace)
    cycles = sum(step.delta_cycles for step in trace)
    objective = down + theta.rho * up + theta.lambda_mm * cycles
    if not all(isfinite(v) for v in (down, up, objective)):
        raise ValueError("Non-finite replay cost")
    return ScheduleReplay(down, up, cycles, objective, tuple(trace))
