from app.api.v1.router_factory import build_crud_router
from app.crud import user_crud
from app.schemas import UserCreate, UserRead, UserUpdate

router = build_crud_router(
    crud=user_crud,
    create_schema=UserCreate,
    update_schema=UserUpdate,
    read_schema=UserRead,
    resource_name="user",
)
