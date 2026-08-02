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
            f"Recommended price: **{pricing.currency} {pricing.recommended_price:.2f}**. "
            f"Estimated profit after the supplied product, shipping, advertising, platform fee, "
            f"tax, and return-reserve assumptions: **{pricing.currency} {pricing.profit:.2f}** "
            f"({pricing.margin_percent:.2f}% margin versus a "
            f"{pricing.target_margin_percent:.2f}% target).\n\n"
            f"- Product cost: {pricing.currency} {pricing.cost:.2f}\n"
            f"- Shipping: {pricing.currency} {pricing.shipping_cost:.2f}\n"
            f"- Advertising: {pricing.currency} {pricing.advertising_cost:.2f}\n"
            f"- Platform fee: {pricing.currency} {pricing.platform_fee:.2f}\n"
            f"- Tax: {pricing.currency} {pricing.tax:.2f}\n"
            f"- Return reserve: {pricing.currency} {pricing.return_reserve:.2f}\n"
            f"- Total estimated cost: {pricing.currency} {pricing.total_cost:.2f}\n\n"
            f"## Actions\n\n{actions}"
        )
