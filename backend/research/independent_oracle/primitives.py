"""Independent geometry primitives for polyline centerline distance, intersection,
collinear segments, degenerate points, self-intersection, and contact disks.

Written independently by TV3 from Docs 31 specifications without importing TV4 DP,
geometry, or schedule checker modules.
"""

from __future__ import annotations

import math
from typing import Any, Sequence

Point = tuple[float, float]
Segment = tuple[Point, Point]

# Contract constants from Docs 31
C_MIN_MM = 0.20


def point_distance(p1: Point, p2: Point) -> float:
    """Euclidean distance between two 2D points with overflow check."""
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    dist = math.hypot(dx, dy)
    if math.isinf(dist) or math.isnan(dist):
        raise ValueError("Arithmetic overflow in geometry calculation")
    return dist


def point_to_segment_distance(p: Point, a: Point, b: Point) -> float:
    """Euclidean distance from point p to segment [a, b]."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    l2 = dx * dx + dy * dy
    if math.isinf(l2) or math.isnan(l2):
        raise ValueError("Arithmetic overflow in geometry calculation")
    if l2 == 0.0:
        return point_distance(p, a)
    px = p[0] - a[0]
    py = p[1] - a[1]
    t = (px * dx + py * dy) / l2
    if t <= 0.0:
        return point_distance(p, a)
    if t >= 1.0:
        return point_distance(p, b)
    proj = (a[0] + t * dx, a[1] + t * dy)
    return point_distance(p, proj)


def cross_product(p: Point, q: Point, r: Point) -> float:
    """2D cross product of vectors (q - p) and (r - p)."""
    val = (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    if math.isinf(val) or math.isnan(val):
        raise ValueError("Arithmetic overflow in geometry calculation")
    return val


def is_on_segment(p: Point, a: Point, b: Point) -> bool:
    """Returns True if point p lies on segment [a, b], assuming p is collinear with ab."""
    min_x = min(a[0], b[0])
    max_x = max(a[0], b[0])
    min_y = min(a[1], b[1])
    max_y = max(a[1], b[1])
    return min_x <= p[0] <= max_x and min_y <= p[1] <= max_y


def segments_intersect(a: Point, b: Point, c: Point, d: Point) -> bool:
    """Determines whether segment [a, b] and segment [c, d] intersect (touching or crossing)."""
    # Degenerate cases: point to segment or point to point
    if a == b and c == d:
        return a == c
    if a == b:
        return cross_product(c, d, a) == 0.0 and is_on_segment(a, c, d)
    if c == d:
        return cross_product(a, b, c) == 0.0 and is_on_segment(c, a, b)

    d1 = cross_product(c, d, a)
    d2 = cross_product(c, d, b)
    d3 = cross_product(a, b, c)
    d4 = cross_product(a, b, d)

    # General intersection (straddling)
    if ((d1 > 0 and d2 < 0) or (d1 < 0 and d2 > 0)) and ((d3 > 0 and d4 < 0) or (d3 < 0 and d4 > 0)):
        return True

    # Collinear or endpoint touching
    if d1 == 0.0 and is_on_segment(a, c, d):
        return True
    if d2 == 0.0 and is_on_segment(b, c, d):
        return True
    if d3 == 0.0 and is_on_segment(c, a, b):
        return True
    if d4 == 0.0 and is_on_segment(d, a, b):
        return True

    return False


def segment_distance(a: Point, b: Point, c: Point, d: Point) -> float:
    """Minimum Euclidean distance between segment [a, b] and segment [c, d].

    Returns 0.0 if the segments intersect, touch, or overlap.
    """
    if segments_intersect(a, b, c, d):
        return 0.0

    return min(
        point_to_segment_distance(a, c, d),
        point_to_segment_distance(b, c, d),
        point_to_segment_distance(c, a, b),
        point_to_segment_distance(d, a, b),
    )


def self_intersects(points: Sequence[Point]) -> bool:
    """Determines whether a polyline self-intersects according to Docs 31 §3.

    Consecutive duplicate points are filtered. Non-adjacent segments are checked for intersection.
    Adjacent segments sharing a vertex are permitted unless they backtrack 180 degrees
    along the same line.
    """
    if len(points) < 2:
        return False

    # Filter out consecutive duplicate points
    deduped: list[Point] = [points[0]]
    for pt in points[1:]:
        if pt != deduped[-1]:
            deduped.append(pt)

    if len(deduped) < 3:
        return False

    segments: list[Segment] = [(deduped[i], deduped[i + 1]) for i in range(len(deduped) - 1)]

    for j, (a, b) in enumerate(segments):
        for h in range(j + 1, len(segments)):
            c, d = segments[h]
            if h == j + 1:
                # Adjacent segments share vertex b == c.
                # A 180-degree reversal along the same line is an invalid self-intersection.
                if cross_product(a, b, d) == 0.0 and (is_on_segment(d, a, b) or is_on_segment(a, b, d)):
                    return True
            else:
                if segments_intersect(a, b, c, d):
                    return True

    return False


def clip_segment_outside_disk(a: Point, b: Point, center: Point, radius: float) -> list[Segment]:
    """Clips segment [a, b] against an open disk B(center, radius).

    Returns a list of 0, 1, or 2 subsegments lying strictly outside the disk (distance >= radius).
    """
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    wx = a[0] - center[0]
    wy = a[1] - center[1]

    a_quad = dx * dx + dy * dy
    b_quad = 2.0 * (dx * wx + dy * wy)
    c_quad = wx * wx + wy * wy - radius * radius

    if math.isinf(a_quad) or math.isinf(b_quad) or math.isinf(c_quad):
        raise ValueError("Arithmetic overflow in geometry calculation")

    if a_quad == 0.0:
        # Segment is a single point
        if wx * wx + wy * wy < radius * radius:
            return []
        return [(a, b)]

    discrim = b_quad * b_quad - 4.0 * a_quad * c_quad
    if math.isinf(discrim) or math.isnan(discrim):
        raise ValueError("Arithmetic overflow in geometry calculation")

    if discrim <= 0.0:
        # Line does not enter disk interior; whole segment is outside
        return [(a, b)]

    sqrt_d = math.sqrt(discrim)
    t1 = (-b_quad - sqrt_d) / (2.0 * a_quad)
    t2 = (-b_quad + sqrt_d) / (2.0 * a_quad)
    if t1 > t2:
        t1, t2 = t2, t1

    # Portions inside disk: t in (t1, t2).
    # Outside portions inside parameter range [0.0, 1.0]:
    pieces: list[Segment] = []

    # First piece: [0.0, min(1.0, t1)]
    if t1 > 0.0:
        end_t = min(1.0, t1)
        if end_t > 0.0:
            p_end = (a[0] + end_t * dx, a[1] + end_t * dy)
            pieces.append((a, p_end))

    # Second piece: [max(0.0, t2), 1.0]
    if t2 < 1.0:
        start_t = max(0.0, t2)
        if start_t < 1.0:
            p_start = (a[0] + start_t * dx, a[1] + start_t * dy)
            pieces.append((p_start, b))

    return pieces


def polyline_clearance(
    poly1: Sequence[Point],
    poly2: Sequence[Point],
    contact_spec: Any | None = None,
) -> float | None:
    """Calculates minimum distance between centerlines of two polylines.

    If contact_spec is provided, segments inside the contact disk B(location_mm, radius_mm)
    are exempt from clearance check. Only portions outside the disk are compared.

    Returns None if polylines have fewer than 2 points or have no portions outside contact disk.
    """
    if len(poly1) < 2 or len(poly2) < 2:
        return None

    # Filter consecutive duplicates
    pts1: list[Point] = [poly1[0]]
    for p in poly1[1:]:
        if p != pts1[-1]:
            pts1.append(p)

    pts2: list[Point] = [poly2[0]]
    for p in poly2[1:]:
        if p != pts2[-1]:
            pts2.append(p)

    if len(pts1) < 2 or len(pts2) < 2:
        return None

    segs1: list[Segment] = [(pts1[i], pts1[i + 1]) for i in range(len(pts1) - 1)]
    segs2: list[Segment] = [(pts2[i], pts2[i + 1]) for i in range(len(pts2) - 1)]

    if contact_spec is not None:
        loc = getattr(contact_spec, "location_mm", None)
        rad = getattr(contact_spec, "radius_mm", None)
        if loc is None and isinstance(contact_spec, dict):
            loc = contact_spec.get("location_mm")
            rad = contact_spec.get("radius_mm")
        center = (float(loc[0]), float(loc[1]))
        radius = float(rad)

        clipped1: list[Segment] = []
        for s in segs1:
            clipped1.extend(clip_segment_outside_disk(s[0], s[1], center, radius))

        clipped2: list[Segment] = []
        for s in segs2:
            clipped2.extend(clip_segment_outside_disk(s[0], s[1], center, radius))

        segs1 = clipped1
        segs2 = clipped2

    if not segs1 or not segs2:
        return None

    min_dist: float | None = None
    for a, b in segs1:
        for c, d in segs2:
            d_val = segment_distance(a, b, c, d)
            if min_dist is None or d_val < min_dist:
                min_dist = d_val

    return min_dist
