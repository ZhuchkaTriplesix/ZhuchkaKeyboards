from pydantic import BaseModel, Field


class Auth(BaseModel):
    username: str


class AuthSchema(Auth):
    password: str = Field(..., min_length=6)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: float


class LoginRequest(BaseModel):
    username: str
    password: str
