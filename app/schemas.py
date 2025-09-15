from pydantic import BaseModel, PositiveInt
from typing import Optional
from datetime import datetime

class AddItemRequest(BaseModel):
    product_id: PositiveInt
    quantity: PositiveInt

class ProductBase(BaseModel):
    id: int
    name: str
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderItemResponse(BaseModel):
    product: ProductBase
    quantity: int
    class Config:
        from_attributes = True
    @property
    def price(self):
        return self.product.price
    @property
    def total_amount(self):
        return self.product.price * self.quantity

class ErrorResponse(BaseModel):
    detail: str