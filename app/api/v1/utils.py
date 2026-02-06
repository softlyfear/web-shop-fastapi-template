"""API utility functions."""

from fastapi import HTTPException, status


async def get_or_404(crud, session, obj_id):
    """Get object or raise 404."""
    obj = await crud.get(session, obj_id)
    if obj is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return obj
