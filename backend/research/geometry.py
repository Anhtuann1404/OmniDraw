"""TV4 DEV polyline geometry; TV3 must implement independent primitives.

All simultaneously selectable stroke pairs are checked, irrespective of client
separation_pairs. A declared contact exempts only its finite disk. Self crossings
and overlapping/backtracking adjacent segments are rejected under this DEV
policy. Numeric/contact/quality policy approval for research freeze is PENDING.
"""

from dataclasses import dataclass
from itertools import combinations
from math import dist, isfinite, sqrt

from .schemas import ResearchCase, Schedule
from .schedule_checker import EXACT_CONTACT_POLICY, StrokeKey

FLATTEN_POLICY = "tv4-dev-polyline-v1"
NUMERIC_POLICY = "tv4-dev-float-v1"
SEPARATION_POLICY = "tv4-dev-all-pairs-v1"


def cross(a, b, c):
    value = (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])
    if not isfinite(value):
        raise ValueError("Geometry arithmetic overflow")
    return value


def on_segment(p, a, b):
    return cross(a, b, p) == 0 and all(min(a[j], b[j]) <= p[j] <= max(a[j], b[j]) for j in (0, 1))


def intersects(a, b, c, d):
    x, y, z, w = cross(a, b, c), cross(a, b, d), cross(c, d, a), cross(c, d, b)
    opposite = lambda u, v: (u < 0 < v) or (v < 0 < u)
    return (opposite(x, y) and opposite(z, w)) or any(
        value == 0 and on_segment(p, u, v)
        for value, p, u, v in ((x, c, a, b), (y, d, a, b), (z, a, c, d), (w, b, c, d)))


def point_distance(p, a, b):
    vx, vy = b[0] - a[0], b[1] - a[1]
    den = vx * vx + vy * vy
    if not isfinite(den):
        raise ValueError("Geometry arithmetic overflow")
    if den == 0:
        return dist(p, a)
    t = ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / den
    if not isfinite(t):
        raise ValueError("Geometry arithmetic overflow")
    t = max(0.0, min(1.0, t))
    return dist(p, (a[0] + t * vx, a[1] + t * vy))


def segment_distance(a, b, c, d):
    if intersects(a, b, c, d):
        return 0.0
    return min(point_distance(a, c, d), point_distance(b, c, d),
               point_distance(c, a, b), point_distance(d, a, b))


def outside_disk(a, b, contact):
    """Clip one segment; retained pieces lie outside the declared contact disk."""
    center, radius = contact.location_mm, contact.radius_mm
    vx, vy = b[0] - a[0], b[1] - a[1]
    dx, dy = a[0] - center[0], a[1] - center[1]
    den = vx * vx + vy * vy
    if den == 0:
        return [] if dist(a, center) <= radius else [(a, b)]
    linear = dx * vx + dy * vy
    constant = dx * dx + dy * dy - radius * radius
    discriminant = linear * linear - den * constant
    if not all(isfinite(x) for x in (den, linear, constant, discriminant)):
        raise ValueError("Geometry arithmetic overflow")
    if discriminant <= 0:
        return [(a, b)]
    lo = max(0.0, (-linear - sqrt(discriminant)) / den)
    hi = min(1.0, (-linear + sqrt(discriminant)) / den)
    if lo >= hi:
        return [(a, b)]
    point = lambda t: (a[0] + t * vx, a[1] + t * vy)
    return ([(a, point(lo))] if lo > 0 else []) + ([(point(hi), b)] if hi < 1 else [])


def polyline_clearance(first, second, contact=None, guard=lambda: None):
    pieces = []
    for points in (first, second):
        segments = []
        for a, b in zip(points, points[1:]):
            guard()
            segments.extend(outside_disk(a, b, contact) if contact else [(a, b)])
        pieces.append(segments)
    minimum = None
    for a, b in pieces[0]:
        for c, d in pieces[1]:
            guard()
            value = segment_distance(a, b, c, d)
            minimum = value if minimum is None else min(minimum, value)
    return minimum


