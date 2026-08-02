from core.models import ProductInput
from pricing.pricing_optimizer import PricingOptimizer


def test_pricing_for_low_cost_product() -> None:
    product = ProductInput(name="Storage Box", category="Home", cost=5, market="PH")

    result = PricingOptimizer().optimize(product)

    assert result.recommended_price == 17.5
    assert result.profit == 12.5
    assert result.pricing_score == 88


def test_pricing_includes_supplied_operating_costs() -> None:
    product = ProductInput(
        name="Storage Box",
        category="Home",
        cost=5,
        market="PH",
        shipping_cost=2,
        advertising_cost=1,
        platform_fee_percent=10,
        tax_percent=5,
        return_rate_percent=5,
        target_margin_percent=20,
    )

    result = PricingOptimizer().optimize(product)

    assert result.recommended_price == 17.5
    assert result.total_cost == 11.51
    assert result.profit == 5.99
    assert result.margin_percent == 34.23
    assert result.strategy == "Test Market"
