from typing import Dict

from fastapi import APIRouter, Depends, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.dependencies import DbSession
from src.dependencies import VUser
from src.routers.user.actions import _sign_up, _sign_in, _verify_email, _change_password, _reset_password_request, \
    _reset_password
from src.routers.user.schemas import *

router = APIRouter()


@router.post("/sign-in")
async def sign_in(response: Response, session: DbSession, form_data: OAuth2PasswordRequestForm = Depends()):
    session = await _sign_in(email=form_data.username, password=form_data.password, session=session)
    response.set_cookie(key="session_id", value=session.session_id, httponly=True, secure=True, samesite='lax')
    return {"message": "Successfully signed in"}


@router.post("/sign-up")
async def sign_up(body: SignUp, session: DbSession) -> Dict:
    return await _sign_up(body=body, session=session)


@router.patch("/verify")
async def verify_email(body: VerifyEmail, session: DbSession) -> Dict:
    return await _verify_email(body, session)


@router.patch("/password/change")
async def change_password(body: ChangePassword, user: VUser, session: DbSession) -> Dict:
    return await _change_password(body=body, user=user, session=session)


@router.post("/password/reset/request")
async def reset_password_request(body: ResetPasswordRequest, session: DbSession) -> Dict:
    return await _reset_password_request(body=body, session=session)


@router.post("/password/reset/confirm")
async def reset_password(body: ResetPasswordForm, session: DbSession) -> Dict:
    return await _reset_password(body=body, session=session)