from pydantic import BaseModel, EmailStr


class SignUp(BaseModel):
    email: EmailStr
    password: str
    phone_number: str


class UserToken(BaseModel):
    session_id: str


class VerifyEmail(BaseModel):
    token: str


class ChangePassword(BaseModel):
    old_password: str
    new_password: str


class ResetPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordForm(BaseModel):
    token: str
    new_password: str
