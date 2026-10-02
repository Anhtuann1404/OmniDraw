"""HTTP gateway contract tests. Test adapters are not research solvers or an oracle."""

import copy
import json

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from backend.research.router import MAX_REQUEST_BYTES, create_router
from backend.research.schemas import ResearchCase, VERSION, canonical_hash
from backend.research.service import ResearchService, load_manifest, manifest_hash


def case_payload(split="synthetic", with_strokes=False):
    data = {
        "schema_version": VERSION, "case_id": "case-001", "dataset_version": "dev-v1",
        "manifest_sha256": "a" * 64, "split": split, "normalized_text": "",
        "normalization": "NFD", "candidates": [], "delay_policy": {},
        "geometry_policy": {"c_min_mm": 0.20, "flatten_policy_id": "polyline-v1",
                            "contact_policy_id": "contact-v1", "numeric_policy_id": "numeric-v1",
                            "separation_policy_id": "all-interactions-v1"},
        "boundary": {"p0_mm": [0.0, 0.0], "p_end_mm": [0.0, 0.0], "initial_pen": "UP",
                     "final_pen": "UP", "convention_id": "cycles-v1"},
    }
    if with_strokes:
        data["normalized_text"] = "a"
        data["candidates"] = [{"owner_index": 0, "grapheme": "a", "variants": [{
            "candidate_id": "a-v1", "source_hash": "b" * 64,
            "strokes": [{"stroke_id": "body", "role": "body", "owner_index": 0,
                         "reversible": False, "polyline_mm": [[0.0, 0.0], [1.0, 0.0]]},
                        {"stroke_id": "mark", "role": "mark", "owner_index": 0,
                         "reversible": True, "mark_type": "tone",
                         "polyline_mm": [[0.0, 1.0], [1.0, 1.0]]}],
            "body_order": ["body"], "mark_precedence": []}]}]
        data["delay_policy"] = {"tone": 0}
    return ResearchCase.prepare(data).model_dump(mode="json")


def solve_request(method="joint_dp"):
    return {"schema_version": VERSION, "run_id": "run-001", "case_ref": "case-001",
            "method": method, "theta": {"rho": 1.0, "lambda_mm": 2.0}, "baseline": None,
            "budget": {"wall_time_ms": 10000, "max_states": 100000,
                       "max_configurations": 10000, "memory_limit_mb": 512}, "seed": 42,
            "freeze_manifest_ref": None}


def client_for(case=None, solvers=None, certifier=None):
    app = FastAPI()
    cases = [ResearchCase.model_validate(case or case_payload())]
    service = ResearchService(cases, solvers, certifier)
    app.include_router(create_router(service))
    return TestClient(app), service


def provenance(case, request):
    return {"git_commit": "a" * 40, "dirty_patch_sha256": None,
            "manifest_sha256": case.manifest_sha256,
            "input_sha256": canonical_hash(case.model_dump(mode="json")),
            "config_sha256": canonical_hash(request.model_dump(mode="json")),
            "seed": request.seed, "runtime_versions": {"test-adapter": "1"}, "timing_source": "assumed"}


def empty_adapter(case, request):
    return {"run_id": request.run_id, "case_id": case.case_id, "method": request.method,
            "candidate_set_sha256": case.candidate_set_sha256, "contract_version": VERSION,
            "outcome": "OPTIMAL", "scope": "full_candidate_set", "enumeration_complete": False,
            "ranking_complete": False, "search_complete": True,
            "schedule": {"candidate_ids": [], "actions": [], "boundary_convention_id": "cycles-v1"},
            "metrics": {"L_down_mm": 0.0, "L_up_mm": 0.0, "N_cycle": 0, "J_mm": 0.0,
                        "total_wall_time_ms": 0.1},
            "bounds": {"lower_bound_J_mm": 0.0, "upper_bound_J_mm": 0.0},
            "provenance": provenance(case, request), "validation": {"status": "NOT_RUN"}, "error": None}


def test_capabilities_and_unavailable_method_are_honest():
    client, _ = client_for()
    capabilities = client.get("/api/research/capabilities").json()
    assert not any(capabilities["methods"].values())
    assert capabilities["public_holdout_enabled"] is False
    response = client.post("/api/research/solve", json=solve_request())
    assert response.status_code == 503
    assert response.json()["error"]["code"] == "RESEARCH_METHOD_NOT_READY"


def test_validation_is_structural_and_does_not_register_case():
    client, service = client_for()
    data = case_payload(with_strokes=True)
    data["case_id"] = "another"
    response = client.post("/api/research/validate", json=data)
    assert response.status_code == 200
    assert response.json()["geometric_validation"] == "NOT_RUN"
    request = dict(solve_request(), case_ref="another")
    assert client.post("/api/research/solve", json=request).status_code == 404


