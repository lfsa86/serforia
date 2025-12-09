"""
Pydantic models for authentication
"""
from pydantic import BaseModel, Field
from typing import Optional


class LoginRequest(BaseModel):
    """Request model for login"""
    usuario: str = Field(..., min_length=1, description="Username")
    password: str = Field(..., min_length=1, description="Password in plain text")


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
