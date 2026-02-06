"""Shopping cart management utilities."""

from decimal import Decimal

from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import product_crud
from app.schemas import CartItemResponse


class CartManager:
    """Session-based shopping cart manager."""

    @staticmethod
    def get_cart(request: Request) -> dict:
        """Get cart from session."""
        return request.session.get("cart", {})

    @staticmethod
    def save_cart(request: Request, cart: dict) -> None:
        """Сохранить корзину в сессию."""
        request.session["cart"] = cart

    @staticmethod
    def clear_cart(request: Request) -> None:
        """Clear cart."""
        request.session["cart"] = {}

    @staticmethod
    async def add_to_cart(
        request: Request,
        session: AsyncSession,
        product_id: int,
        quantity: int = 1,
    ) -> dict:
        """Add product to cart."""
        product = await product_crud.get(session, product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        if not product.is_active:
            raise HTTPException(status_code=400, detail="Product unavailable")

        cart = CartManager.get_cart(request)

        current_quantity = cart.get(str(product_id), {}).get("quantity", 0)
        new_quantity = current_quantity + quantity

        if new_quantity > product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {product.stock}",
            )

        cart[str(product_id)] = {
            "quantity": new_quantity,
            "price": float(product.price),
        }

        CartManager.save_cart(request, cart)
        return cart

    @staticmethod
    async def update_cart_item(
        request: Request,
        session: AsyncSession,
        product_id: int,
        quantity: int,
    ) -> dict:
        """Update cart item quantity."""
        cart = CartManager.get_cart(request)

        if str(product_id) not in cart:
            raise HTTPException(status_code=404, detail="Product not found in cart")

        if quantity == 0:
            del cart[str(product_id)]
        else:
            product = await product_crud.get(session, product_id)
            if not product:
                raise HTTPException(status_code=404, detail="Product not found")

            if quantity > product.stock:
                raise HTTPException(
                    status_code=400,
                    detail=f"Insufficient stock. Available: {product.stock}",
                )

            cart[str(product_id)]["quantity"] = quantity
            cart[str(product_id)]["price"] = float(product.price)

        CartManager.save_cart(request, cart)
        return cart

    @staticmethod
    async def remove_from_cart(request: Request, product_id: int) -> dict:
        """Remove product from cart."""
        cart = CartManager.get_cart(request)

        if str(product_id) not in cart:
            raise HTTPException(status_code=404, detail="Product not found in cart")

        del cart[str(product_id)]
        CartManager.save_cart(request, cart)
        return cart

    @staticmethod
    async def get_cart_details(
        request: Request,
        session: AsyncSession,
    ) -> dict:
        """Get detailed cart information."""
        cart = CartManager.get_cart(request)

        if not cart:
            return {
                "items": [],
                "total_price": Decimal("0"),
                "total_items": 0,
            }

        items = []
        total_price = Decimal("0")
        total_items = 0

        for product_id, cart_item in cart.items():
            product = await product_crud.get(session, int(product_id))
            if not product:
                continue

            quantity = cart_item["quantity"]
            price = Decimal(str(cart_item["price"]))
            item_total = price * quantity

            items.append(
                CartItemResponse(
                    product_id=int(product_id),
                    quantity=quantity,
                    name=product.name,
                    price=price,
                    total=item_total,
                    image=product.image,
                    stock=product.stock,
                )
            )

            total_price += item_total
            total_items += quantity

        return {
            "items": items,
            "total_price": total_price,
            "total_items": total_items,
        }
