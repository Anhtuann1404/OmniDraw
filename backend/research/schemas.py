"""Strict, versioned transport types for Docs 31/32 (not a geometric oracle)."""

import hashlib
import json
import unicodedata
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationInfo, model_validator

VERSION = "joint-artifact-v1-draft"
METHODS = ("joint_dp", "independent_oracle", "staged_top_m", "beam")
Name = Annotated[str, Field(strict=True, min_length=1, max_length=200)]
LocalID = Annotated[str, Field(strict=True, min_length=1, max_length=200, pattern=r"^[^/\\]+$")]
Hash = Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{64}$")]
Number = Annotated[float, Field(strict=True, allow_inf_nan=False)]
Nonnegative = Annotated[float, Field(strict=True, allow_inf_nan=False, ge=0)]
Positive = Annotated[float, Field(strict=True, allow_inf_nan=False, gt=0)]
Index = Annotated[int, Field(strict=True, ge=0)]
Count = Annotated[int, Field(strict=True, gt=0)]
Point = tuple[Number, Number]
Method = Literal["joint_dp", "independent_oracle", "staged_top_m", "beam"]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", validate_default=True, allow_inf_nan=False)


class Stroke(StrictModel):
    stroke_id: LocalID
    role: Literal["body", "mark"]
    owner_index: Index
    reversible: Annotated[bool, Field(strict=True)]
    polyline_mm: Annotated[list[Point], Field(min_length=2, max_length=10000)]
    mark_type: Name | None = None


class Variant(StrictModel):
    candidate_id: LocalID
    source_hash: Hash
    strokes: Annotated[list[Stroke], Field(min_length=1, max_length=1000)]
    body_order: list[Name]
    mark_precedence: list[tuple[Name, Name]] = Field(default_factory=list)

    @model_validator(mode="after")
    def validate_order(self):
        ids = [s.stroke_id for s in self.strokes]
        if len(set(ids)) != len(ids):
            raise ValueError("Duplicate stroke IDs")
        bodies = {s.stroke_id for s in self.strokes if s.role == "body"}
        marks = {s.stroke_id for s in self.strokes if s.role == "mark"}
        if not bodies or len(self.body_order) != len(bodies) or set(self.body_order) != bodies:
            raise ValueError("body_order must contain every body stroke exactly once")
        successors = {key: set() for key in marks}
        for a, b in self.mark_precedence:
            if a not in marks or b not in marks or a == b or b in successors[a]:
                raise ValueError("Invalid or duplicate mark precedence")
            successors[a].add(b)
        indegrees = {key: 0 for key in marks}
        for values in successors.values():
            for key in values:
                indegrees[key] += 1
        ready = [key for key, degree in indegrees.items() if degree == 0]
        seen = 0
        while ready:
            key = ready.pop()
            seen += 1
            for other in successors[key]:
                indegrees[other] -= 1
                if indegrees[other] == 0:
                    ready.append(other)
        if seen != len(marks):
            raise ValueError("Cyclic mark precedence")
        return self


class Character(StrictModel):
    owner_index: Index
    grapheme: Annotated[str, Field(strict=True, min_length=1, max_length=16)]
    variants: Annotated[list[Variant], Field(min_length=1, max_length=256)]

    @model_validator(mode="after")
    def validate_owner(self):
        if len({v.candidate_id for v in self.variants}) != len(self.variants):
            raise ValueError("Duplicate candidate IDs")
        if any(s.owner_index != self.owner_index for v in self.variants for s in v.strokes):
            raise ValueError("Stroke owner does not match character")
        if unicodedata.normalize("NFD", self.grapheme) != self.grapheme:
            raise ValueError("grapheme must be NFD")
        if unicodedata.combining(self.grapheme[0]) or any(
            not unicodedata.combining(c) for c in self.grapheme[1:]
        ):
            raise ValueError("grapheme must be one base followed by combining marks")
        return self


class StrokeRef(StrictModel):
    owner_index: Index
    candidate_id: LocalID
    stroke_id: LocalID

    def key(self):
        return self.owner_index, self.candidate_id, self.stroke_id


class SeparationPair(StrictModel):
    first: StrokeRef
    second: StrokeRef