def self_intersects(points, guard=lambda: None):
    segments = [(a, b) for a, b in zip(points, points[1:]) if a != b]
    for j, (a, b) in enumerate(segments):
        for h, (c, d) in enumerate(segments[j + 1:], j + 1):
            guard()
            if h == j + 1:
                # The shared endpoint is allowed; a reversal along the same line is not.
                if cross(a, b, d) == 0 and (on_segment(d, a, b) or on_segment(a, c, d)):
                    return True
            elif intersects(a, b, c, d):
                return True
    return False


@dataclass
class GeometryIndex:
    variants: dict
    strokes: dict
    invalid_variants: set
    incompatible: set
    future_neighbors: dict
    contacts: dict
    pair_checks: int

    def compatible(self, owner, cid, assignments):
        choice = (owner, cid)
        return choice not in self.invalid_variants and all(
            frozenset((choice, other)) not in self.incompatible for other in assignments)


def compile_geometry(case: ResearchCase, guard=lambda: None) -> GeometryIndex:
    """Conservative interaction graph over every candidate, before state merging."""
    policy = case.geometry_policy
    if (policy.flatten_policy_id != FLATTEN_POLICY or policy.numeric_policy_id != NUMERIC_POLICY
            or policy.separation_policy_id != SEPARATION_POLICY
            or policy.contact_policy_id != EXACT_CONTACT_POLICY):
        raise ValueError("Unsupported geometry policy; DEV policies must be declared explicitly")
    variants = {(c.owner_index, v.candidate_id): v for c in case.candidates for v in c.variants}
    strokes = {(owner, cid, s.stroke_id): s for (owner, cid), v in variants.items() for s in v.strokes}
    contacts = {frozenset((c.first.key(), c.second.key())): c for c in case.contacts}
    for contact in case.contacts:
        guard()
        if contact.policy_id != EXACT_CONTACT_POLICY:
            raise ValueError("Unsupported contact policy")
        for ref in (contact.first, contact.second):
            points = strokes[ref.key()].polyline_mm
            if contact.location_mm not in (points[0], points[-1]):
                raise ValueError("DEV contact location must be an endpoint of both strokes")
    invalid, incompatible = set(), set()
    neighbors = {i: set() for i in range(len(case.candidates))}
    pair_checks = 0
    for key, stroke in strokes.items():
        guard()
        if self_intersects(stroke.polyline_mm, guard):
            invalid.add(key[:2])
    for first, second in combinations(strokes, 2):
        guard()
        if first[0] == second[0] and first[1] != second[1]:
            continue
        value = polyline_clearance(strokes[first].polyline_mm, strokes[second].polyline_mm,
                                   contacts.get(frozenset((first, second))), guard)
        pair_checks += 1
        if value is not None and value < policy.c_min_mm:
            if first[:2] == second[:2]:
                invalid.add(first[:2])
            else:
                incompatible.add(frozenset((first[:2], second[:2])))
                neighbors[first[0]].add(second[0])
                neighbors[second[0]].add(first[0])
    return GeometryIndex(variants, strokes, invalid, incompatible, neighbors, contacts, pair_checks)


def check_selected_geometry(case: ResearchCase, schedule: Schedule):
    """TV4 geometry check only; independent validation remains NOT_RUN."""
    from .schemas import check_schedule_structure
    case = ResearchCase.model_validate(case.model_dump(mode="json"))
    schedule = Schedule.model_validate(schedule.model_dump(mode="json"))
    check_schedule_structure(case, schedule)
    index = compile_geometry(case)
    selected = []
    for owner, cid in enumerate(schedule.candidate_ids):
        if not index.compatible(owner, cid, selected):
            raise ValueError("Selected geometry violates DEV separation/self-intersection policy")
        selected.append((owner, cid))
    return {"checker_id": "tv4-dev-geometry", "status": "PASS", "independent_validation": "NOT_RUN"}
