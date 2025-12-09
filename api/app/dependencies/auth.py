"""
Authentication dependencies for FastAPI
"""
from fastapi import Header, HTTPException, status
from typing import Optional
import json
import base64

from ..core import settings
from ..models.auth import UserInfo


async def get_current_user(
    authorization: Optional[str] = Header(None)
) -> UserInfo:
    """
    Dependency to get current authenticated user

    Args:
        authorization: Authorization header with Bearer token

    Returns:
        UserInfo of the authenticated user

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

    # Decode JWT without validation (just extract payload)
    try:
        # JWT format: header.payload.signature
        payload_part = token.split('.')[1]

        # Add padding if needed
        padding = 4 - (len(payload_part) % 4)
        if padding != 4:
            payload_part += '=' * padding

        # Decode base64
        payload_bytes = base64.urlsafe_b64decode(payload_part)
        payload = json.loads(payload_bytes)

        # Extract user info from payload
        user_id = payload.get("id") or payload.get("userId") or payload.get("sub", 0)
        user_name = payload.get("nombre") or payload.get("name") or payload.get("username", "unknown")

        # Try to parse user_id as int
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            user_id = 0

        return UserInfo(
            id=user_id,
            nombre=user_name,
            sistema_id=settings.SGI_SISTEMA_ID,
            compagnia_id=settings.SGI_COMPAGNIA_ID
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
