"""Cost-based pricing baseline."""

import math

from core.models import PricingAnalysis, ProductInput


class PricingOptimizer:
    def optimize(self, product: ProductInput) -> PricingAnalysis:
        multiplier = 3.5 if product.cost <= 10 else 2.8 if product.cost <= 30 else 2.2
        baseline_price = product.cost * multiplier

        variable_rate = (
            product.platform_fee_percent + product.tax_percent + product.return_rate_percent
        ) / 100
        target_rate = product.target_margin_percent / 100
        fixed_cost = product.cost + product.shipping_cost + product.advertising_cost
        available_rate = 1 - variable_rate - target_rate
        target_price = fixed_cost / available_rate
        recommended_price = math.ceil(max(baseline_price, target_price) * 100) / 100

        platform_fee = round(recommended_price * product.platform_fee_percent / 100, 2)
        tax = round(recommended_price * product.tax_percent / 100, 2)
        return_reserve = round(recommended_price * product.return_rate_percent / 100, 2)
        total_cost = round(
            product.cost
            + product.shipping_cost
            + product.advertising_cost
            + platform_fee
            + tax
            + return_reserve,
            2,
        )
        profit = round(recommended_price - total_cost, 2)
        margin_percent = round((profit / recommended_price) * 100, 2)

        margin_gap = margin_percent - product.target_margin_percent
        pricing_score = max(0, min(100, round(60 + margin_gap * 0.55)))
        if margin_gap >= 20 and profit >= 15:
            strategy = "Scale"
        elif margin_gap >= 0:
            strategy = "Test Market"
        else:
            strategy = "Avoid"

        return PricingAnalysis(
            currency=product.currency,
            cost=round(product.cost, 2),
            recommended_price=recommended_price,
            shipping_cost=round(product.shipping_cost, 2),
            advertising_cost=round(product.advertising_cost, 2),
            platform_fee=platform_fee,
            tax=tax,
            return_reserve=return_reserve,
            total_cost=total_cost,
            profit=profit,
            margin_percent=margin_percent,
            target_margin_percent=product.target_margin_percent,
            strategy=strategy,
            pricing_score=pricing_score,
        )