@pytest.mark.parametrize("mutate", [
    lambda d: d.update(candidate_set_sha256="c" * 64),
    lambda d: d["geometry_policy"].update(c_min_mm=0.10),
    lambda d: d.update(normalized_text="unexpected"),
    lambda d: d.update(delay_policy={"tone": True}),
    lambda d: d["candidates"][0].update(owner_index=2),
    lambda d: d["candidates"][0]["variants"][0].update(body_order=[]),
    lambda d: d["candidates"][0]["variants"][0]["strokes"][0].update(polyline_mm=[[0.,0.],[0.,0.]]),
])
def test_reject_invalid_case_without_echoing_input(mutate):
    client, _ = client_for()
    data = case_payload(with_strokes=True)
    mutate(data)
    response = client.post("/api/research/validate", json=data)
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "RESEARCH_INVALID_INPUT"
    assert "input" not in str(response.json()["findings"])


def test_mark_precedence_cycle_and_missing_delay():
    from pydantic import ValidationError
    data = case_payload(with_strokes=True)
    variant = data["candidates"][0]["variants"][0]
    other = copy.deepcopy(variant["strokes"][1]);other["stroke_id"] = "mark2"
    variant["strokes"].append(other)
    variant["mark_precedence"] = [["mark", "mark2"], ["mark2", "mark"]]
    with pytest.raises(ValidationError, match="Cyclic"):
        ResearchCase.prepare(data)
    data = case_payload(with_strokes=True);data["delay_policy"] = {}
    with pytest.raises(ValidationError, match="delay"):
        ResearchCase.prepare(data)


@pytest.mark.parametrize("value", [True, "1", float("nan"), float("inf"), -1, 0])
def test_invalid_theta_never_invokes_adapter(value):
    calls = []
    client, _ = client_for(solvers={"joint_dp": lambda *_: calls.append(1)})
    req = solve_request();req["theta"]["rho"] = value
    response = client.post("/api/research/solve", content=json.dumps(req), headers={"content-type": "application/json"})
    assert response.status_code == 422
    assert not calls


@pytest.mark.parametrize("method,options,valid", [
    ("beam", None, False), ("joint_dp", {"width": 5}, False),
    ("staged_top_m", {"width": 5}, False),
    ("beam", {"width": 5}, True),
    ("staged_top_m", {"ranker": "H_ref", "m": 2, "rank_at_theta0_ref": "theta0"}, True),
])
def test_method_specific_options(method, options, valid):
    client, _ = client_for();req=solve_request(method);req["baseline"] = options
    assert client.post("/api/research/solve", json=req).status_code == (503 if valid else 422)


def test_holdout_and_official_run_not_exposed():
    client, _ = client_for(case_payload(split="holdout"))
    assert client.post("/api/research/solve", json=solve_request()).status_code == 404
    assert client.post("/api/research/validate", json=case_payload(split="holdout")).status_code == 403
    client, _ = client_for();req=solve_request();req["freeze_manifest_ref"] = "a" * 64
    assert client.post("/api/research/solve", json=req).status_code == 403


def test_budget_and_payload_limits():
    client, _ = client_for();req=solve_request();req["budget"]["wall_time_ms"] = 30001
    assert client.post("/api/research/solve", json=req).status_code == 422
    response=client.post("/api/research/solve", content=b"x"*(MAX_REQUEST_BYTES+1))
    assert response.status_code == 413


def test_registered_adapter_result_and_provenance_roundtrip():
    client, _ = client_for(solvers={"joint_dp": empty_adapter})
    response = client.post("/api/research/solve", json=solve_request())
    assert response.status_code == 200
    assert response.json()["outcome"] == "OPTIMAL"
    assert response.json()["validation"]["status"] == "NOT_RUN"


@pytest.mark.parametrize("mutate", [
    lambda r: r.update(search_complete=False),
    lambda r: r.update(candidate_set_sha256="b" * 64),
    lambda r: r["provenance"].update(config_sha256="b" * 64),
    lambda r: r["metrics"].update(J_mm=5.0),
    lambda r: r["metrics"].update(J_mm=float("nan")),
])
def test_adapter_cannot_publish_false_or_mismatched_claim(mutate):
    def adapter(case, req):
        result=empty_adapter(case,req);mutate(result);return result
    client,_=client_for(solvers={"joint_dp":adapter})
    response=client.post("/api/research/solve",json=solve_request())
    assert response.status_code == 500
    assert response.json()["error"]["code"] == "RESEARCH_ADAPTER_ERROR"


def test_timeout_keeps_outcome_and_incumbent():
    def adapter(case,req):
        result=empty_adapter(case,req);result.update(outcome="TIMEOUT",search_complete=False)
        return result
    client,_=client_for(solvers={"joint_dp":adapter})
    result=client.post("/api/research/solve",json=solve_request()).json()
    assert result["outcome"] == "TIMEOUT" and result["schedule"] is not None