class Contact(SeparationPair):
    location_mm: Point
    radius_mm: Nonnegative
    policy_id: Name


class GeometryPolicy(StrictModel):
    c_min_mm: Number
    flatten_policy_id: Name
    contact_policy_id: Name
    numeric_policy_id: Name
    separation_policy_id: Name
    allow_zero_length: Annotated[bool, Field(strict=True)] = False

    @model_validator(mode="after")
    def fixed_floor(self):
        if self.c_min_mm != 0.20:
            raise ValueError("This contract fixes c_min_mm at 0.20")
        return self


class Boundary(StrictModel):
    p0_mm: Point
    p_end_mm: Point
    initial_pen: Literal["UP"]
    final_pen: Literal["UP"]
    convention_id: Name


class ReferenceGeometry(StrictModel):
    source_hash: Hash
    mapping_policy_id: Name


def canonical_hash(value) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


class ResearchCase(StrictModel):
    schema_version: Literal["joint-artifact-v1-draft"]
    case_id: Name
    dataset_version: Name
    manifest_sha256: Hash
    split: Literal["dev", "holdout", "supplemental", "synthetic"]
    original_text: Annotated[str, Field(strict=True, max_length=10000)] | None = None
    normalized_text: Annotated[str, Field(strict=True, max_length=10000)]
    normalization: Literal["NFD"]
    candidates: Annotated[list[Character], Field(max_length=256)]
    contacts: list[Contact] = Field(default_factory=list)
    separation_pairs: list[SeparationPair] = Field(default_factory=list)
    delay_policy: dict[Name, Index]
    geometry_policy: GeometryPolicy
    boundary: Boundary
    reference_geometry: ReferenceGeometry | None = None
    candidate_set_sha256: Hash

    def geometry_hash(self):
        # Versioned serialization: geometry, contact and boundary policy are part of scope.
        data = self.model_dump(mode="json")
        return canonical_hash({key: data[key] for key in (
            "schema_version", "normalization", "normalized_text", "candidates", "contacts",
            "separation_pairs", "delay_policy", "geometry_policy", "boundary", "reference_geometry"
        )})

    @model_validator(mode="after")
    def semantic_structure(self, info: ValidationInfo):
        if [c.owner_index for c in self.candidates] != list(range(len(self.candidates))):
            raise ValueError("Character owners must be contiguous from zero")
        if "".join(c.grapheme for c in self.candidates) != self.normalized_text:
            raise ValueError("Text does not match grapheme mapping")
        if self.original_text is not None and unicodedata.normalize("NFD", self.original_text) != self.normalized_text:
            raise ValueError("Original text does not normalize to normalized_text")
        refs = { (c.owner_index, v.candidate_id, s.stroke_id): s
            for c in self.candidates for v in c.variants for s in v.strokes }
        for key, stroke in refs.items():
            if not self.geometry_policy.allow_zero_length and all(p == stroke.polyline_mm[0] for p in stroke.polyline_mm):
                raise ValueError("Zero-length stroke requires declared policy")
            if stroke.role == "mark":
                qualified_id = "/".join(map(str, key))
                if qualified_id not in self.delay_policy and stroke.mark_type not in self.delay_policy:
                    raise ValueError("Every mark requires a delay value by qualified ID or type")
        for pairs in (self.contacts, self.separation_pairs):
            seen = set()
            for pair in pairs:
                a, b = pair.first.key(), pair.second.key()
                if a not in refs or b not in refs or a == b:
                    raise ValueError("Invalid stroke pair reference")
                if a[0] == b[0] and a[1] != b[1]:
                    raise ValueError("Pair references mutually exclusive variants")
                key = tuple(sorted((a,b)))
                if key in seen:
                    raise ValueError("Duplicate stroke pair")
                seen.add(key)
        if (info.context or {}).get("prepare_geometry_hash"):
            self.candidate_set_sha256 = self.geometry_hash()
        elif self.candidate_set_sha256 != self.geometry_hash():
            raise ValueError("Candidate geometry hash mismatch")
        return self

    @classmethod
    def prepare(cls, payload: dict):
        """Offline authoring helper only; HTTP never recomputes a mismatching hash."""
        data = dict(payload, candidate_set_sha256="0" * 64)
        return cls.model_validate(data, context={"prepare_geometry_hash": True})


