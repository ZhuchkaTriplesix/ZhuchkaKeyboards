from typing import Dict

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies import VUser
from src.redis.redis import RedisController
from src.routers.user.dal import UserDAL
from src.routers.user.schemas import SignUp, UserToken, VerifyEmail, ChangePassword, ResetPasswordRequest, \
    ResetPasswordForm
from src.security.hashing import Hasher
from src.security.security import Security
from src.services.email import EmailService

logger = get_logger(__name__)


async def _sign_up(body: SignUp, session: AsyncSession) -> Dict:
    user_dal = UserDAL(session=session)
    email_exist = await user_dal.get_user_by_email(email=body.email)
    phone_number_exists = await user_dal.get_user_by_phone_number(phone_number=body.phone_number)
    if email_exist:
        raise HTTPException(
            status_code=401,
            detail="Email is already exists."
        )

    if phone_number_exists:
        raise HTTPException(
            status_code=401,
            detail="Phone number is already exists."
        )

    user = await user_dal.create_user(
        email=body.email,
        password=Hasher().get_password_hash(body.password),
        phone_number=body.phone_number
    )

    if not user:
        raise HTTPException(
            status_code=500,
            detail="Something get wrong."
        )

    await EmailService().send_verify_token(user=user)

    return {"message": "Successfully registration."}


async def _sign_in(email: str, password: str, session: AsyncSession) -> UserToken:
    if email is None or password is None:
        raise HTTPException(
            status_code=401,
            detail="Email and password are required."
        )
    user = await UserDAL(session=session).get_user_by_email(email=email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Email not found."
        )
    if not user.is_verify:
        await EmailService().send_verify_token(user=user)
        raise HTTPException(
            status_code=402,
            detail="User has not verified yet."
        )
    if not Hasher().verify_password(plain_password=password, hashed_password=user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password."
        )
    session_id = await Security().create_session(user_id=user.id, email=user.email, permission="user")
    return UserToken(session_id=session_id)


async def _verify_email(body: VerifyEmail, session: AsyncSession) -> Dict:
    email = await RedisController().get_record(tag="email", key=body.token)
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Token is invalid or expired."
        )
    await UserDAL(session=session).verify_email(email=email)
    await RedisController().del_record(tag="email", key=body.token)
    return {"message": "Successfully verify."}


async def _change_password(body: ChangePassword, user: VUser, session: AsyncSession) -> Dict:
    if body.current_password == "" or body.new_password == "" or body.new_password_secondary == "":
        raise HTTPException(
            status_code=405,
            detail="Empty password.",
        )
    if body.new_password != body.new_password_secondary:
        raise HTTPException(
            status_code=403,
            detail="Incorrect new password.",
        )

    user_dal = UserDAL(session=session)

    c_user = await user_dal.get_user_by_email(email=user.email)

    if not Hasher().verify_password(plain_password=body.current_password, hashed_password=c_user.password):
        raise HTTPException(
            status_code=402,
            detail="Incorrect password.",
        )

    await user_dal.update_user_password(email=c_user.email, password=Hasher().get_password_hash(body.new_password))

    return {"message": "Successfully change password."}


async def _reset_password_request(body: ResetPasswordRequest, session: AsyncSession) -> Dict:
    user = await UserDAL(session=session).get_user_by_email(email=body.email)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found."
        )
    await EmailService().send_password_recovery_token(user=user)
    return {"message": "Reset link sent."}


async def _reset_password(body: ResetPasswordForm, session: AsyncSession) -> Dict:
    email = await RedisController().get_record(tag="pw", key=body.token)
    if not email:
        raise HTTPException(
            status_code=404,
            detail="Token is invalid or expired."
        )
    if body.new_password == "":
        raise HTTPException(
            status_code=403,
            detail="Password is empty."
        )
    await UserDAL(session=session).update_user_password(email=email, password=Hasher().get_password_hash(body.new_password))
    await RedisController().del_record(tag="pw", key=body.token)
    return {"message": "Successfully change password."}