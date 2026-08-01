"""Cost-based pricing baseline."""

from core.models import PricingAnalysis, ProductInput


class PricingOptimizer:
    def optimize(self, product: ProductInput) -> PricingAnalysis:
        multiplier = 3.5 if product.cost <= 10 else 2.8 if product.cost <= 30 else 2.2
        recommended_price = round(product.cost * multiplier, 2)
        profit = round(recommended_price - product.cost, 2)
        margin_percent = round((profit / recommended_price) * 100, 2)

        if margin_percent >= 70:
            pricing_score, strategy = 88, "Test Market"
        elif margin_percent >= 55:
            pricing_score, strategy = 78, "Test Market"
        elif margin_percent >= 40:
            pricing_score, strategy = 65, "Test Market"
        else:
            pricing_score, strategy = 40, "Avoid"

        return PricingAnalysis(
            cost=round(product.cost, 2),
            recommended_price=recommended_price,
            profit=profit,
            margin_percent=margin_percent,
            strategy=strategy,
            pricing_score=pricing_score,
        )