class Theta(StrictModel):
    rho: Positive
    lambda_mm: Nonnegative


class Budget(StrictModel):
    wall_time_ms: Count
    max_states: Count
    max_configurations: Count
    memory_limit_mb: Count


class StagedOptions(StrictModel):
    ranker: Literal["H_ref", "H_geom"]
    m: Count
    rank_at_theta0_ref: Name


class BeamOptions(StrictModel):
    width: Count


class SolveRequest(StrictModel):
    schema_version: Literal["joint-artifact-v1-draft"]
    run_id: Name
    case_ref: Name
    method: Method
    theta: Theta
    baseline: StagedOptions | BeamOptions | None = None
    budget: Budget
    seed: Annotated[int, Field(strict=True)]
    freeze_manifest_ref: Hash | None = None

    @model_validator(mode="after")
    def options_match_method(self):
        required = {"staged_top_m": StagedOptions, "beam": BeamOptions}.get(self.method)
        if (required and not isinstance(self.baseline, required)) or (not required and self.baseline is not None):
            raise ValueError("Options do not match method")
        return self


class ScheduleAction(StrictModel):
    stroke: StrokeRef
    orientation: Literal["forward", "reverse"]
    transition: Literal["CONNECT", "LIFT"]


class Schedule(StrictModel):
    candidate_ids: list[Name]
    actions: list[ScheduleAction]
    boundary_convention_id: Name


class Metrics(StrictModel):
    L_down_mm: Nonnegative | None = None
    L_up_mm: Nonnegative | None = None
    N_cycle: Index | None = None
    J_mm: Nonnegative | None = None
    T_hat_sec: Nonnegative | None = None
    total_wall_time_ms: Nonnegative
    peak_states: Index | None = None
    peak_memory_mb: Nonnegative | None = None
    w: Index | None = None
    f: Index | None = None
    b: Index | None = None
    independent_violations: Index | None = None


class Bounds(StrictModel):
    lower_bound_J_mm: Nonnegative | None = None
    upper_bound_J_mm: Nonnegative | None = None
    evidence_id: Name | None = None


class Validation(StrictModel):
    status: Literal["NOT_RUN", "PASS", "FAIL"]
    checker_id: Name | None = None
    checker_version: Name | None = None
    findings: list[Name] = Field(default_factory=list)

    @model_validator(mode="after")
    def identified_checker(self):
        if self.status != "NOT_RUN" and (not self.checker_id or not self.checker_version):
            raise ValueError("Validation requires checker identity")
        return self


class Provenance(StrictModel):
    git_commit: Annotated[str, Field(strict=True, pattern=r"^[0-9a-f]{40}$")]
    dirty_patch_sha256: Hash | None
    manifest_sha256: Hash
    input_sha256: Hash
    config_sha256: Hash
    seed: Annotated[int, Field(strict=True)]
    runtime_versions: dict[Name, Name]
    timing_source: Literal["measured", "dev", "assumed"]


class ResearchError(StrictModel):
    code: Name
    message: Name


