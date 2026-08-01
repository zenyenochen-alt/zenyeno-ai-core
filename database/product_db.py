from pydantic import BaseModel


class Product(BaseModel):
    name: str
    category: str
    cost: float
    market: str