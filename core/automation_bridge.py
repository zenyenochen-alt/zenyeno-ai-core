"""Secure server-to-server bridge into the private automation engine."""

from __future__ import annotations

import hashlib
import re

import httpx

from core.models import ProductAnalysis, ProductInput


MARKET_REGIONS = {
    "philippines": "PH",
    "thailand": "TH",
    "malaysia": "MY",
    "singapore": "SG",
    "vietnam": "VN",
    "indonesia": "ID",
    "united states": "US",
    "usa": "US",
}


def market_region(market: str) -> str:
    normalized = market.strip().lower()
    for name, region in MARKET_REGIONS.items():
        if name in normalized:
            return region
    if re.fullmatch(r"[A-Za-z]{2}", market.strip()):
        return market.strip().upper()
    raise ValueError(f"Unsupported target market: {market}")


def build_candidate_import(product: ProductInput, analysis: ProductAnalysis) -> dict:
    identity = "|".join(
        [product.name.strip().lower(), product.category.strip().lower(), product.market.strip().lower()]
    )
    source_product_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:24]
    competition_scores = {"Low": 80, "Medium": 55, "High": 25}
    return {
        "source": "ZENYENO_ANALYSIS",
        "candidates": [
            {
                "candidate_id": f"zenyeno-{source_product_id}",
                "source_product_id": source_product_id,
                "region": market_region(product.market),
                "title": product.name,
                "category_name": product.category,
                "currency": analysis.pricing.currency,
                "selling_price": analysis.pricing.recommended_price,
                "procurement_cost": product.cost,
                "shipping_cost": product.shipping_cost,
                "platform_cost": (
                    analysis.pricing.platform_fee
                    + analysis.pricing.tax
                    + analysis.pricing.return_reserve
                    + analysis.pricing.advertising_cost
                ),
                "metrics": {
                    "zenyeno_final_score": analysis.final_score,
                    "zenyeno_recommendation": analysis.recommendation,
                    "trend_score": analysis.market_analysis.trend_score,
                    "competition_score": competition_scores[analysis.market_analysis.competition],
                    "margin_score": analysis.pricing.pricing_score,
                    "margin_percent": analysis.pricing.margin_percent,
                    "analysis_version": "1.1.0",
                },
            }
        ],
    }


def import_candidate(api_url: str, api_key: str, payload: dict) -> dict:
    response = httpx.post(
        f"{api_url.rstrip('/')}/api/internal/candidates/import",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=15,
    )
    response.raise_for_status()
    result = response.json()
    if result.get("status") != "ok" or result.get("imported") != 1:
        raise RuntimeError("Automation engine returned an invalid import receipt.")
    return result
