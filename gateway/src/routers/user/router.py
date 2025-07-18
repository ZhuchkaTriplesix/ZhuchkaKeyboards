from datetime import timedelta
from fastapi import APIRouter
from fastapi import Depends, status, Response, HTTPException
from .schemas import *
from utils.resonses import api_responses
from utils.logger import get_logger
from config import jwt_cfg
from security.security import create_access_token
from services.redis.rediska import redis_manager

router = APIRouter()

# Инициализируем логгер
logger = get_logger(__name__)


