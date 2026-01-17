from fastapi import APIRouter
from app.web import catalog

router = APIRouter()

router.include_router(catalog.router, tags=["catalog"])
