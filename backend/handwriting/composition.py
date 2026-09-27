"""PR3 composition states and placement candidates (glyph-local geometry).

This module does not change the B3/default solver. Placement offsets are in
world millimetres and are applied only by the later world transform slice.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping, Optional, Tuple
import math
import numpy as np

from .engine import GlyphVariant, generate_accents
from .metrics_evaluator import compute_diacritic_clearance

CONTRACT_VERSION = "e4-v1"


class NoValidCompositionState(ValueError):
    """Every candidate for a character violated a hard constraint."""


class CompositionGeometryError(ValueError):
    """A local or world geometry value is malformed."""


def _strokes_copy(strokes):
    result = []
    for stroke in strokes:
        points = np.array(stroke, dtype=float, copy=True)
        if points.ndim != 2 or points.shape[1] != 2 or len(points) == 0 or not np.isfinite(points).all():
            raise ValueError("invalid diacritic stroke geometry")
        points.setflags(write=False)
        result.append(points)
    return tuple(result)


@dataclass(frozen=True)
class DiacriticConfig:
    internal_collision_tolerance_mm: float = 0.05
    clearance_threshold_mm: float = 0.20
    max_internal_collision_cost: float = 0.50
    dx_candidates_mm: Mapping[str, float] = field(default_factory=lambda: {
        "canonical": 0.0, "safe_left": -0.45, "safe_right": 0.45,
    })
    dy_candidates_mm: Mapping[str, float] = field(default_factory=lambda: {"canonical": 0.0})
    max_placement_shift_mm: float = 1.0

    def __post_init__(self):
        for value in (self.internal_collision_tolerance_mm, self.clearance_threshold_mm,
                      self.max_internal_collision_cost, self.max_placement_shift_mm):
            if not math.isfinite(value) or value < 0:
                raise ValueError("config scalars must be finite and nonnegative")
        dx = dict(self.dx_candidates_mm)
        dy = dict(self.dy_candidates_mm)
        if set(dx) != {"canonical", "safe_left", "safe_right"} or dx["canonical"] != 0:
            raise ValueError("expected canonical, safe_left, safe_right offsets")
        if not all(math.isfinite(v) for v in (*dx.values(), *dy.values())):
            raise ValueError("placement offsets must be finite")
        object.__setattr__(self, "dx_candidates_mm", MappingProxyType(dx))
        object.__setattr__(self, "dy_candidates_mm", MappingProxyType(dy))


@dataclass(frozen=True)
class DiacriticCandidate:
    marks: Tuple[str, ...]
    placement_tag: str
    strokes_local: Tuple[np.ndarray, ...]
    anchor_x: float
    anchor_y: float
    dx: float  # world mm; applied after scaling local strokes
    dy: float  # world mm; applied after scaling local strokes
    bounds_local: Tuple[float, float, float, float]
    clearance_zone_local: Tuple[np.ndarray, ...]
    placement_penalty: float

    def __post_init__(self):
        strokes = _strokes_copy(self.strokes_local)
        if not strokes:
            raise ValueError("diacritic candidate requires geometry")
        bounds = tuple(float(v) for v in self.bounds_local)
        if len(bounds) != 4 or not all(math.isfinite(v) for v in bounds):
            raise ValueError("invalid local bounds")
        if not all(math.isfinite(v) for v in (self.anchor_x, self.anchor_y, self.dx, self.dy,
                                               self.placement_penalty)) or self.placement_penalty < 0:
            raise ValueError("invalid placement scalars")
        object.__setattr__(self, "strokes_local", strokes)
        object.__setattr__(self, "clearance_zone_local", _strokes_copy(self.clearance_zone_local))
        object.__setattr__(self, "bounds_local", bounds)


@dataclass(frozen=True)
class CompositionState:
    base_variant: GlyphVariant
    diacritic_candidate: Optional[DiacriticCandidate]
    base_char: str
    accents: Tuple[str, ...]
    context: Mapping[str, Any]
    state_tag: str
    internal_collision_cost: float
    legibility_cost: float
    metadata: Mapping[str, Any]

    def __post_init__(self):
        if bool(self.accents) != (self.diacritic_candidate is not None):
            raise ValueError("accent marks and candidate must agree")
        if not all(math.isfinite(v) and v >= 0 for v in
                   (self.internal_collision_cost, self.legibility_cost)):
            raise ValueError("state costs must be finite and nonnegative")
        object.__setattr__(self, "accents", tuple(self.accents))
        object.__setattr__(self, "context", MappingProxyType(dict(self.context)))
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))


def generate_diacritic_candidates(base_char, accents, anchor_x, config=None):
    """Build P0 placement choices from the current canonical accent geometry.

    This slice records world-mm offsets without prematurely mixing them into
    glyph-local polylines. Hard geometry failures yield no candidates.
    """
    marks = tuple(accents)
    if not marks:
        return ()
    structural = {"\u0302", "\u0306", "\u031b"}
    tones = {"\u0301", "\u0300", "\u0309", "\u0303", "\u0323"}
    if (not set(marks) <= structural | tones or
            sum(mark in structural for mark in marks) > 1 or
            sum(mark in tones for mark in marks) > 1 or
            len(marks) != len(set(marks))):
        return ()
    config = config or DiacriticConfig()
    strokes = generate_accents(base_char, marks, anchor_x)
    try:
        immutable = _strokes_copy(strokes)
    except (TypeError, ValueError):
        return ()
    if not immutable:
        return ()
    points = np.vstack(immutable)
    bounds = (float(points[:, 0].min()), float(points[:, 1].min()),
              float(points[:, 0].max()), float(points[:, 1].max()))
    candidates = []
    for tag, dx in config.dx_candidates_mm.items():
        dy = config.dy_candidates_mm.get(tag, 0.0)
        shift = math.hypot(dx, dy)
        if shift > config.max_placement_shift_mm:
            continue
        candidates.append(DiacriticCandidate(
            marks, tag, immutable, float(anchor_x), 0.0, dx, dy, bounds, (),
            shift / config.max_placement_shift_mm if config.max_placement_shift_mm else 0.0,
        ))
    return tuple(candidates)


def build_composition_states(base_char, accents, base_variants, anchor_x, config=None,
                             context=None):
    """Combine existing glyph variants with valid placements, at most 9 states."""
    marks = tuple(accents)
    variants = tuple(base_variants)
    if len(variants) > 3:
        raise ValueError("P0 supports at most three base variants")
    candidates = generate_diacritic_candidates(base_char, marks, anchor_x, config) if marks else (None,)
    states = tuple(CompositionState(
        variant, candidate, base_char, marks, context or {},
        f"{variant.tag}_{candidate.placement_tag if candidate else 'none'}",
        0.0, float(variant.cost_legibility), {},
    ) for variant in variants for candidate in candidates)
    if not states:
        raise NoValidCompositionState(base_char)
    return states


@dataclass(frozen=True)
class GlyphWorldGeometry:
    """Evaluated geometry in paper millimetres for one composition state."""
    base_strokes: Tuple[np.ndarray, ...]
    diacritic_strokes: Tuple[np.ndarray, ...]
    entry_pt: np.ndarray
    exit_pt: np.ndarray
    v_entry: np.ndarray
    v_exit: np.ndarray
    diacritic_bbox: Optional[Tuple[float, float, float, float]]

    def __post_init__(self):
        object.__setattr__(self, "base_strokes", _strokes_copy(self.base_strokes))
        object.__setattr__(self, "diacritic_strokes", _strokes_copy(self.diacritic_strokes))
        for name in ("entry_pt", "exit_pt", "v_entry", "v_exit"):
            point = np.array(getattr(self, name), dtype=float, copy=True)
            if point.shape != (2,) or not np.isfinite(point).all():
                raise CompositionGeometryError(f"invalid {name}")
            point.setflags(write=False)
            object.__setattr__(self, name, point)


def _frame(scale_vec, offset):
    scale = np.asarray(scale_vec, dtype=float)
    origin = np.asarray(offset, dtype=float)
    if (scale.shape != (2,) or origin.shape != (2,) or
            not np.isfinite(scale).all() or not np.isfinite(origin).all() or
            np.any(scale <= 0)):
        raise CompositionGeometryError("invalid glyph-to-world frame")
    return scale, origin


def transform_state_to_world(state, scale_vec, offset):
    """Apply one anisotropic glyph frame; add placement offset once in world mm."""
    scale, origin = _frame(scale_vec, offset)

    def point(value):
        p = np.asarray(value, dtype=float)
        if p.shape != (2,) or not np.isfinite(p).all():
            raise CompositionGeometryError("invalid glyph point")
        return p * scale + origin

    def tangent(value):
        t = np.asarray(value, dtype=float)
        if t.shape != (2,) or not np.isfinite(t).all():
            raise CompositionGeometryError("invalid glyph tangent")
        t = t * scale
        norm = np.linalg.norm(t)
        if not math.isfinite(norm) or norm <= 0:
            raise CompositionGeometryError("zero or invalid world tangent")
        return t / norm

    def strokes_world(strokes, extra):
        result = []
        for stroke in strokes:
            local = np.asarray(stroke, dtype=float)
            if local.ndim != 2 or local.shape[1] != 2 or len(local) < 2 or not np.isfinite(local).all():
                raise CompositionGeometryError("invalid glyph stroke")
            world = local * scale + origin + extra
            if not np.isfinite(world).all():
                raise CompositionGeometryError("world stroke overflow")
            result.append(world)
        return tuple(result)

    base = state.base_variant
    world_base = strokes_world(base.strokes, np.zeros(2))
    candidate = state.diacritic_candidate
    world_marks = strokes_world(candidate.strokes_local, np.array([candidate.dx, candidate.dy])) if candidate else ()
    bbox = None
    if world_marks:
        points = np.vstack(world_marks)
        bbox = (float(points[:, 0].min()), float(points[:, 1].min()),
                float(points[:, 0].max()), float(points[:, 1].max()))
    return GlyphWorldGeometry(world_base, world_marks, point(base.entry_pt), point(base.exit_pt),
                              tangent(base.v_entry), tangent(base.v_exit), bbox)


@dataclass(frozen=True)
class StateCostBreakdown:
    """Internal geometry metric is separate from dimensionless state cost."""
    minimum_internal_clearance_mm: float
    c_internal_collision: float
    c_legibility: float
    c_placement: float
    total_cost: float


def evaluate_composition_state(state, world, config=None, w_legibility=1.0):
    """Compute C_state; never include any inter-character transition cost."""
    config = config or DiacriticConfig()
    if not math.isfinite(w_legibility) or w_legibility < 0:
        raise ValueError("legibility weight must be finite and nonnegative")
    clearance = compute_diacritic_clearance(world.base_strokes, world.diacritic_strokes)
    if len(world.diacritic_strokes) > 1:
        for i, stroke in enumerate(world.diacritic_strokes):
            other = world.diacritic_strokes[i + 1:]
            clearance = min(clearance, compute_diacritic_clearance((stroke,), other))
    if math.isnan(clearance) or clearance < 0:
        raise CompositionGeometryError("invalid internal clearance")
    # A geometric deficit becomes dimensionless only after division by a mm threshold.
    deficit = max(0.0, config.clearance_threshold_mm - clearance)
    collision_cost = deficit / config.clearance_threshold_mm if config.clearance_threshold_mm else 0.0
    legibility = w_legibility * state.legibility_cost
    placement = state.diacritic_candidate.placement_penalty if state.diacritic_candidate else 0.0
    total = collision_cost + legibility + placement
    if not math.isfinite(total):
        raise CompositionGeometryError("non-finite state cost")
    return StateCostBreakdown(clearance, collision_cost, legibility, placement, total)


def prune_composition_states(states, scale_vec, offset, config=None, page_bounds_mm=None):
    """Remove hard-invalid states; never restore a pruned canonical candidate."""
    config = config or DiacriticConfig()
    _frame(scale_vec, offset)
    if page_bounds_mm is not None:
        bounds = np.asarray(page_bounds_mm, dtype=float)
        if bounds.shape != (4,) or not np.isfinite(bounds).all() or bounds[0] > bounds[2] or bounds[1] > bounds[3]:
            raise ValueError("invalid page bounds")
    valid = []
    for state in states:
        try:
            world = transform_state_to_world(state, scale_vec, offset)
            cost = evaluate_composition_state(state, world, config)
        except (CompositionGeometryError, ValueError):
            continue
        if cost.c_internal_collision > config.max_internal_collision_cost:
            continue
        if page_bounds_mm is not None and world.diacritic_bbox is not None:
            x0, y0, x1, y1 = world.diacritic_bbox
            if x0 < bounds[0] or y0 < bounds[1] or x1 > bounds[2] or y1 > bounds[3]:
                continue
        valid.append(state)
    if not valid:
        raise NoValidCompositionState("no candidate satisfies world geometry constraints")
    return tuple(valid)
