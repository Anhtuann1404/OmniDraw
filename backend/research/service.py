"""Server-owned case registry and checked adapter handoff. No public case registration."""

import json
import logging
import math
import os
from pathlib import Path
from typing import Callable

from .schemas import (
    METHODS, VERSION, CertificateRequest, CertificateResult, ResearchCase,
    SolveRequest, SolveResult, canonical_hash, check_schedule_structure,
)

log = logging.getLogger(__name__)
MAX_MANIFEST_BYTES = 2 * 1024 * 1024


class ResearchFailure(Exception):
    def __init__(self, status: int, code: str, message: str):
        super().__init__(message)
        self.status, self.code, self.message = status, code, message


def manifest_hash(cases: list[ResearchCase]) -> str:
    data = [case.model_dump(mode="json", exclude={"manifest_sha256"}) for case in cases]
    return canonical_hash({"schema_version": VERSION, "cases": data})


class ResearchService:
    def __init__(self, cases=(), solvers=None, certifier=None):
        self._cases = {}
        for case in cases:
            # Revalidate even an instance constructed through model_construct.
            checked = ResearchCase.model_validate(case.model_dump(mode="json"))
            if checked.case_id in self._cases:
                raise ValueError("Ambiguous case_ref")
            self._cases[checked.case_id] = checked
        self._solvers: dict[str, Callable] = dict(solvers or {})
        if set(self._solvers) - set(METHODS):
            raise ValueError("Unknown registered method")
        if any(not callable(adapter) for adapter in self._solvers.values()):
            raise ValueError("Registered solver must be callable")
        if certifier is not None and not callable(certifier):
            raise ValueError("Registered certifier must be callable")
        self._certifier = certifier

    def capabilities(self):
        return {
            "schema_version": VERSION,
            "api_status": "ADAPTER_GATEWAY",
            "methods": {method: method in self._solvers for method in METHODS},
            "certify_ready": self._certifier is not None,
            "public_holdout_enabled": False,
            "validation_level": "STRUCTURAL_ONLY",
            "request_limit_bytes": 1024 * 1024,
            "budget_limits": {"wall_time_ms": 30000, "max_states": 200000,
                              "max_configurations": 100000, "memory_limit_mb": 512},
        }

    def _case(self, case_ref):
        case = self._cases.get(case_ref)
        if case is None or case.split == "holdout":
            # Do not disclose existence of sealed Holdout items through lookup responses.
            raise ResearchFailure(404, "RESEARCH_CASE_NOT_AVAILABLE", "Case is not available to this API")
        return case.model_copy(deep=True)

    def _budget(self, request):
        if request.freeze_manifest_ref is not None:
            raise ResearchFailure(403, "RESEARCH_OFFICIAL_RUN_DISABLED", "Official frozen runs require the offline custody workflow")
        limits = self.capabilities()["budget_limits"]
        if any(value > limits[key] for key, value in request.budget.model_dump().items()):
            raise ResearchFailure(422, "RESEARCH_BUDGET_LIMIT", "Requested budget exceeds API limits")

    @staticmethod
    def validate_case(case):
        if case.split == "holdout":
            raise ResearchFailure(403, "RESEARCH_HOLDOUT_DISABLED", "Holdout data cannot be submitted through the public API")
        return {"schema_version": VERSION, "case_id": case.case_id,
                "candidate_set_sha256": case.candidate_set_sha256,
                "status": "STRUCTURALLY_VALID", "geometric_validation": "NOT_RUN"}

    def solve(self, request: SolveRequest) -> SolveResult:
        self._budget(request)
        case = self._case(request.case_ref)
        solver = self._solvers.get(request.method)
        if solver is None:
            raise ResearchFailure(503, "RESEARCH_METHOD_NOT_READY", "Requested method has no registered implementation")
        # Adapters enforce wall-time/state/memory budgets internally; returning TIMEOUT/RESOURCE_LIMIT.
        try:
            result = solver(case.model_copy(deep=True), request.model_copy(deep=True))
            if isinstance(result, SolveResult):
                result = result.model_dump(mode="json")
            result = SolveResult.model_validate(result)
            self._check_identity(result, case, request)
            if result.method != request.method:
                raise ValueError("Adapter changed method")
            if result.schedule is not None:
                check_schedule_structure(case, result.schedule)
                metrics = result.metrics
                if any(value is None for value in (metrics.L_down_mm, metrics.L_up_mm, metrics.N_cycle, metrics.J_mm)):
                    raise ValueError("Incumbent lacks motion coefficients")
                expected_j = metrics.L_down_mm + request.theta.rho * metrics.L_up_mm + request.theta.lambda_mm * metrics.N_cycle
                if not math.isfinite(expected_j) or abs(expected_j - metrics.J_mm) > 1e-9 * max(1.0, expected_j):
                    raise ValueError("Objective is inconsistent with theta and coefficients")
            if request.method == "joint_dp" and result.scope != "full_candidate_set":
                raise ValueError("Joint solver must declare full scope")
            if request.method == "staged_top_m":
                if result.scope == "full_candidate_set":
                    raise ValueError("Staged result must retain prefix/subset scope")
                if result.outcome == "INFEASIBLE":
                    raise ValueError("Prefix must use NO_FEASIBLE_IN_PREFIX")
                if result.outcome in {"OPTIMAL", "NO_FEASIBLE_IN_PREFIX"} and not (
                    result.enumeration_complete and result.ranking_complete
                ):
                    raise ValueError("Prefix exactness requires complete ranking")
            if request.method == "beam" and result.outcome in {"OPTIMAL", "INFEASIBLE"}:
                raise ValueError("Uncertified beam cannot assert exactness")
            if result.validation.status == "FAIL" and result.outcome in {"OPTIMAL", "FEASIBLE"}:
                raise ValueError("Failed validation cannot be published as valid output")
            return result
        except Exception:
            log.exception("Research solve adapter failed its output contract")
            raise ResearchFailure(500, "RESEARCH_ADAPTER_ERROR", "Solver failed its output contract") from None

    @staticmethod
    def _check_identity(result, case, request):
        if (result.case_id != case.case_id or result.run_id != request.run_id
                or result.candidate_set_sha256 != case.candidate_set_sha256
                or result.provenance.manifest_sha256 != case.manifest_sha256
                or result.provenance.seed != request.seed
                or result.provenance.input_sha256 != canonical_hash(case.model_dump(mode="json"))
                or result.provenance.config_sha256 != canonical_hash(request.model_dump(mode="json"))):
            raise ValueError("Adapter changed input or provenance")

    def certify(self, request: CertificateRequest) -> CertificateResult:
        self._budget(request)
        case = self._case(request.case_ref)
        if request.candidate_set_sha256 != case.candidate_set_sha256:
            raise ResearchFailure(422, "RESEARCH_SCOPE_MISMATCH", "Candidate set does not match case")
        try:
            check_schedule_structure(case, request.schedule)
        except ValueError:
            raise ResearchFailure(422, "RESEARCH_INVALID_SCHEDULE", "Schedule does not match case structure") from None
        if self._certifier is None:
            raise ResearchFailure(503, "RESEARCH_CERTIFIER_NOT_READY", "No registered certificate implementation")
        try:
            raw = self._certifier(case.model_copy(deep=True), request.model_copy(deep=True))
            if isinstance(raw, CertificateResult):
                raw = raw.model_dump(mode="json")
            result = CertificateResult.model_validate(raw)
            self._check_identity(result, case, request)
            if result.schedule_sha256 != canonical_hash(request.schedule.model_dump(mode="json")):
                raise ValueError("Certificate changed schedule")
            d = request.domain
            expected = sorted([(rho, lam) for rho in (d.rho_min, d.rho_max)
                               for lam in (d.lambda_min_mm, d.lambda_max_mm)])
            if sorted((v.theta.rho, v.theta.lambda_mm) for v in result.vertices) != expected:
                raise ValueError("Certificate vertices do not match domain")
            tol = result.numerical_tolerance_mm
            for v in result.vertices:
                if v.exact and (v.optimum_J_mm is None or v.lower_bound_J_mm is None
                                or abs(v.optimum_J_mm-v.lower_bound_J_mm) > tol):
                    raise ValueError("Exact vertex lacks optimum evidence")
                if not v.exact and v.optimum_J_mm is not None:
                    raise ValueError("Non-exact vertex cannot label a value as optimum")
                if v.lower_bound_J_mm is not None and v.lower_bound_J_mm > v.J_pi_mm + tol:
                    raise ValueError("Lower bound exceeds feasible schedule cost")
            status = result.certificate_status
            if status != "NOT_CERTIFIED":
                if result.validation.status != "PASS" or any(v.lower_bound_J_mm is None for v in result.vertices):
                    raise ValueError("Certificate lacks validation or lower bounds")
                upper = max(max(0.0, v.J_pi_mm-v.lower_bound_J_mm) for v in result.vertices)
                if result.max_regret_upper_mm is None or abs(upper-result.max_regret_upper_mm) > tol:
                    raise ValueError("Certificate regret is inconsistent")
                if status == "EXACT_MODELED" and not all(v.exact for v in result.vertices):
                    raise ValueError("Exact certificate requires four exact vertices")
            elif result.max_regret_upper_mm is not None:
                raise ValueError("Uncertified result cannot assert a bound")
            return result
        except Exception:
            log.exception("Research certificate adapter failed its output contract")
            raise ResearchFailure(500, "RESEARCH_ADAPTER_ERROR", "Certificate failed its output contract") from None


def load_manifest(path: Path) -> list[ResearchCase]:
    with path.open("rb") as stream:
        raw = stream.read(MAX_MANIFEST_BYTES + 1)
    if len(raw) > MAX_MANIFEST_BYTES:
        raise ValueError("Research manifest exceeds size limit")
    packet = json.loads(raw)
    if not isinstance(packet, dict) or set(packet) != {"schema_version", "manifest_sha256", "cases"}:
        raise ValueError("Invalid research manifest envelope")
    if packet["schema_version"] != VERSION or not isinstance(packet["cases"], list):
        raise ValueError("Invalid research manifest version/cases")
    cases = [ResearchCase.model_validate(case) for case in packet["cases"]]
    digest = manifest_hash(cases)
    if packet["manifest_sha256"] != digest or any(case.manifest_sha256 != digest for case in cases):
        raise ValueError("Research manifest hash mismatch")
    # Registry constructor also rejects duplicate IDs.
    ResearchService(cases)
    return cases


def service_from_environment() -> ResearchService:
    path = os.environ.get("OMNIDRAW_RESEARCH_MANIFEST")
    return ResearchService(load_manifest(Path(path)) if path else ())
