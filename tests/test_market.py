from core.models import ProductInput
from market.market_intelligence import MarketIntelligence


def test_market_analysis_for_demo_product() -> None:
    product = ProductInput(
        name="Foldable Storage Box",
        category="Home Storage",
        cost=5,
        market="TikTok Philippines",
    )

    result = MarketIntelligence().analyze(product)

    assert result.trend_score == 82
    assert result.demand == "High"
    assert result.competition == "Medium"
    assert result.recommendation == "GOOD"


def test_market_competition_is_independent_from_trend_score() -> None:
    product = ProductInput(
        name="Phone Beauty Light",
        category="Electronics",
        cost=8,
        market="TikTok Thailand",
    )

    result = MarketIntelligence().analyze(product)

    assert result.competition == "High"
