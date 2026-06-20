import secrets

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from app.config import settings


security = HTTPBasic(auto_error=False)


def verify_basic_auth(
    credentials: HTTPBasicCredentials | None = Depends(security),
):
    if not settings.require_auth:
        return None

    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Basic"},
        )

    correct_username = secrets.compare_digest(
        credentials.username,
        settings.api_username,
    )
    correct_password = secrets.compare_digest(
        credentials.password,
        settings.api_password,
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username