"""PR3 composition states and placement candidates (glyph-local geometry).

This module does not change the B3/default solver. Placement offsets are in
world millimetres and are applied only by the later world transform slice.
"""

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Literal, Mapping, Optional, Tuple
import math
import numpy as np

from .engine import GlyphVariant, build_ligature_bridge, bridge_collision_cost, generate_accents
from .metrics_evaluator import compute_diacritic_clearance

CONTRACT_VERSION = "e4-v1"
PROPOSED_METHOD_TAG = "pr3_composition"


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


def _readonly_vector(value):
    vector = np.array(value, dtype=float, copy=True)
    if vector.shape != (2,) or not np.isfinite(vector).all():
        raise ValueError("invalid glyph vector")
    vector.setflags(write=False)
    return vector


def _freeze_context(value):
    if isinstance(value, Mapping):
        return MappingProxyType({key: _freeze_context(item) for key, item in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_freeze_context(item) for item in value)
    if isinstance(value, np.ndarray):
        array = np.array(value, copy=True)
        array.setflags(write=False)
        return array
    return value


@dataclass(frozen=True)
class _GlyphVariantSnapshot:
    """Read-only PR3 view of a mutable B3 GlyphVariant."""
    strokes: Tuple[np.ndarray, ...]
    entry_pt: np.ndarray
    exit_pt: np.ndarray
    v_entry: np.ndarray
    v_exit: np.ndarray
    can_in: bool
    can_out: bool
    cost_legibility: float
    tag: str

    @classmethod
    def from_variant(cls, variant):
        return cls(
            _strokes_copy(variant.strokes),
            _readonly_vector(variant.entry_pt), _readonly_vector(variant.exit_pt),
            _readonly_vector(variant.v_entry), _readonly_vector(variant.v_exit),
            bool(variant.can_in), bool(variant.can_out),
            float(variant.cost_legibility), str(variant.tag),
        )


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
        object.__setattr__(self, "base_variant", _GlyphVariantSnapshot.from_variant(self.base_variant))
        object.__setattr__(self, "accents", tuple(self.accents))
        object.__setattr__(self, "context", _freeze_context(self.context))
        object.__setattr__(self, "metadata", _freeze_context(self.metadata))


def generate_diacritic_candidates(base_char, accents, anchor_x, config=None,
                                  dot_below_x_offset=None):
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
    strokes = generate_accents(base_char, marks, anchor_x,
                               dot_below_x_offset=dot_below_x_offset)
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
                             context=None, dot_below_x_offset=None):
    """Combine existing glyph variants with valid placements, at most 9 states."""
    marks = tuple(accents)
    variants = tuple(base_variants)
    if len(variants) > 3:
        raise ValueError("P0 supports at most three base variants")
    candidates = (generate_diacritic_candidates(base_char, marks, anchor_x, config,
                                                dot_below_x_offset)
                  if marks else (None,))
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


class TransitionEvaluationError(ValueError):
    """The transition calculation encountered malformed or non-finite data."""


class NoValidPathError(ValueError):
    """No complete path remains through the PR3 trellis."""


@dataclass(frozen=True)
class TransitionWeights:
    w_penup: float = 0.5
    w_lift: float = 4.0
    w_curvature: float = 2.0
    w_bridge_collision: float = 15.0

    def __post_init__(self):
        if not all(math.isfinite(v) and v >= 0 for v in
                   (self.w_penup, self.w_lift, self.w_curvature, self.w_bridge_collision)):
            raise ValueError("transition weights must be finite and nonnegative")


@dataclass(frozen=True)
class TransitionCostBreakdown:
    d_penup_mm: float
    n_lift: int
    c_curvature: float
    c_bridge_collision: float
    total_cost: float

    def __post_init__(self):
        if self.n_lift not in (0, 1) or not all(math.isfinite(v) and v >= 0 for v in
                (self.d_penup_mm, self.c_curvature, self.c_bridge_collision, self.total_cost)):
            raise ValueError("transition breakdown must be finite and nonnegative")


@dataclass(frozen=True)
class TransitionResult:
    contract_version: str
    is_valid: bool
    decision: Literal["CONNECT", "LIFT", "REJECT"]
    total_cost: float
    breakdown: Optional[TransitionCostBreakdown]
    reject_reason: Optional[str] = None
    bridge_strokes: Optional[Tuple[np.ndarray, ...]] = None

    def __post_init__(self):
        if self.contract_version != CONTRACT_VERSION:
            raise ValueError("wrong transition contract version")
        if self.decision == "REJECT":
            if (self.is_valid or self.total_cost != float("inf") or self.breakdown is not None or
                    self.bridge_strokes is not None or not self.reject_reason):
                raise ValueError("invalid rejected transition")
        elif self.decision in ("CONNECT", "LIFT"):
            if (not self.is_valid or not math.isfinite(self.total_cost) or self.total_cost < 0 or
                    self.breakdown is None or self.breakdown.total_cost != self.total_cost or
                    self.reject_reason is not None):
                raise ValueError("invalid accepted transition")
            if self.decision == "CONNECT":
                if not self.bridge_strokes or self.breakdown.n_lift != 0:
                    raise ValueError("connect requires a bridge and no lift")
                object.__setattr__(self, "bridge_strokes", _strokes_copy(self.bridge_strokes))
            elif self.bridge_strokes is not None or self.breakdown.n_lift != 1:
                raise ValueError("lift must not carry a bridge")
        else:
            raise ValueError("unknown transition decision")


def _reject(reason):
    return TransitionResult(CONTRACT_VERSION, False, "REJECT", float("inf"), None, reason)


