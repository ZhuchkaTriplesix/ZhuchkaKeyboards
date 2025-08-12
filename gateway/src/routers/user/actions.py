from typing import Dict

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies import VUser
from services.redis.rediska import redis_manager
from routers.user.dal import UserDAL
from routers.user.schemas import (
    SignUp,
    UserToken,
    VerifyEmail,
    ChangePassword,
    ResetPasswordRequest,
    ResetPasswordForm,
)
from security.hashing import Hasher
from utils.logger import get_logger

logger = get_logger(__name__)


async def _sign_up(body: SignUp, session: AsyncSession) -> Dict:
    user_dal = UserDAL(session=session)
    email_exist = await user_dal.get_user_by_email(email=body.email)
    phone_number_exists = await user_dal.get_user_by_phone_number(
        phone_number=body.phone_number
    )
    if email_exist:
        raise HTTPException(status_code=401, detail="Email is already exists.")

    if phone_number_exists:
        raise HTTPException(status_code=401, detail="Phone number is already exists.")

    user = await user_dal.create_user(
        email=body.email,
        password=Hasher().get_password_hash(body.password),
        phone_number=body.phone_number,
    )

    if not user:
        raise HTTPException(status_code=500, detail="Something get wrong.")

    # TODO: Implement email service
    # await EmailService().send_verify_token(user=user)

    return {"message": "Successfully registration."}


async def _sign_in(email: str, password: str, session: AsyncSession) -> UserToken:
    user_dal = UserDAL(session=session)
    user = await user_dal.get_user_by_email(email=email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    if not Hasher().verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Invalid password.")

    if not user.is_verify:
        # TODO: Implement email service
        # await EmailService().send_verify_token(user=user)
        raise HTTPException(status_code=402, detail="Email not verified.")

    # TODO: Implement session creation
    # session = Security().create_session(user=user)
    # return session

    return UserToken(session_id="temp_session_id")


async def _verify_email(body: VerifyEmail, session: AsyncSession) -> Dict:
    email = await redis_manager.get_record(tag="email", key=body.token)
    if not email:
        raise HTTPException(status_code=401, detail="Token is invalid or expired.")
    await UserDAL(session=session).verify_email(email=email)
    await redis_manager.del_record(tag="email", key=body.token)
    return {"message": "Successfully verify."}


async def _change_password(
    body: ChangePassword, session: AsyncSession, user: VUser
) -> Dict:
    user_dal = UserDAL(session=session)
    user_obj = await user_dal.get_user_by_email(email=user.email)
    if not user_obj:
        raise HTTPException(status_code=404, detail="User not found.")

    if not Hasher().verify_password(body.old_password, user_obj.password):
        raise HTTPException(status_code=401, detail="Invalid old password.")

    await user_dal.update_user_password(
        email=user.email, password=Hasher().get_password_hash(body.new_password)
    )
    return {"message": "Successfully change password."}


async def _reset_password_request(
    body: ResetPasswordRequest, session: AsyncSession
) -> Dict:
    user_dal = UserDAL(session=session)
    user = await user_dal.get_user_by_email(email=body.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # TODO: Implement email service
    # await EmailService().send_reset_token(user=user)

    return {"message": "Reset password token sent."}


async def _reset_password(body: ResetPasswordForm, session: AsyncSession) -> Dict:
    email = await redis_manager.get_record(tag="pw", key=body.token)
    if not email:
        raise HTTPException(status_code=404, detail="Token is invalid or expired.")
    if body.new_password == "":
        raise HTTPException(status_code=403, detail="Password is empty.")
    await UserDAL(session=session).update_user_password(
        email=email, password=Hasher().get_password_hash(body.new_password)
    )
    await redis_manager.del_record(tag="pw", key=body.token)
    return {"message": "Successfully change password."}
