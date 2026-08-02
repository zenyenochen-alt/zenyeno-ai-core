"""Product-potential scoring."""

from core.models import MarketAnalysis, PricingAnalysis, ProductInput, ProductPrediction


class ProductPredictor:
    def predict(
        self,
        product: ProductInput,
        market: MarketAnalysis,
        pricing: PricingAnalysis,
    ) -> ProductPrediction:
        competition_adjustment = {"Low": 5, "Medium": 0, "High": -10}[market.competition]
        final_score = round(
            (market.trend_score * 0.55)
            + (pricing.pricing_score * 0.45)
            + competition_adjustment
        )
        final_score = max(0, min(100, final_score))
        recommendation = "YES" if final_score >= 80 else "TEST" if final_score >= 60 else "NO"

        return ProductPrediction(
            product=product.name,
            market=product.market,
            final_score=final_score,
            competition=market.competition,
            recommended_price=pricing.recommended_price,
            profit_estimate=pricing.profit,
            recommendation=recommendation,
        )