class SolveResult(StrictModel):
    run_id: Name
    case_id: Name
    method: Method
    candidate_set_sha256: Hash
    contract_version: Literal["joint-artifact-v1-draft"]
    outcome: Literal["OPTIMAL", "FEASIBLE", "INFEASIBLE", "NO_FEASIBLE_IN_PREFIX", "TIMEOUT", "RESOURCE_LIMIT", "INVALID_INPUT", "INTERNAL_ERROR"]
    scope: Literal["full_candidate_set", "declared_prefix", "explored_subset"]
    enumeration_complete: Annotated[bool, Field(strict=True)]
    ranking_complete: Annotated[bool, Field(strict=True)]
    search_complete: Annotated[bool, Field(strict=True)]
    schedule: Schedule | None
    metrics: Metrics
    bounds: Bounds
    provenance: Provenance
    validation: Validation
    error: ResearchError | None

    @model_validator(mode="after")
    def truthful_claims(self):
        if self.outcome in {"OPTIMAL", "FEASIBLE"} and (self.schedule is None or self.metrics.J_mm is None):
            raise ValueError("Feasible outcome requires schedule and objective")
        if self.outcome in {"OPTIMAL", "INFEASIBLE", "NO_FEASIBLE_IN_PREFIX"} and not self.search_complete:
            raise ValueError("Exact claim requires complete search")
        if self.outcome in {"INFEASIBLE", "NO_FEASIBLE_IN_PREFIX"} and self.schedule is not None:
            raise ValueError("Infeasible outcome cannot contain incumbent")
        if self.scope == "declared_prefix" and self.outcome == "INFEASIBLE":
            raise ValueError("Prefix must use NO_FEASIBLE_IN_PREFIX")
        if self.outcome == "NO_FEASIBLE_IN_PREFIX" and self.scope != "declared_prefix":
            raise ValueError("Prefix outcome requires declared prefix scope")
        if self.outcome in {"OPTIMAL", "FEASIBLE"} and self.error is not None:
            raise ValueError("Successful outcome cannot contain an error")
        if self.scope == "explored_subset" and self.outcome in {"OPTIMAL", "INFEASIBLE"}:
            raise ValueError("Explored subset cannot claim global exactness")
        if self.validation.status == "PASS" and self.metrics.independent_violations != 0:
            raise ValueError("Passed validation requires zero independently detected violations")
        lo, hi = self.bounds.lower_bound_J_mm, self.bounds.upper_bound_J_mm
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("Bounds are reversed")
        return self


class Domain(StrictModel):
    rho_min: Positive
    rho_max: Positive
    lambda_min_mm: Nonnegative
    lambda_max_mm: Nonnegative

    @model_validator(mode="after")
    def ordered(self):
        if self.rho_min > self.rho_max or self.lambda_min_mm > self.lambda_max_mm:
            raise ValueError("Invalid rectangular domain")
        return self


class CertificateRequest(StrictModel):
    schema_version: Literal["joint-artifact-v1-draft"]
    run_id: Name
    case_ref: Name
    candidate_set_sha256: Hash
    schedule: Schedule
    domain: Domain
    budget: Budget
    seed: Annotated[int, Field(strict=True)]
    freeze_manifest_ref: Hash | None = None


class VertexEvidence(StrictModel):
    theta: Theta
    J_pi_mm: Nonnegative
    lower_bound_J_mm: Nonnegative | None
    optimum_J_mm: Nonnegative | None
    exact: Annotated[bool, Field(strict=True)]
    evidence_id: Name


class CertificateResult(StrictModel):
    run_id: Name
    case_id: Name
    candidate_set_sha256: Hash
    schedule_sha256: Hash
    contract_version: Literal["joint-artifact-v1-draft"]
    scope: Literal["full_candidate_set"]
    validation: Validation
    vertices: Annotated[list[VertexEvidence], Field(min_length=4, max_length=4)]
    certificate_status: Literal["EXACT_MODELED", "CONSERVATIVE_BOUND", "NOT_CERTIFIED"]
    max_regret_upper_mm: Nonnegative | None
    numerical_tolerance_mm: Nonnegative
    provenance: Provenance


def check_schedule_structure(case: ResearchCase, schedule: Schedule):
    """Check IDs/directions/counts only; geometry and cost require the owner checker."""
    if len(schedule.candidate_ids) != len(case.candidates):
        raise ValueError("Schedule must select one candidate per character")
    strokes = {}
    for character, candidate_id in zip(case.candidates, schedule.candidate_ids):
        variant = next((v for v in character.variants if v.candidate_id == candidate_id), None)
        if variant is None:
            raise ValueError("Unknown selected candidate")
        for stroke in variant.strokes:
            strokes[(character.owner_index, candidate_id, stroke.stroke_id)] = stroke
    seen = set()
    for action in schedule.actions:
        key = action.stroke.key()
        if key not in strokes or key in seen:
            raise ValueError("Schedule stroke missing, duplicated or from another candidate")
        if action.orientation == "reverse" and not strokes[key].reversible:
            raise ValueError("Schedule reverses a non-reversible stroke")
        seen.add(key)
    if seen != set(strokes) or schedule.boundary_convention_id != case.boundary.convention_id:
        raise ValueError("Schedule coverage or boundary mismatch")
    if schedule.actions and schedule.actions[0].transition != "LIFT":
        raise ValueError("Initial pen is UP; first action must lower the pen")
