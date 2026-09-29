from typing import Protocol

from ..models import SimulatedCallRequest, SimulatedCallResult


class VoiceProvider(Protocol):
    """Small boundary that a production voice provider adapter must implement."""

    def simulate(self, request: SimulatedCallRequest) -> SimulatedCallResult: ...
