from typing import TYPE_CHECKING

from fastapi import APIRouter, status
from pydantic import BaseModel

from app.core import SessionDep

if TYPE_CHECKING:
    from app.api import get_or_404


def build_crud_router(
    *,
    crud,
    create_schema: type[BaseModel],
    update_schema: type[BaseModel],
    read_schema: type[BaseModel],
) -> APIRouter:
    router = APIRouter()

    @router.post("/", response_model=read_schema, status_code=status.HTTP_201_CREATED)
    async def create_item(item_in: create_schema, session: SessionDep):  # type: ignore[valid-type]
        return await crud.create(session, item_in)

    @router.get(
        "/{item_id}", response_model=read_schema, status_code=status.HTTP_200_OK
    )
    async def get_item(item_id: int, session: SessionDep):
        return await get_or_404(crud, session, item_id)

    @router.get("/", response_model=list[read_schema], status_code=status.HTTP_200_OK)
    async def get_items(session: SessionDep, offset: int = 0, limit: int = 20):
        return await crud.get_multi(session, offset, limit)

    @router.patch(
        "/{item_id}", response_model=read_schema, status_code=status.HTTP_200_OK
    )
    async def update_item(item_id: int, item_in: update_schema, session: SessionDep):  # type: ignore[valid-type]
        obj = await get_or_404(crud, session, item_id)
        return await crud.update(session, obj, item_in)

    @router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
    async def delete_item(item_id: int, session: SessionDep):
        obj = await get_or_404(crud, session, item_id)
        await crud.delete(session, obj)

    return router
