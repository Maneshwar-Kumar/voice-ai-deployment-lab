import logging
import os
import time
import uuid

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware

from . import __version__
from .models import DeploymentInput, DeploymentPlan, SimulatedCallRequest, SimulatedCallResult
from .planner import build_deployment_plan
from .providers import DeterministicVoiceProvider

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger("voice_ai_deployment_lab")

app = FastAPI(
    title="Voice AI Deployment Lab",
    version=__version__,
    description="Provider-neutral reference API using synthetic data and deterministic calls.",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Request-ID"],
)
provider = DeterministicVoiceProvider()


@app.middleware("http")
async def request_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    started = time.perf_counter()
    response: Response = await call_next(request)
    duration_ms = round((time.perf_counter() - started) * 1000, 2)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Response-Time-Ms"] = str(duration_ms)
    logger.info(
        "request_complete method=%s path=%s status=%s duration_ms=%s request_id=%s",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
        request_id,
    )
    return response


@app.get("/healthz")
def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/readyz")
def readiness() -> dict[str, str]:
    return {"status": "ready", "provider": "deterministic-demo"}


@app.post("/v1/deployment-plan", response_model=DeploymentPlan)
def deployment_plan(inputs: DeploymentInput) -> DeploymentPlan:
    return build_deployment_plan(inputs)


@app.post("/v1/simulate-call", response_model=SimulatedCallResult)
def simulate_call(request: SimulatedCallRequest) -> SimulatedCallResult:
    return provider.simulate(request)
