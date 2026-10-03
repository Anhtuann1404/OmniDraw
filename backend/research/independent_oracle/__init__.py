"""Independent verification oracle and geometry primitives for Vietnamese handwriting.

Authored independently by TV3 following Docs 31 (joint solver contract) and Docs 32
(research API and artifact contract).
No imports from backend.research.geometry, backend.research.schedule_checker,
or backend.research.joint_dp.
"""

from .adapter import independent_validate_case, solve_oracle_adapter
from .enumerator import (
    ORACLE_COST_POLICY,
    ORACLE_TIE_POLICY,
    OracleRun,
    OracleSchedule,
    solve_oracle,
    validate_configuration_geometry,
)
from .primitives import (
    C_MIN_MM,
    clip_segment_outside_disk,
    point_distance,
    point_to_segment_distance,
    polyline_clearance,
    segment_distance,
    segments_intersect,
    self_intersects,
)

__all__ = [
    "C_MIN_MM",
    "ORACLE_COST_POLICY",
    "ORACLE_TIE_POLICY",
    "OracleRun",
    "OracleSchedule",
    "clip_segment_outside_disk",
    "independent_validate_case",
    "point_distance",
    "point_to_segment_distance",
    "polyline_clearance",
    "segment_distance",
    "segments_intersect",
    "self_intersects",
    "solve_oracle",
    "solve_oracle_adapter",
    "validate_configuration_geometry",
]
