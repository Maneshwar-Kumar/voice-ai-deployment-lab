from ..models import SimulatedCallRequest, SimulatedCallResult, TimelineEvent


class DeterministicVoiceProvider:
    """Credential-free provider used for repeatable demos and contract tests."""

    def simulate(self, request: SimulatedCallRequest) -> SimulatedCallResult:
        base_timeline = [
            TimelineEvent(
                offset_ms=0,
                duration_ms=160,
                component="Telephony",
                action="Receive audio frame",
                status="ok",
            ),
            TimelineEvent(
                offset_ms=160,
                duration_ms=340,
                component="Speech-to-text",
                action="Transcribe caller turn",
                status="ok",
            ),
            TimelineEvent(
                offset_ms=500,
                duration_ms=90,
                component="Policy",
                action="Check consent and intent",
                status="ok",
            ),
            TimelineEvent(
                offset_ms=590,
                duration_ms=420,
                component="Orchestrator",
                action="Select next action",
                status="ok",
            ),
        ]

        if not request.customer_consented:
            return SimulatedCallResult(
                outcome="Stopped before processing personal data",
                contained=False,
                escalated=True,
                escalation_reason="Consent not provided",
                transcript=[
                    "Agent: Before we continue, may I process your details to arrange service?",
                    "Caller: No.",
                    "Agent: Understood. I will connect you to a colleague.",
                ],
                policy_flags=["consent_missing"],
                timeline=base_timeline
                + [
                    TimelineEvent(
                        offset_ms=1010,
                        duration_ms=210,
                        component="Handoff",
                        action="Transfer to human queue",
                        status="ok",
                    )
                ],
                total_latency_ms=1220,
            )

        if request.caller_requests_human:
            return SimulatedCallResult(
                outcome="Warm transfer completed",
                contained=False,
                escalated=True,
                escalation_reason="Caller requested a person",
                transcript=[
                    "Caller: I would like to speak to a service adviser.",
                    (
                        "Agent: Certainly. I will transfer you and pass along the reason for "
                        "your call."
                    ),
                ],
                policy_flags=[],
                timeline=base_timeline
                + [
                    TimelineEvent(
                        offset_ms=1010,
                        duration_ms=240,
                        component="Handoff",
                        action="Warm transfer with context",
                        status="ok",
                    )
                ],
                total_latency_ms=1250,
            )

        if not request.crm_available:
            return SimulatedCallResult(
                outcome="Callback captured; no unverified booking promised",
                contained=False,
                escalated=True,
                escalation_reason="CRM unavailable",
                transcript=[
                    "Agent: The booking system is temporarily unavailable.",
                    "Agent: I can arrange a callback rather than promise an unconfirmed slot.",
                ],
                policy_flags=["dependency_degraded"],
                timeline=base_timeline
                + [
                    TimelineEvent(
                        offset_ms=1010,
                        duration_ms=500,
                        component="CRM",
                        action="Read available slots",
                        status="timeout",
                    ),
                    TimelineEvent(
                        offset_ms=1510,
                        duration_ms=180,
                        component="Fallback",
                        action="Create callback task",
                        status="ok",
                    ),
                ],
                total_latency_ms=1690,
            )

        return SimulatedCallResult(
            outcome="Appointment booked and confirmed",
            contained=True,
            escalated=False,
            transcript=[
                f"Caller: {request.caller_intent}",
                "Agent: I found two verified service slots. Would tomorrow at 10:30 work?",
                "Caller: Yes.",
                "Agent: Your appointment is confirmed. I will send the details now.",
            ],
            policy_flags=[],
            timeline=base_timeline
            + [
                TimelineEvent(
                    offset_ms=1010,
                    duration_ms=280,
                    component="CRM",
                    action="Read customer and vehicle context",
                    status="ok",
                ),
                TimelineEvent(
                    offset_ms=1290,
                    duration_ms=310,
                    component="Calendar",
                    action="Reserve selected slot",
                    status="ok",
                ),
                TimelineEvent(
                    offset_ms=1600,
                    duration_ms=260,
                    component="Text-to-speech",
                    action="Stream confirmation",
                    status="ok",
                ),
                TimelineEvent(
                    offset_ms=1860,
                    duration_ms=80,
                    component="Events",
                    action="Emit outcome and quality telemetry",
                    status="ok",
                ),
            ],
            total_latency_ms=1940,
        )
