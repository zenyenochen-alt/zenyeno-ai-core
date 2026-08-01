from core.models import ProductInput
from market.market_intelligence import MarketIntelligence
from prediction.product_predictor import ProductPredictor
from pricing.pricing_optimizer import PricingOptimizer


def test_predictor_uses_final_score_only() -> None:
    product = ProductInput(
        name="Foldable Storage Box",
        category="Home Storage",
        cost=5,
        market="TikTok Philippines",
    )
    market = MarketIntelligence().analyze(product)
    pricing = PricingOptimizer().optimize(product)

    result = ProductPredictor().predict(product, market, pricing)
    payload = result.model_dump()

    assert result.final_score == 85
    assert result.recommendation == "YES"
    assert "potential_score" not in payload
