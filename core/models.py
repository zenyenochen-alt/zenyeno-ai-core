"""Shared request and response contracts for the analysis pipeline."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


CompetitionLevel = Literal["Low", "Medium", "High"]
Decision = Literal["YES", "TEST", "NO"]


class StrictModel(BaseModel):
    """Base contract that rejects accidental or obsolete fields."""

    model_config = ConfigDict(extra="forbid")


class ProductInput(StrictModel):
    name: str = Field(min_length=1, max_length=200, examples=["Foldable Storage Box"])
    category: str = Field(min_length=1, max_length=120, examples=["Home Storage"])
    cost: float = Field(gt=0, le=1_000_000, examples=[5])
    market: str = Field(min_length=1, max_length=120, examples=["TikTok Philippines"])
    currency: str = Field(default="USD", min_length=3, max_length=3, pattern=r"^[A-Z]{3}$")
    shipping_cost: float = Field(default=0, ge=0, le=1_000_000)
    advertising_cost: float = Field(default=0, ge=0, le=1_000_000)
    platform_fee_percent: float = Field(default=0, ge=0, le=50)
    tax_percent: float = Field(default=0, ge=0, le=50)
    return_rate_percent: float = Field(default=0, ge=0, le=50)
    target_margin_percent: float = Field(default=20, ge=0, lt=90)

    @model_validator(mode="after")
    def validate_revenue_allocation(self) -> "ProductInput":
        allocated_percent = (
            self.platform_fee_percent
            + self.tax_percent
            + self.return_rate_percent
            + self.target_margin_percent
        )
        if allocated_percent >= 95:
            raise ValueError(
                "platform fees, tax, return reserve, and target margin must total less than 95%"
            )
        return self


class MarketAnalysis(StrictModel):
    market: str
    trend_score: int = Field(ge=0, le=100)
    demand: Literal["Low", "Medium", "High"]
    competition: CompetitionLevel
    buyer_interest: Literal["Weak", "Moderate", "Strong"]
    recommendation: Literal["POOR", "TEST", "GOOD"]


class PricingAnalysis(StrictModel):
    currency: str
    cost: float = Field(gt=0)
    recommended_price: float = Field(gt=0)
    shipping_cost: float = Field(ge=0)
    advertising_cost: float = Field(ge=0)
    platform_fee: float = Field(ge=0)
    tax: float = Field(ge=0)
    return_reserve: float = Field(ge=0)
    total_cost: float = Field(gt=0)
    profit: float
    margin_percent: float
    target_margin_percent: float
    strategy: Literal["Avoid", "Test Market", "Scale"]
    pricing_score: int = Field(ge=0, le=100)


class ProductPrediction(StrictModel):
    product: str
    market: str
    final_score: int = Field(ge=0, le=100)
    competition: CompetitionLevel
    recommended_price: float = Field(gt=0)
    profit_estimate: float
    recommendation: Decision


class SalesRecommendation(StrictModel):
    decision: Decision
    priority: Literal["Low", "Medium", "High"]
    suggestions: list[str]


class ProductAnalysis(StrictModel):
    product: str
    category: str
    market: str
    final_score: int = Field(ge=0, le=100)
    recommendation: Decision
    prediction: ProductPrediction
    market_analysis: MarketAnalysis
    pricing: PricingAnalysis
    sales_recommendations: SalesRecommendation
    report: str


class AnalysisRecord(StrictModel):
    id: int = Field(gt=0)
    created_at: datetime
    request: ProductInput
    result: ProductAnalysis


class AnalysisHistory(StrictModel):
    items: list[AnalysisRecord]
    total: int = Field(ge=0)
