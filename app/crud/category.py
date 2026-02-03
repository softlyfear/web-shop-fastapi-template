from slugify import slugify

from app.crud import BaseCrud
from app.models import Category
from app.schemas import CategoryCreate, CategoryUpdate


class CategoryCrud(BaseCrud[Category, CategoryCreate, CategoryUpdate]):
    def _prepare_create_data(self, obj_in: CategoryCreate) -> dict:
        data = obj_in.model_dump()
        if not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    def _prepare_update_data(self, obj_in: CategoryUpdate) -> dict:
        data = obj_in.model_dump(exclude_unset=True)
        if "name" in data and not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data


category_crud = CategoryCrud(Category)