def certificate_request():
    return {"schema_version":VERSION,"run_id":"cert-001","case_ref":"case-001",
            "candidate_set_sha256":case_payload()["candidate_set_sha256"],
            "schedule":{"candidate_ids":[],"actions":[],"boundary_convention_id":"cycles-v1"},
            "domain":{"rho_min":1.0,"rho_max":2.0,"lambda_min_mm":0.0,"lambda_max_mm":2.0},
            "budget":solve_request()["budget"],"seed":42,"freeze_manifest_ref":None}


def certificate_adapter(case,req):
    vertices=[{"theta":{"rho":rho,"lambda_mm":lam},"J_pi_mm":5.0,"lower_bound_J_mm":3.0,
               "optimum_J_mm":3.0,"exact":True,"evidence_id":f"vertex-{i}"}
              for i,(rho,lam) in enumerate([(1.,0.),(1.,2.),(2.,0.),(2.,2.)])]
    return {"run_id":req.run_id,"case_id":case.case_id,"candidate_set_sha256":case.candidate_set_sha256,
            "schedule_sha256":canonical_hash(req.schedule.model_dump(mode="json")),"contract_version":VERSION,
            "scope":"full_candidate_set","validation":{"status":"PASS","checker_id":"test-only","checker_version":"1"},
            "vertices":vertices,"certificate_status":"EXACT_MODELED","max_regret_upper_mm":2.0,
            "numerical_tolerance_mm":1e-9,"provenance":provenance(case,req)}


def test_certificate_readiness_and_vertex_contract():
    client,_=client_for()
    assert client.post("/api/research/certify",json=certificate_request()).status_code == 503
    client,_=client_for(certifier=certificate_adapter)
    assert client.post("/api/research/certify",json=certificate_request()).status_code == 200


@pytest.mark.parametrize("mutate",[
    lambda r:r["vertices"][0].update(exact=False,optimum_J_mm=None),
    lambda r:r["vertices"][0]["theta"].update(rho=3.0),
    lambda r:r.update(schedule_sha256="d"*64),
    lambda r:r.update(max_regret_upper_mm=0.0),
    lambda r:r["validation"].update(status="NOT_RUN"),
])
def test_reject_invalid_certificate_claims(mutate):
    def adapter(case,req):
        r=certificate_adapter(case,req);mutate(r);return r
    client,_=client_for(certifier=adapter)
    assert client.post("/api/research/certify",json=certificate_request()).status_code == 500


def test_manifest_hash_duplicates_and_no_request_path_access(tmp_path):
    case=ResearchCase.model_validate(case_payload())
    digest=manifest_hash([case]);case.manifest_sha256=digest
    packet={"schema_version":VERSION,"manifest_sha256":digest,"cases":[case.model_dump(mode="json")]}
    path=tmp_path/'dev-manifest.json';path.write_text(json.dumps(packet))
    assert load_manifest(path)[0].case_id == "case-001"
    packet["cases"][0]["boundary"]["p_end_mm"][0]=5.0;path.write_text(json.dumps(packet))
    with pytest.raises(ValueError):load_manifest(path)
    with pytest.raises(ValueError,match="Ambiguous"):ResearchService([case,case])
    client,_=client_for();req=solve_request();req["case_ref"] = "../../.env"
    assert client.post("/api/research/solve",json=req).status_code == 404


def test_real_app_exposes_gateway_and_keeps_product_routes():
    from backend.main import app
    client = TestClient(app)
    assert client.get("/api/research/capabilities").status_code == 200
    schema = app.openapi()
    assert "post" in schema["paths"]["/api/research/solve"]
    assert "post" in schema["paths"]["/api/ai/generate"]
    assert "post" in schema["paths"]["/api/print/start"]


@pytest.mark.parametrize("outcome", ["OPTIMAL", "NO_FEASIBLE_IN_PREFIX"])
@pytest.mark.parametrize("ranking_complete", [True, False])
def test_exact_prefix_requires_certified_ranking_not_exhaustive_enumeration(outcome, ranking_complete):
    def adapter(case, request):
        result = empty_adapter(case, request)
        result.update(scope="declared_prefix", outcome=outcome,
                      enumeration_complete=False, ranking_complete=ranking_complete)
        if outcome == "NO_FEASIBLE_IN_PREFIX":
            result["schedule"] = None
            result["metrics"] = {"total_wall_time_ms": 0.1}
            result["bounds"] = {}
        return result
    client, _ = client_for(solvers={"staged_top_m": adapter})
    request = solve_request("staged_top_m")
    request["baseline"] = {"ranker": "H_geom", "m": 1, "rank_at_theta0_ref": "dev-theta0"}
    response = client.post("/api/research/solve", json=request)
    assert response.status_code == (200 if ranking_complete else 500)
    if ranking_complete:
        assert response.json()["enumeration_complete"] is False
        assert response.json()["outcome"] == outcome
