"""Cart Pydantic schemas."""

from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    """Base cart item schema."""

    product_id: int
    quantity: int = Field(ge=1, description="Quantity must be >= 1")


class CartItemAdd(CartItemBase):
    """Schema for adding item to cart."""


class CartItemUpdate(BaseModel):
    """Schema for updating cart item quantity."""

    product_id: int
    quantity: int = Field(ge=0, description="Quantity (0 = remove)")


class CartItemResponse(CartItemBase):
    """Schema for cart item response."""

    name: str
    price: Decimal
    total: Decimal
    image: str | None = None
    stock: int


class CartResponse(BaseModel):
    """Schema for full cart response."""

    items: list[CartItemResponse]
    total_price: Decimal
    total_items: int
