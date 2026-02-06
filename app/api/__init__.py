"""API package."""

from app.api.v1.api import router_v1
from app.api.v1.router_factory import build_crud_router
from app.api.v1.utils import get_or_404

__all__ = [
    "router_v1",
    "get_or_404",
    "build_crud_router",
]
