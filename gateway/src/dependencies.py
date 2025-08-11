from fastapi import Request, HTTPException, status
from security.security import verify_token
from typing import Annotated
from fastapi import Depends
from main_schemas import User


def get_current_user(request: Request):
    token = request.cookies.get("session_id")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated"
        )
    return verify_token(token)


VUser = Annotated[User, Depends(get_current_user)]
