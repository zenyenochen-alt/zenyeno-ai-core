"""Deterministic market-signal baseline used by the agent pipeline."""

from core.models import MarketAnalysis, ProductInput


class MarketIntelligence:
    """Estimate demand from transparent keyword heuristics.

    This module is intentionally replaceable by live marketplace data later.
    """

    def analyze(self, product: ProductInput) -> MarketAnalysis:
        text = f"{product.name} {product.category} {product.market}".lower()
        score = 70
        score += 5 if "tiktok" in text else 0
        score += 3 if "philippines" in text else 0
        score += 4 if any(word in text for word in ("home", "storage")) else 0
        score += 3 if any(word in text for word in ("beauty", "pet", "fitness")) else 0
        score -= 8 if any(word in text for word in ("fragile", "oversized", "hazardous")) else 0
        score = max(0, min(100, score))

        demand = "High" if score >= 80 else "Medium" if score >= 55 else "Low"
        high_competition_terms = ("beauty", "fashion", "electronics", "phone", "makeup")
        low_competition_terms = ("industrial", "replacement part", "specialty", "niche")
        competition = (
            "High"
            if any(word in text for word in high_competition_terms)
            else "Low"
            if any(word in text for word in low_competition_terms)
            else "Medium"
        )
        buyer_interest = "Strong" if score >= 80 else "Moderate" if score >= 55 else "Weak"
        recommendation = "GOOD" if score >= 75 else "TEST" if score >= 50 else "POOR"

        return MarketAnalysis(
            market=product.market,
            trend_score=score,
            demand=demand,
            competition=competition,
            buyer_interest=buyer_interest,
            recommendation=recommendation,
        )
