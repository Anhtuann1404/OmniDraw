"""Public DEV gateway. Does not register cases, read arbitrary paths or start print jobs."""

from fastapi import APIRouter, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.requests import ClientDisconnect

from .schemas import CertificateRequest, CertificateResult, ResearchCase, SolveRequest, SolveResult
from .service import ResearchFailure, ResearchService

MAX_REQUEST_BYTES = 1024 * 1024


def failure_response(status, code, message, findings=None):
    return JSONResponse(status_code=status, content={
        "outcome": "INVALID_INPUT" if status in (400, 403, 404, 413, 422) else "INTERNAL_ERROR",
        "error": {"code": code, "message": message}, "findings": findings or [],
    })


class ResearchRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def limited_handler(request: Request):
            try:
                chunks, size = [], 0
                async for chunk in request.stream():
                    size += len(chunk)
                    if size > MAX_REQUEST_BYTES:
                        return failure_response(413, "RESEARCH_PAYLOAD_LIMIT", "Research request exceeds size limit")
                    chunks.append(chunk)
                body = b"".join(chunks)

                async def receive():
                    return {"type": "http.request", "body": body, "more_body": False}

                return await handler(Request(request.scope, receive=receive))
            except RequestValidationError as exc:
                # Never echo raw input/NaN or Pydantic exception objects into JSON errors.
                findings = [{"location": list(e["loc"]), "type": e["type"]} for e in exc.errors()]
                return failure_response(422, "RESEARCH_INVALID_INPUT", "Invalid research request", findings)
            except ClientDisconnect:
                return failure_response(400, "RESEARCH_DISCONNECTED", "Incomplete research request")
            except ResearchFailure as exc:
                return failure_response(exc.status, exc.code, exc.message)

        return limited_handler


def create_router(service: ResearchService) -> APIRouter:
    router = APIRouter(prefix="/api/research", tags=["Research (draft gateway)"], route_class=ResearchRoute)

    @router.get("/capabilities")
    def capabilities():
        return service.capabilities()

    @router.post("/validate")
    def validate_case(case: ResearchCase):
        return service.validate_case(case)

    @router.post("/solve", response_model=SolveResult)
    def solve(request: SolveRequest):
        return service.solve(request)

    @router.post("/certify", response_model=CertificateResult)
    def certify(request: CertificateRequest):
        return service.certify(request)

    return router
