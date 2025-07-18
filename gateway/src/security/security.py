from datetime import datetime, timedelta
import jwt
from jwt import PyJWTError
from passlib.context import CryptContext
from fastapi import HTTPException, status
from typing import Optional
from services.redis.rediska import redis_manager
from config import jwt_cfg
from utils.logger import get_logger

logger = get_logger(__name__)

ACCESS_TOKEN_EXPIRE_MINUTES = jwt_cfg.jwt_exp

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, jwt_cfg.jwt_secret, algorithm=jwt_cfg.jwt_algorithm)
    return encoded_jwt


def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token invalid or expired",
    )
    logger.info(f"verify_token: received token: {token}")
    try:
        payload = jwt.decode(token, jwt_cfg.jwt_secret, algorithms=[jwt_cfg.jwt_algorithm])
        logger.info(f"verify_token: decoded payload: {payload}")
        username: str = payload.get("sub")
        logger.info(f"verify_token: username from payload: {username}")
        if username is None:
            logger.warning("verify_token: username is None in payload")
            raise credentials_exception

        redis_token = redis_manager.get_token(username)
        logger.info(f"verify_token: token from redis for user {username}: {redis_token}")
        if redis_token != token:
            logger.warning(f"verify_token: token mismatch! token from redis: {redis_token}, token from cookie: {token}")

        if not redis_manager.token_exists(username, token):
            logger.warning(f"verify_token: token does not exist in redis for user {username}")
            raise credentials_exception

        return username
    except PyJWTError as e:
        logger.warning(f"verify_token: PyJWTError: {e}")
        raise credentials_exception