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

CONTRACT_VERSION = "e4-v1"


class NoValidCompositionState(ValueError):
    """Every candidate for a character violated a hard constraint."""


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
