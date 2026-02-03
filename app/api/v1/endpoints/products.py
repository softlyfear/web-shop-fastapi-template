from app.api.v1.router_factory import build_crud_router
from app.crud import product_crud
from app.schemas import ProductCreate, ProductRead, ProductUpdate

router = build_crud_router(
    crud=product_crud,
    create_schema=ProductCreate,
    update_schema=ProductUpdate,
    read_schema=ProductRead,
)
