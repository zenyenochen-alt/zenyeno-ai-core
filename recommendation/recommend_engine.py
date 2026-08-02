"""Turn analysis scores into concrete sales actions."""

from core.models import MarketAnalysis, PricingAnalysis, ProductPrediction, SalesRecommendation


class RecommendEngine:
    def recommend(
        self,
        prediction: ProductPrediction,
        market: MarketAnalysis,
        pricing: PricingAnalysis,
    ) -> SalesRecommendation:
        suggestions = [
            f"Launch a small validation campaign at {pricing.currency} {pricing.recommended_price:.2f}.",
            f"Track conversion and acquisition cost in {prediction.market}.",
        ]
        if pricing.margin_percent < pricing.target_margin_percent:
            suggestions.append("Reduce landed cost or raise the selling price before launch.")
        if market.competition != "Low":
            suggestions.append("Differentiate the offer with a clear use-case and short-form video creative.")
        if prediction.recommendation == "YES":
            suggestions.append("Scale only after the test reaches the target contribution margin.")
        elif prediction.recommendation == "NO":
            suggestions[0] = "Do not launch until cost, demand, or differentiation improves."

        priority = "High" if prediction.recommendation == "YES" else "Medium" if prediction.recommendation == "TEST" else "Low"
        return SalesRecommendation(
            decision=prediction.recommendation,
            priority=priority,
            suggestions=suggestions,
        )
