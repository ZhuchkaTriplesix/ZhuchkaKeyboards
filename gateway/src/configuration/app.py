from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from routers import Router
from utils.logger import get_logger
from utils.responses import ORJSONResponse
from middleware import apply_middleware_stack

# print("DEBUG: About to import prometheus_metrics...")
# from services.metrics import prometheus_metrics
# print("DEBUG: prometheus_metrics imported successfully")

# Инициализируем логгер
logger = get_logger(__name__)


class App:
    def __init__(self):
        self._app: FastAPI = FastAPI(
            title="Gateway API",
            description="Gateway API for ZhuchkaKeyboards",
            docs_url=None,
            redoc_url=None,
            openapi_url="/api/openapi.json",
            # Настройки для использования orjson
            default_response_class=ORJSONResponse,
        )
        
        # Настройка CORS middleware
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["GET", "POST", "DELETE", "PATCH"],
            allow_headers=["*"],
        )
        
        # Применяем централизованный стек middleware
        logger.info("Applying middleware stack...")
        apply_middleware_stack(self._app)
        logger.info("Middleware stack applied successfully")

        # Initialize Prometheus metrics - DISABLED для избежания дублирования
        # try:
        #     print("DEBUG: Initializing Prometheus metrics...")
        #     prometheus_metrics.init_app(self._app)
        #     print("DEBUG: Prometheus metrics initialized successfully")
        # except Exception as e:
        #     print(f"DEBUG: Error initializing Prometheus metrics: {e}")
        #     import traceback
        #     traceback.print_exc()

        self._register_routers()

    def _register_routers(self) -> None:
        for router, prefix, tags in Router.routers:
            self._app.include_router(router=router, prefix=prefix, tags=tags)

    @property
    def app(self) -> FastAPI:
        return self._app
