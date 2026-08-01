"""Shared request and response contracts for the analysis pipeline."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


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


class MarketAnalysis(StrictModel):
    market: str
    trend_score: int = Field(ge=0, le=100)
    demand: Literal["Low", "Medium", "High"]
    competition: CompetitionLevel
    buyer_interest: Literal["Weak", "Moderate", "Strong"]
    recommendation: Literal["POOR", "TEST", "GOOD"]


class PricingAnalysis(StrictModel):
    cost: float = Field(gt=0)
    recommended_price: float = Field(gt=0)
    profit: float
    margin_percent: float
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
