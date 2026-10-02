"""TV4 primitive tests with hand answers, not independent TV3 validation."""

from pathlib import Path
import pytest

from backend.research.geometry import (
    compile_geometry, polyline_clearance, segment_distance, self_intersects,
)
from backend.research.schemas import ResearchCase
from backend.research.service import load_manifest

FIXTURE = Path(__file__).parent / "fixtures" / "solver_dev_cases.json"


@pytest.mark.parametrize("gap", [.19, .20, .21])
def test_parallel_clearance_hand_boundary(gap):
    assert polyline_clearance([(0, 0), (1, 0)], [(0, gap), (1, gap)]) == gap


@pytest.mark.parametrize("segments,expected", [
    (((0, 0), (2, 2), (0, 2), (2, 0)), 0),
    (((0, 0), (2, 0), (1, 0), (3, 0)), 0),
    (((0, 0), (1, 0), (2, 0), (3, 0)), 1),
    (((0, 0), (0, 0), (3, 4), (3, 4)), 5),
    (((0, 0), (1, 0), (1, 0), (1, 1)), 0),
])
def test_segment_degenerate_collinear_crossing(segments, expected):
    assert segment_distance(*segments) == expected


@pytest.mark.parametrize("points,expected", [
    ([(0, 0), (1, 0), (2, 0)], False),
    ([(0, 0), (2, 0), (1, 0)], True),
    ([(0, 0), (2, 2), (0, 2), (2, 0)], True),
    ([(0, 0), (0, 0), (1, 0)], False),
    ([(0, 0), (1, 0), (1, 1)], False),
])
def test_self_intersection_policy(points, expected):
    assert self_intersects(points) is expected


def test_contact_disk_does_not_exempt_remaining_pair():
    case = load_manifest(FIXTURE)[0]
    contact = case.contacts[0]
    assert polyline_clearance([(3, 0), (4, 0)], [(4, 0), (5, 0)], contact) == .5
    # Contact location is allowed; overlap outside that region remains invalid.
    assert polyline_clearance([(3, 0), (4, 0)], [(4, 0), (3, 0)], contact) == 0


def test_zero_radius_contact_cannot_hide_neighbor_clearance():
    case = load_manifest(FIXTURE)[0]
    contact = case.contacts[0].model_copy(update={"radius_mm": 0})
    assert polyline_clearance([(3, 0), (4, 0)], [(4, 0), (5, 0)], contact) == 0


@pytest.mark.parametrize("gap,invalid", [(.19, True), (.20, False), (.21, False)])
def test_client_omitting_separation_pairs_does_not_bypass_floor(gap, invalid):
    case = load_manifest(FIXTURE)[0]
    data = case.model_dump(mode="json")
    data["candidates"][0]["variants"][0]["strokes"][1]["polyline_mm"] = [[0, gap], [1, gap]]
    assert data["separation_pairs"] == []
    index = compile_geometry(ResearchCase.prepare(data))
    assert ((0, "a-dev") in index.invalid_variants) is invalid


@pytest.mark.parametrize("field", ["numeric_policy_id", "separation_policy_id", "flatten_policy_id", "contact_policy_id"])
def test_unknown_policy_rejected(field):
    data = load_manifest(FIXTURE)[0].model_dump(mode="json")
    data["geometry_policy"][field] = "PENDING"
    with pytest.raises(ValueError, match="Unsupported"):
        compile_geometry(ResearchCase.prepare(data))


def test_geometry_overflow_is_explicit():
    with pytest.raises(ValueError, match="overflow"):
        segment_distance((-1e308, 0), (1e308, 0), (0, -1e308), (0, 1e308))
