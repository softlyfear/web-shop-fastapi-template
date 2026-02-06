from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import DeclarativeBase


class BaseCrud[
    ModelType: DeclarativeBase,
    CreateSchemaType: BaseModel,
    UpdateSchemaType: BaseModel,
]:
    """Абстрактный базовый класс для CRUD-операций с БД."""

    def __init__(self, model: type[ModelType]) -> None:
        self.model = model

    def _prepare_create_data(self, obj_in: CreateSchemaType) -> dict:
        return obj_in.model_dump()

    def _prepare_update_data(self, obj_in: UpdateSchemaType) -> dict:
        return obj_in.model_dump(exclude_unset=True)

    async def _commit_refresh(
        self,
        session: AsyncSession,
        obj: ModelType,
    ) -> ModelType:
        try:
            await session.commit()
            await session.refresh(obj)
            return obj
        except IntegrityError:
            await session.rollback()
            raise

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
    ) -> ModelType:
        data = self._prepare_create_data(obj_in)
        obj = self.model(**data)
        session.add(obj)
        return await self._commit_refresh(session, obj)

    async def get(
        self,
        session: AsyncSession,
        obj_id: int,
    ) -> ModelType | None:
        return await session.get(self.model, obj_id)

    async def get_multi(
        self,
        session: AsyncSession,
        offset: int = 0,
        limit: int = 25,
    ) -> list[ModelType]:
        stmt = select(self.model).order_by(self.model.id).offset(offset).limit(limit)
        result = await session.execute(stmt)
        return list(result.scalars().all())

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
    ) -> ModelType:
        data = self._prepare_update_data(obj_in)
        for field, value in data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
            else:
                logger.warning(
                    f"Поле {field} не существует в модели {self.model.__name__}"
                )
        return await self._commit_refresh(session, db_obj)

    async def delete(
        self,
        session: AsyncSession,
        db_obj: ModelType,
    ) -> None:
        await session.delete(db_obj)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise
