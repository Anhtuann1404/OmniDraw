"""Tests for TV3 independent geometry primitives and clearance boundaries.

Authored independently by TV3 following Docs 31 §3 and Docs 32.
Validates 0.19 / 0.20 / 0.21 mm clearance boundaries, contact disk exemptions,
degenerate segments, collinear segments, self-intersections, and arithmetic guards.
"""

from __future__ import annotations

import math
import pytest

from backend.research.independent_oracle.primitives import (
    C_MIN_MM,
    clip_segment_outside_disk,
    point_distance,
    point_to_segment_distance,
    polyline_clearance,
    segment_distance,
    segments_intersect,
    self_intersects,
)


# ---------------------------------------------------------------------------
# 1. Hand-calculated Clearance Boundaries: 0.19 / 0.20 / 0.21 mm
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("gap,expected_feasible", [
    (0.19, False),   # Strictly below c_min = 0.20 mm -> INFEASIBLE
    (0.20, True),    # Exactly at c_min = 0.20 mm -> FEASIBLE boundary
    (0.21, True),    # Strictly above c_min = 0.20 mm -> FEASIBLE
])
def test_clearance_boundary_019_020_021(gap: float, expected_feasible: bool):
    """Hand-calculated test: two parallel segments at distance gap.
    Clearance must match gap, and feasibility against c_min must be exact.
    """
    poly1 = [(0.0, 0.0), (1.0, 0.0)]
    poly2 = [(0.0, gap), (1.0, gap)]

    clearance = polyline_clearance(poly1, poly2)
    assert clearance is not None
    assert math.isclose(clearance, gap, rel_tol=1e-9)

    is_feasible = clearance >= C_MIN_MM
    assert is_feasible is expected_feasible


# ---------------------------------------------------------------------------
# 2. Segment Intersection, Degeneracy, and Collinearity
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("segments,expected_dist", [
    # Crossing X shape at (1, 1) -> distance 0
    (((0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0)), 0.0),
    # Collinear overlapping segments along x-axis -> distance 0
    (((0.0, 0.0), (2.0, 0.0), (1.0, 0.0), (3.0, 0.0)), 0.0),
    # Collinear disjoint segments with gap 1.0 along x-axis -> distance 1.0
    (((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)), 1.0),
    # Degenerate point to point (0,0) and (3,4) -> distance 5.0 (Pythagorean 3-4-5)
    (((0.0, 0.0), (0.0, 0.0), (3.0, 4.0), (3.0, 4.0)), 5.0),
    # T-junction touching at endpoint (1, 0) -> distance 0.0
    (((0.0, 0.0), (1.0, 0.0), (1.0, 0.0), (1.0, 1.0)), 0.0),
    # Parallel segments of length 1 separated vertically by 0.5 -> distance 0.5
    (((0.0, 0.0), (1.0, 0.0), (0.0, 0.5), (1.0, 0.5)), 0.5),
    # Degenerate point (0, 0) to segment [(0, 1), (0, 3)] -> distance 1.0
    (((0.0, 0.0), (0.0, 0.0), (0.0, 1.0), (0.0, 3.0)), 1.0),
])
def test_segment_distance_hand_cases(segments, expected_dist):
    a, b, c, d = segments
    dist = segment_distance(a, b, c, d)
    assert math.isclose(dist, expected_dist, abs_tol=1e-9)


def test_point_to_segment_projections():
    """Verify orthogonal projection vs clamp to endpoints."""
    # Point projects orthogonally onto segment
    assert math.isclose(point_to_segment_distance((0.5, 0.5), (0.0, 0.0), (1.0, 0.0)), 0.5)
    # Point clamps to start endpoint A
    assert math.isclose(point_to_segment_distance((-1.0, 0.0), (0.0, 0.0), (1.0, 0.0)), 1.0)
    # Point clamps to end endpoint B
    assert math.isclose(point_to_segment_distance((2.0, 0.0), (0.0, 0.0), (1.0, 0.0)), 1.0)


