"""
Authentication routes for the API
"""
from fastapi import APIRouter, HTTPException, Request
import logging

from ..models.auth import LoginRequest, LoginResponse
from ..services.auth_service import get_auth_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, req: Request):
    """
    Authenticate user against SGI Seguridad

    Args:
        request: LoginRequest with usuario and password
        req: FastAPI Request object to extract client IP

    Returns:
        LoginResponse with token and user info if successful
    """
    try:
        # Get client IP
        client_ip = req.client.host if req.client else "unknown"

        # Authenticate
        auth_service = get_auth_service()
        result = await auth_service.login(
            usuario=request.usuario,
            password=request.password,
            client_ip=client_ip
        )

        return result

    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )
