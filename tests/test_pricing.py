from core.models import ProductInput
from pricing.pricing_optimizer import PricingOptimizer


def test_pricing_for_low_cost_product() -> None:
    product = ProductInput(name="Storage Box", category="Home", cost=5, market="PH")

    result = PricingOptimizer().optimize(product)

    assert result.recommended_price == 17.5
    assert result.profit == 12.5
    assert result.pricing_score == 88
