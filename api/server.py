"""FastAPI entry point."""

from fastapi import FastAPI

from core.agent_controller import AgentController
from core.models import ProductAnalysis, ProductInput

app = FastAPI(
    title="Zenyeno AI Ecommerce Product Analysis Engine",
    description="Product research, potential scoring, and pricing optimization API.",
    version="0.1.0",
)
controller = AgentController()


@app.get("/health", tags=["system"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/analyze", response_model=ProductAnalysis, tags=["analysis"])
def analyze(product: ProductInput) -> ProductAnalysis:
    return controller.analyze(product)
