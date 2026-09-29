from fastapi.testclient import TestClient

from voice_ai_deployment_lab.app import app

client = TestClient(app)


def test_health_and_readiness() -> None:
    health = client.get("/healthz")
    ready = client.get("/readyz")

    assert health.status_code == 200
    assert health.json()["status"] == "ok"
    assert ready.status_code == 200
    assert ready.json() == {"status": "ready", "provider": "deterministic-demo"}


def test_plan_endpoint_validates_and_returns_request_context() -> None:
    response = client.post(
        "/v1/deployment-plan",
        json={
            "monthly_calls": 12000,
            "average_handle_minutes": 4.5,
            "human_cost_per_hour": 9,
            "expected_containment_rate": 0.58,
            "platform_cost_per_minute": 0.08,
            "implementation_cost": 18000,
            "language_count": 2,
            "integration_count": 3,
            "regulated_workflow": False,
        },
        headers={"X-Request-ID": "test-request"},
    )

    assert response.status_code == 200
    assert response.headers["X-Request-ID"] == "test-request"
    assert float(response.headers["X-Response-Time-Ms"]) >= 0
    assert response.json()["recommended_stage"] == "shadow"


def test_invalid_input_is_rejected() -> None:
    response = client.post("/v1/deployment-plan", json={"monthly_calls": -1})

    assert response.status_code == 422


def test_simulation_contract() -> None:
    response = client.post(
        "/v1/simulate-call",
        json={
            "caller_intent": "Please book my annual car service",
            "customer_consented": True,
            "crm_available": True,
            "caller_requests_human": False,
        },
    )

    body = response.json()
    assert response.status_code == 200
    assert body["outcome"] == "Appointment booked and confirmed"
    assert body["total_latency_ms"] == 1940
