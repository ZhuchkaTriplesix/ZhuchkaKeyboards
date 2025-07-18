from fastapi import Request, HTTPException, status
from security.security import verify_token

def get_current_user(request: Request):
    token = request.cookies.get('access_token')
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Not authenticated')
    return verify_token(token)
