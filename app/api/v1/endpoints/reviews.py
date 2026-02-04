from app.api.v1.router_factory import build_crud_router
from app.crud import review_crud
from app.schemas import ReviewCreate, ReviewRead, ReviewUpdate

router = build_crud_router(
    crud=review_crud,
    create_schema=ReviewCreate,
    update_schema=ReviewUpdate,
    read_schema=ReviewRead,
    resource_name="review",
)
