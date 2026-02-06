"""Authentication Pydantic schemas."""

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Schema for login request."""

    username: str
    password: str


class TokenInfo(BaseModel):
    """Schema for token response."""

    access_token: str
    token_type: str


class TokenPair(BaseModel):
    """Schema for access and refresh token pair."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    """Schema for token refresh request."""

    refresh_token: str


class PasswordUpdate(BaseModel):
    """Schema for password update."""

    current_password: str
    new_password: str
