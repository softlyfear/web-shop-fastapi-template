from fastapi import APIRouter, HTTPException, status

from app.core import SessionDep
from app.crud import product_crud
from app.schemas import ProductCreate, ProductRead, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.post("/", response_model=ProductRead, status_code=status.HTTP_201_CREATED)
async def create_products(
    product_in: ProductCreate,
    session: SessionDep,
):
    """Создать продукт."""
    return await product_crud.create_product(session, product_in)


@router.get("/{product_id}", response_model=ProductRead, status_code=status.HTTP_200_OK)
async def get_product(
    product_id: int,
    session: SessionDep,
):
    """Получить продукт по ID."""
    product = await product_crud.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return product


@router.get("/", response_model=list[ProductRead], status_code=status.HTTP_200_OK)
async def get_products(
    session: SessionDep,
    offset: int = 0,
    limit: int = 20,
):
    """Получить все продукты с пагинацией."""
    return await product_crud.get_products(session, offset, limit)


@router.patch(
    "/{product_id}", response_model=ProductRead, status_code=status.HTTP_200_OK
)
async def update_product(
    session: SessionDep,
    product_id: int,
    product_in: ProductUpdate,
):
    """Обновление продукта."""
    product = await product_crud.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return await product_crud.update_product(session, product, product_in)


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    session: SessionDep,
    product_id: int,
):
    """Удалить продукт по ID."""
    product = await product_crud.get_product(session, product_id)
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    await product_crud.delete_product(session, product)
