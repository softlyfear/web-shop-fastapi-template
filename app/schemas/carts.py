from decimal import Decimal

from pydantic import BaseModel, Field


class CartItemBase(BaseModel):
    product_id: int
    quantity: int = Field(ge=1, description="Количество должно быть >= 1")


class CartItemAdd(CartItemBase):
    """Схема для добавления товара в корзину."""

    pass


class CartItemUpdate(BaseModel):
    """Схема для обновления количества товара в корзине."""

    product_id: int
    quantity: int = Field(ge=0, description="Количество (0 = удалить)")


class CartItemResponse(CartItemBase):
    """Схема для отображения товара в корзине."""

    name: str
    price: Decimal
    total: Decimal
    image: str | None = None
    stock: int


class CartResponse(BaseModel):
    """Схема для отображения всей корзины."""

    items: list[CartItemResponse]
    total_price: Decimal
    total_items: int
