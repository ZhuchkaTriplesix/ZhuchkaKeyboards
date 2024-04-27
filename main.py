from fastapi import FastAPI
from fastapi.routing import APIRoute
from sqlalchemy import text

from api.api import api_router
from core.config import settings
from db.session import db_session


def custom_generate_unique_id(route: APIRoute):
    return f"{route.tags[0]}-{route.name}"


db_session.execute(text("SELECT 1"))


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    generate_unique_id_function=custom_generate_unique_id,
)

app.include_router(api_router, prefix=settings.API_V1_STR)
