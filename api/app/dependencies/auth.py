"""
Authentication dependencies for FastAPI
"""
from fastapi import Header, HTTPException, status
from typing import Optional

from ..core import settings
from ..models.auth import UserInfo
from ..services.jwt_utils import decode_token


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> UserInfo:
    """
    Dependency to get current authenticated user from JWT token

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        UserInfo of the authenticated user (decoded from JWT)

    Raises:
        HTTPException: If authentication fails
    """
    # Dev mode bypass
    if settings.AUTH_DEV_MODE:
        return UserInfo(
            id=999,
            nombre=settings.AUTH_DEV_USER,
            sistema_id=settings.SGI_SISTEMA_ID,
            compagnia_id=settings.SGI_COMPAGNIA_ID
        )

    # Check authorization header
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionó token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Extract token
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Formato de token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = parts[1]

    # Decode JWT to get user info (stateless)
    user_info = decode_token(token)

    if user_info:
        return user_info

    # Token invalid or expired
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sesión expirada o inválida. Por favor, inicie sesión nuevamente.",
        headers={"WWW-Authenticate": "Bearer"},
    )
