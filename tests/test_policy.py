from voice_ai_deployment_lab.models import SimulatedCallRequest
from voice_ai_deployment_lab.providers import DeterministicVoiceProvider


def test_no_scenario_promises_a_booking_when_crm_is_down() -> None:
    result = DeterministicVoiceProvider().simulate(
        SimulatedCallRequest(caller_intent="Book a service", crm_available=False)
    )

    combined_transcript = " ".join(result.transcript).lower()
    assert "your appointment is confirmed" not in combined_transcript
    assert "callback" in combined_transcript


def test_no_personal_details_are_emitted_in_telemetry() -> None:
    result = DeterministicVoiceProvider().simulate(
        SimulatedCallRequest(caller_intent="Book my vehicle service")
    )

    for event in result.timeline:
        assert "phone" not in event.action.lower()
        assert "email" not in event.action.lower()
        assert "registration number" not in event.action.lower()
