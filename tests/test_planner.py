from voice_ai_deployment_lab.models import DeploymentInput, RolloutStage
from voice_ai_deployment_lab.planner import build_deployment_plan


def test_positive_case_recommends_shadow_mode() -> None:
    plan = build_deployment_plan(DeploymentInput())

    assert plan.recommended_stage == RolloutStage.SHADOW
    assert plan.economics.current_monthly_cost == 8100.0
    assert plan.economics.projected_monthly_cost == 7722.0
    assert plan.economics.monthly_benefit == 378.0
    assert plan.economics.payback_months == 47.6
    assert len(plan.gates) == 5


def test_unfavourable_economics_stays_in_discovery() -> None:
    plan = build_deployment_plan(
        DeploymentInput(
            human_cost_per_hour=4,
            platform_cost_per_minute=0.3,
            expected_containment_rate=0.2,
        )
    )

    assert plan.recommended_stage == RolloutStage.DISCOVERY
    assert plan.economics.monthly_benefit < 0
    assert plan.economics.payback_months is None


def test_risk_register_expands_for_complex_workflow() -> None:
    plan = build_deployment_plan(
        DeploymentInput(regulated_workflow=True, language_count=5, integration_count=7)
    )

    names = {risk.name for risk in plan.risks}
    assert "Regulatory non-compliance" in names
    assert "Uneven multilingual quality" in names
    assert "Integration-chain fragility" in names
    assert plan.recommended_stage == RolloutStage.DISCOVERY
