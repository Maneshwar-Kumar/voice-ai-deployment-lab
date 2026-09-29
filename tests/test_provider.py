import pytest
from pydantic import ValidationError

from voice_ai_deployment_lab.models import SimulatedCallRequest, SimulatedCallResult
from voice_ai_deployment_lab.providers import DeterministicVoiceProvider


@pytest.fixture
def provider() -> DeterministicVoiceProvider:
    return DeterministicVoiceProvider()


def test_happy_path_books_only_after_tool_confirmation(
    provider: DeterministicVoiceProvider,
) -> None:
    result = provider.simulate(
        SimulatedCallRequest(caller_intent="I need my car serviced tomorrow")
    )

    assert result.contained is True
    assert result.escalated is False
    assert result.outcome == "Appointment booked and confirmed"
    assert any(event.component == "Calendar" and event.status == "ok" for event in result.timeline)


def test_missing_consent_forces_handoff(provider: DeterministicVoiceProvider) -> None:
    result = provider.simulate(
        SimulatedCallRequest(
            caller_intent="Book a service",
            customer_consented=False,
        )
    )

    assert result.escalated is True
    assert result.escalation_reason == "Consent not provided"
    assert "consent_missing" in result.policy_flags


def test_dependency_failure_uses_degraded_mode(provider: DeterministicVoiceProvider) -> None:
    result = provider.simulate(
        SimulatedCallRequest(
            caller_intent="Book a service",
            crm_available=False,
        )
    )

    assert result.contained is False
    assert result.escalation_reason == "CRM unavailable"
    assert "unverified booking" in result.outcome
    assert any(event.status == "timeout" for event in result.timeline)


def test_human_request_is_honoured(provider: DeterministicVoiceProvider) -> None:
    result = provider.simulate(
        SimulatedCallRequest(
            caller_intent="I need help",
            caller_requests_human=True,
        )
    )

    assert result.escalated is True
    assert result.escalation_reason == "Caller requested a person"


def test_result_rejects_inconsistent_escalation() -> None:
    with pytest.raises(ValidationError):
        SimulatedCallResult(
            outcome="invalid",
            contained=False,
            escalated=True,
            transcript=[],
            policy_flags=[],
            timeline=[],
            total_latency_ms=0,
        )
