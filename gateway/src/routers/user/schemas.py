from typing import Optional
from pydantic import BaseModel, EmailStr
from pydantic_config import default_config


class SignUp(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

    model_config = default_config


class UserToken(BaseModel):
    session_id: str

    model_config = default_config


class VerifyEmail(BaseModel):
    token: str

    model_config = default_config


class ChangePassword(BaseModel):
    old_password: str
    new_password: str

    model_config = default_config


class ResetPasswordRequest(BaseModel):
    email: EmailStr

    model_config = default_config


class ResetPasswordForm(BaseModel):
    token: str
    new_password: str

    model_config = default_config