# ---------------------------------------------------------------------------
# 3. Self-Intersection Policy (Docs 31 §3)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("points,expected_self_intersect", [
    # Monotonic forward polyline along line -> False
    ([(0.0, 0.0), (1.0, 0.0), (2.0, 0.0)], False),
    # 180-degree reversal backtracking on same segment -> True
    ([(0.0, 0.0), (2.0, 0.0), (1.0, 0.0)], True),
    # Self-crossing X shape -> True
    ([(0.0, 0.0), (2.0, 2.0), (0.0, 2.0), (2.0, 0.0)], True),
    # Duplicate consecutive points -> filtered out, single line -> False
    ([(0.0, 0.0), (0.0, 0.0), (1.0, 0.0)], False),
    # Right-angle L shape -> False
    ([(0.0, 0.0), (1.0, 0.0), (1.0, 1.0)], False),
    # Z-shape with no crossing -> False
    ([(0.0, 0.0), (1.0, 0.0), (0.0, 1.0), (1.0, 1.0)], False),
])
def test_self_intersection_hand_cases(points, expected_self_intersect):
    assert self_intersects(points) is expected_self_intersect


# ---------------------------------------------------------------------------
# 4. Contact Disk Exemption Policy
# ---------------------------------------------------------------------------

def test_contact_disk_exemption_exact():
    """Verify that contact disk permits local endpoint touch but requires clearance outside."""
    poly1 = [(3.0, 0.0), (4.0, 0.0)]
    poly2 = [(4.0, 0.0), (5.0, 0.0)]
    contact_spec = {"location_mm": (4.0, 0.0), "radius_mm": 0.25}

    # Points outside disk of radius 0.25 around (4, 0):
    # poly1 outside: [(3, 0), (3.75, 0)]
    # poly2 outside: [(4.25, 0), (5, 0)]
    # Distance between them is 4.25 - 3.75 = 0.50 mm.
    clearance = polyline_clearance(poly1, poly2, contact_spec=contact_spec)
    assert clearance is not None
    assert math.isclose(clearance, 0.50, abs_tol=1e-9)


def test_contact_disk_does_not_exempt_backtracking_overlap():
    """If strokes share contact point but overlap outside the disk, clearance is 0.0."""
    poly1 = [(3.0, 0.0), (4.0, 0.0)]
    poly2 = [(4.0, 0.0), (3.0, 0.0)]  # overlaps backwards on poly1
    contact_spec = {"location_mm": (4.0, 0.0), "radius_mm": 0.25}

    clearance = polyline_clearance(poly1, poly2, contact_spec=contact_spec)
    assert clearance is not None
    assert math.isclose(clearance, 0.0, abs_tol=1e-9)
    assert clearance < C_MIN_MM  # Infeasible!


def test_zero_radius_contact_cannot_exempt_touching_segments():
    """A contact specification with radius 0.0 exempts no area; clearance remains 0.0."""
    poly1 = [(3.0, 0.0), (4.0, 0.0)]
    poly2 = [(4.0, 0.0), (5.0, 0.0)]
    contact_spec = {"location_mm": (4.0, 0.0), "radius_mm": 0.0}

    clearance = polyline_clearance(poly1, poly2, contact_spec=contact_spec)
    assert clearance is not None
    assert math.isclose(clearance, 0.0, abs_tol=1e-9)


def test_clip_segment_outside_disk():
    """Test disk clipping directly."""
    # Segment entirely inside disk: [-0.1, 0.1] inside radius 0.5
    clipped = clip_segment_outside_disk((-0.1, 0.0), (0.1, 0.0), (0.0, 0.0), 0.5)
    assert clipped == []

    # Segment passing through disk from (-1, 0) to (1, 0) with radius 0.5
    clipped = clip_segment_outside_disk((-1.0, 0.0), (1.0, 0.0), (0.0, 0.0), 0.5)
    assert len(clipped) == 2
    # Left piece: (-1, 0) to (-0.5, 0)
    assert math.isclose(clipped[0][0][0], -1.0) and math.isclose(clipped[0][1][0], -0.5)
    # Right piece: (0.5, 0) to (1.0, 0)
    assert math.isclose(clipped[1][0][0], 0.5) and math.isclose(clipped[1][1][0], 1.0)


# ---------------------------------------------------------------------------
# 5. Arithmetic Overflow Guard
# ---------------------------------------------------------------------------

def test_overflow_protection_raises_value_error():
    """Extreme coordinates that would produce floating-point overflow raise ValueError."""
    with pytest.raises(ValueError, match="Arithmetic overflow"):
        segment_distance((-1e308, 0.0), (1e308, 0.0), (0.0, -1e308), (0.0, 1e308))
