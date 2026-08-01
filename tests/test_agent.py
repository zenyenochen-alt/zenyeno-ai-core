from core.agent_controller import AgentController
from core.models import ProductInput


def test_complete_agent_pipeline() -> None:
    product = ProductInput(
        name="Foldable Storage Box",
        category="Home Storage",
        cost=5,
        market="TikTok Philippines",
    )

    result = AgentController().analyze(product)
    payload = result.model_dump()

    assert result.final_score == 85
    assert result.prediction.final_score == result.final_score
    assert result.pricing.recommended_price == 17.5
    assert result.market_analysis.trend_score == 82
    assert "potential_score" not in str(payload)
    assert "# Product Analysis" in result.report
