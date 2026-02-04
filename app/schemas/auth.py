from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenInfo(BaseModel):
    access_token: str
    token_type: str


class TokenPair(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str
