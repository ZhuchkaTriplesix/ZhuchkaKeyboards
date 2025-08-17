from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator


def init_app(app: FastAPI):
    """Initialize Prometheus metrics for FastAPI app"""
    instrumentator = Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        should_respect_env_var=True,
        should_instrument_requests_inprogress=True,
        excluded_handlers=["/metrics"],
    )
    
    instrumentator.instrument(app)
    instrumentator.expose(app, endpoint="/metrics")
