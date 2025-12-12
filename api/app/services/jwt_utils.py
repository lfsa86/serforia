"""
JWT utilities for stateless authentication
Creates and validates JWT tokens with embedded user info
"""
import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any

from ..core import settings
from ..models.auth import UserInfo


def create_token(user_info: UserInfo) -> str:
    """
    Create a JWT token with embedded user information

    Args:
        user_info: User information to embed in token

    Returns:
        JWT token string
    """
    payload = {
        "user_id": user_info.id,
        "nombre": user_info.nombre,
        "sistema_id": user_info.sistema_id,
        "compagnia_id": user_info.compagnia_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=settings.JWT_EXPIRATION_HOURS),
        "iat": datetime.now(timezone.utc)
    }

    return jwt.encode(
        payload,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def decode_token(token: str) -> Optional[UserInfo]:
    """
    Decode and validate a JWT token

    Args:
        token: JWT token string

    Returns:
        UserInfo if token is valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        return UserInfo(
            id=payload["user_id"],
            nombre=payload["nombre"],
            sistema_id=payload["sistema_id"],
            compagnia_id=payload["compagnia_id"]
        )

    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def get_token_payload(token: str) -> Optional[Dict[str, Any]]:
    """
    Get raw payload from token (for debugging)

    Args:
        token: JWT token string

    Returns:
        Token payload dict if valid, None otherwise
    """
    try:
        return jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
    except jwt.InvalidTokenError:
        return None
