from .models import DeploymentInput, DeploymentPlan, Economics, Gate, Risk, RolloutStage


def build_deployment_plan(inputs: DeploymentInput) -> DeploymentPlan:
    human_minutes = inputs.monthly_calls * inputs.average_handle_minutes
    current_cost = human_minutes / 60 * inputs.human_cost_per_hour
    platform_cost = human_minutes * inputs.platform_cost_per_minute
    residual_human_cost = current_cost * (1 - inputs.expected_containment_rate)
    projected_cost = platform_cost + residual_human_cost
    monthly_benefit = current_cost - projected_cost
    payback = None
    if monthly_benefit > 0:
        payback = inputs.implementation_cost / monthly_benefit

    risks = _build_risks(inputs)
    severe_risks = sum(risk.level == "high" for risk in risks)
    stage = RolloutStage.SHADOW
    if monthly_benefit <= 0 or severe_risks >= 3:
        stage = RolloutStage.DISCOVERY

    return DeploymentPlan(
        recommended_stage=stage,
        economics=Economics(
            current_monthly_cost=round(current_cost, 2),
            projected_monthly_cost=round(projected_cost, 2),
            monthly_benefit=round(monthly_benefit, 2),
            annual_benefit=round(monthly_benefit * 12, 2),
            payback_months=round(payback, 1) if payback is not None else None,
        ),
        gates=_quality_gates(),
        risks=risks,
        assumptions=[
            "Every call consumes the full average handle time.",
            "Contained calls avoid the modelled human handling cost.",
            "Platform cost includes voice inference but excludes telephony and taxes.",
            "Benefits exclude conversion uplift, after-hours coverage, and quality gains.",
        ],
    )


def _quality_gates() -> list[Gate]:
    return [
        Gate(
            name="Task success", threshold=">= 85% on the approved evaluation set", owner="Product"
        ),
        Gate(name="Unsafe response", threshold="< 0.5% with zero critical events", owner="Risk"),
        Gate(name="Human transfer", threshold=">= 98% successful connection", owner="Operations"),
        Gate(
            name="Response latency",
            threshold="p95 < 1,500 ms after caller turn",
            owner="Engineering",
        ),
        Gate(
            name="Appointment integrity",
            threshold=">= 99.5% valid writes",
            owner="Business systems",
        ),
    ]


def _build_risks(inputs: DeploymentInput) -> list[Risk]:
    risks = [
        Risk(
            name="Incorrect commitment",
            level="high",
            mitigation="Use tool-confirmed slots only; require explicit confirmation before write.",
        ),
        Risk(
            name="Human handoff failure",
            level="high",
            mitigation="Maintain warm-transfer fallback, queue monitoring, and callback capture.",
        ),
        Risk(
            name="PII exposure",
            level="medium",
            mitigation="Redact logs, restrict retention, and isolate access by operating role.",
        ),
    ]
    if inputs.regulated_workflow:
        risks.append(
            Risk(
                name="Regulatory non-compliance",
                level="high",
                mitigation=(
                    "Obtain legal sign-off, version consent language, and retain audit events."
                ),
            )
        )
    if inputs.language_count > 3:
        risks.append(
            Risk(
                name="Uneven multilingual quality",
                level="medium",
                mitigation=(
                    "Maintain language-specific evaluation sets and route low-confidence turns."
                ),
            )
        )
    if inputs.integration_count > 4:
        risks.append(
            Risk(
                name="Integration-chain fragility",
                level="high",
                mitigation=(
                    "Add timeouts, idempotency keys, circuit breakers, and degraded-mode scripts."
                ),
            )
        )
    return risks
