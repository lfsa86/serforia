"""
Pydantic models for authentication
"""
import re
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class LoginRequest(BaseModel):
    """Request model for login"""
    usuario: str = Field(
        ...,
        min_length=1,
        max_length=50,
        pattern=r'^[\w.\-@]+$',
        description="Username (alphanumeric, dots, hyphens, underscores, @)"
    )
    password: str = Field(
        ...,
        min_length=1,
        max_length=128,
        pattern=r'^[\x20-\x7E]+$',
        description="Password (printable ASCII characters)"
    )

    @field_validator('usuario')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Validate username contains only allowed characters"""
        # Permitir alfanuméricos, guiones, puntos, guion bajo y arroba
        if not re.match(r'^[\w.\-@]+$', v):
            raise ValueError("El usuario contiene caracteres no permitidos")
        return v.strip()


class UserInfo(BaseModel):
    """User information model"""
    id: int
    nombre: str
    sistema_id: int
    compagnia_id: int


class LoginResponse(BaseModel):
    """Response model for login"""
    success: bool
    token: Optional[str] = None
    user: Optional[UserInfo] = None
    error: Optional[str] = None
