from slugify import slugify

from app.crud import BaseCrud
from app.models import Product
from app.schemas import ProductCreate, ProductUpdate


class ProductCrud(BaseCrud[Product, ProductCreate, ProductUpdate]):
    def _prepare_create_data(self, obj_in: ProductCreate) -> dict:
        data = obj_in.model_dump()
        if not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data

    def _prepare_update_data(self, obj_in: ProductUpdate) -> dict:
        data = obj_in.model_dump(exclude_unset=True)
        if "name" in data and not data.get("slug"):
            data["slug"] = slugify(data["name"])
        return data


product_crud = ProductCrud(Product)
