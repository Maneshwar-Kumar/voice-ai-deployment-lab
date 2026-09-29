from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class RolloutStage(StrEnum):
    DISCOVERY = "discovery"
    SHADOW = "shadow"
    ASSISTED = "assisted"
    LIMITED_PRODUCTION = "limited-production"
    SCALE = "scale"


class DeploymentInput(BaseModel):
    monthly_calls: int = Field(default=12_000, ge=100, le=10_000_000)
    average_handle_minutes: float = Field(default=4.5, gt=0, le=120)
    human_cost_per_hour: float = Field(default=9.0, ge=0, le=1_000)
    expected_containment_rate: float = Field(default=0.58, ge=0, le=0.95)
    platform_cost_per_minute: float = Field(default=0.08, ge=0, le=10)
    implementation_cost: float = Field(default=18_000, ge=0, le=100_000_000)
    language_count: int = Field(default=2, ge=1, le=50)
    integration_count: int = Field(default=3, ge=0, le=50)
    regulated_workflow: bool = False


class Economics(BaseModel):
    current_monthly_cost: float
    projected_monthly_cost: float
    monthly_benefit: float
    annual_benefit: float
    payback_months: float | None


class Gate(BaseModel):
    name: str
    threshold: str
    owner: str


class Risk(BaseModel):
    name: str
    level: str
    mitigation: str


class DeploymentPlan(BaseModel):
    recommended_stage: RolloutStage
    economics: Economics
    gates: list[Gate]
    risks: list[Risk]
    assumptions: list[str]


class SimulatedCallRequest(BaseModel):
    caller_intent: str = Field(min_length=3, max_length=200)
    customer_consented: bool = True
    crm_available: bool = True
    caller_requests_human: bool = False


class TimelineEvent(BaseModel):
    offset_ms: int = Field(ge=0)
    duration_ms: int = Field(ge=0)
    component: str
    action: str
    status: str


class SimulatedCallResult(BaseModel):
    outcome: str
    contained: bool
    escalated: bool
    escalation_reason: str | None = None
    transcript: list[str]
    policy_flags: list[str]
    timeline: list[TimelineEvent]
    total_latency_ms: int

    @model_validator(mode="after")
    def escalation_is_consistent(self) -> "SimulatedCallResult":
        if self.escalated and not self.escalation_reason:
            raise ValueError("escalated calls require an escalation reason")
        if not self.escalated and self.escalation_reason:
            raise ValueError("non-escalated calls cannot have an escalation reason")
        return self
