from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def register_exception_handlers(app):
    @app.exception_handler(IntegrityError)
    async def integrity_handler(request, exc):
        return JSONResponse(
            status_code=409, content={"detail": "IntegrityError conflict"}
        )
