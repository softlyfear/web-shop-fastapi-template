from app.api.v1.router_factory import build_crud_router
from app.crud import category_crud
from app.schemas import CategoryCreate, CategoryRead, CategoryUpdate

router = build_crud_router(
    crud=category_crud,
    create_schema=CategoryCreate,
    update_schema=CategoryUpdate,
    read_schema=CategoryRead,
)