def evaluate_composition_transition(prev_state, curr_state, prev_world, curr_world,
                                    transition_weights, diacritic_config):
    """Evaluate the E4 transition without changing the frozen B3 solver."""
    weights = transition_weights
    config = diacritic_config
    try:
        for world in (prev_world, curr_world):
            for vector in (world.entry_pt, world.exit_pt, world.v_entry, world.v_exit):
                if np.asarray(vector).shape != (2,) or not np.isfinite(vector).all():
                    raise TransitionEvaluationError("invalid world vector")
            if np.linalg.norm(world.v_entry) <= 0 or np.linalg.norm(world.v_exit) <= 0:
                raise TransitionEvaluationError("zero world tangent")
        if (evaluate_composition_state(prev_state, prev_world, config).c_internal_collision >
                config.max_internal_collision_cost or
                evaluate_composition_state(curr_state, curr_world, config).c_internal_collision >
                config.max_internal_collision_cost):
            return _reject("HARD_INTERNAL_COLLISION")
        delta = curr_world.entry_pt - prev_world.exit_pt
        distance = float(np.linalg.norm(delta))
        if not math.isfinite(distance):
            raise TransitionEvaluationError("non-finite pen-up distance")
        lift_cost = weights.w_penup * distance + weights.w_lift
        if not math.isfinite(lift_cost):
            raise TransitionEvaluationError("non-finite lift cost")
        lift = TransitionResult(CONTRACT_VERSION, True, "LIFT", lift_cost,
                                TransitionCostBreakdown(distance, 1, 0.0, 0.0, lift_cost))
        if not (prev_state.base_variant.can_out and curr_state.base_variant.can_in):
            return lift
        # Preserve B3's geometric eligibility rule while keeping its cost path separate.
        if delta[0] <= -0.2 or distance >= 12.0:
            return lift
        direction = delta / distance if distance > 1e-4 else None
        curvature = 0.0 if direction is None else (
            1.0 - float(np.clip(np.dot(prev_world.v_exit, direction), -1., 1.)) +
            1.0 - float(np.clip(np.dot(direction, curr_world.v_entry), -1., 1.)))
        bridge = build_ligature_bridge(prev_world.exit_pt, prev_world.v_exit,
                                      curr_world.entry_pt, curr_world.v_entry, n=6)
        if not np.isfinite(bridge).all():
            raise TransitionEvaluationError("non-finite bridge")
        # A bridge may meet the two base glyphs at its endpoints. The existing
        # heuristic handles those anchor contacts; marks have no such exemption.
        mark_clearance = compute_diacritic_clearance(
            (bridge,), prev_world.diacritic_strokes + curr_world.diacritic_strokes)
        if mark_clearance < config.clearance_threshold_mm:
            return lift
        collision = bridge_collision_cost(bridge, prev_world.base_strokes,
                                          curr_world.base_strokes, scale_hint=1.0)
        if not math.isfinite(collision) or collision < 0:
            raise TransitionEvaluationError("non-finite bridge collision cost")
        connect_cost = weights.w_curvature * curvature + weights.w_bridge_collision * collision
        if not math.isfinite(connect_cost):
            raise TransitionEvaluationError("non-finite connect cost")
        if connect_cost >= lift_cost:
            return lift
        return TransitionResult(CONTRACT_VERSION, True, "CONNECT", connect_cost,
                                TransitionCostBreakdown(0.0, 0, curvature, collision, connect_cost),
                                bridge_strokes=(bridge,))
    except (ValueError, TypeError, OverflowError, FloatingPointError) as exc:
        if isinstance(exc, TransitionEvaluationError):
            raise
        raise TransitionEvaluationError(str(exc)) from exc


def optimize_composition_dag(layers, transition_weights=None, diacritic_config=None):
    """Viterbi over (state, world) layers with state cost counted once per node."""
    if not layers:
        return {"states": (), "transitions": (), "total_cost": 0.0}
    weights = transition_weights or TransitionWeights()
    config = diacritic_config or DiacriticConfig()
    if any(not layer or len(layer) > 9 for layer in layers):
        raise NoValidPathError("empty or oversized composition layer")
    initial = [evaluate_composition_state(state, world, config) for state, world in layers[0]]
    costs = [cost.total_cost if cost.c_internal_collision <= config.max_internal_collision_cost
             else float("inf") for cost in initial]
    back = []
    for prev_layer, layer in zip(layers, layers[1:]):
        next_costs = []
        layer_back = []
        for state, world in layer:
            state_cost = evaluate_composition_state(state, world, config)
            if state_cost.c_internal_collision > config.max_internal_collision_cost:
                next_costs.append(float("inf"))
                layer_back.append(None)
                continue
            own_cost = state_cost.total_cost
            options = []
            for index, (prev_state, prev_world) in enumerate(prev_layer):
                if not math.isfinite(costs[index]):
                    continue
                result = evaluate_composition_transition(prev_state, state, prev_world, world,
                                                         weights, config)
                if result.is_valid:
                    options.append((costs[index] + result.total_cost + own_cost, index, result))
            if options:
                score, index, result = min(options, key=lambda item: (item[0], item[1]))
                next_costs.append(score)
                layer_back.append((index, result))
            else:
                next_costs.append(float("inf"))
                layer_back.append(None)
        costs = next_costs
        back.append(layer_back)
    if not any(math.isfinite(cost) for cost in costs):
        raise NoValidPathError("no valid path through composition layers")
    index = min(range(len(costs)), key=lambda i: (costs[i], i))
    total = costs[index]
    chosen = [layers[-1][index][0]]
    transitions = []
    for layer_index in range(len(back) - 1, -1, -1):
        index, result = back[layer_index][index]
        transitions.append(result)
        chosen.append(layers[layer_index][index][0])
    return {"states": tuple(reversed(chosen)), "transitions": tuple(reversed(transitions)),
            "total_cost": total}
