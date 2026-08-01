"""Markdown report rendering."""

from core.models import MarketAnalysis, PricingAnalysis, ProductInput, ProductPrediction, SalesRecommendation


class ReportGenerator:
    def generate(
        self,
        product: ProductInput,
        prediction: ProductPrediction,
        market: MarketAnalysis,
        pricing: PricingAnalysis,
        recommendations: SalesRecommendation,
    ) -> str:
        actions = "\n".join(f"- {item}" for item in recommendations.suggestions)
        return (
            f"# Product Analysis: {product.name}\n\n"
            f"- Market: {product.market}\n"
            f"- Category: {product.category}\n"
            f"- Final score: {prediction.final_score}/100\n"
            f"- Decision: {prediction.recommendation}\n\n"
            f"## Market\n\n"
            f"Demand is **{market.demand}**, buyer interest is **{market.buyer_interest}**, "
            f"and competition is **{market.competition}**.\n\n"
            f"## Pricing\n\n"
            f"Recommended price: **{pricing.recommended_price:.2f}**; estimated gross profit before "
            f"fees, shipping, tax, returns, and advertising: **{pricing.profit:.2f}** "
            f"({pricing.margin_percent:.2f}% gross margin).\n\n"
            f"## Actions\n\n{actions}"
        )
