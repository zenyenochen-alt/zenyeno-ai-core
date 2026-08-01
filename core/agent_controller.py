"""Orchestrates the complete product-analysis workflow."""

from core.models import ProductAnalysis, ProductInput
from core.report_generator import ReportGenerator
from market.market_intelligence import MarketIntelligence
from prediction.product_predictor import ProductPredictor
from pricing.pricing_optimizer import PricingOptimizer
from recommendation.recommend_engine import RecommendEngine


class AgentController:
    def __init__(self) -> None:
        self.market_intelligence = MarketIntelligence()
        self.pricing_optimizer = PricingOptimizer()
        self.product_predictor = ProductPredictor()
        self.recommend_engine = RecommendEngine()
        self.report_generator = ReportGenerator()

    def analyze(self, product: ProductInput) -> ProductAnalysis:
        market = self.market_intelligence.analyze(product)
        pricing = self.pricing_optimizer.optimize(product)
        prediction = self.product_predictor.predict(product, market, pricing)
        recommendations = self.recommend_engine.recommend(prediction, market, pricing)
        report = self.report_generator.generate(product, prediction, market, pricing, recommendations)

        return ProductAnalysis(
            product=product.name,
            category=product.category,
            market=product.market,
            final_score=prediction.final_score,
            recommendation=prediction.recommendation,
            prediction=prediction,
            market_analysis=market,
            pricing=pricing,
            sales_recommendations=recommendations,
            report=report,
        )
