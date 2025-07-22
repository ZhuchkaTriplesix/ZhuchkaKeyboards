from typing import Dict, Any, Type, Union
from pydantic import BaseModel
from fastapi import status
from utils.responses_schemas import *


def api_responses(
        success_model: Type[BaseModel] = None,
        *extra_responses: Dict[int, Union[Dict[str, Any], Type[BaseModel]]]) -> Dict[int, Dict[str, Any]]:
    responses = {
        status.HTTP_400_BAD_REQUEST: {
            "description": "Bad Request",
            "model": BadRequestError
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized",
            "model": UnauthorizedError
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden",
            "model": ForbiddenError
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Not Found",
            "model": NotFoundError
        },
        status.HTTP_429_TOO_MANY_REQUESTS: {
            "description": "Too Many Requests",
            "model": TooManyRequestsError
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Internal Error",
            "model": InternalError
        }
    }

    if success_model:
        responses[200] = {
            "description": "Successful Response",
            "model": success_model
        }

    for item in extra_responses:
        for code, content in item.items():
            if isinstance(content, type) and issubclass(content, BaseModel):
                responses[code] = {"description": content.__name__, "model": content}
            else:
                responses[code] = content

    return responses
