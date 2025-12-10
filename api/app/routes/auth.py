"""
Authentication routes for the API
"""
from fastapi import APIRouter, HTTPException, Request
import logging

from ..models.auth import LoginRequest, LoginResponse
from ..services.auth_service import get_auth_service
from ..services.wazuh_logger import get_wazuh_logger
from ..core import settings

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
    wazuh = get_wazuh_logger()
    client_ip = req.client.host if req.client else "unknown"
    auth_mode = "DEV" if settings.AUTH_DEV_MODE else "SGI"

    try:
        # Authenticate
        auth_service = get_auth_service()
        result = await auth_service.login(
            usuario=request.usuario,
            password=request.password,
            client_ip=client_ip
        )

        # Log to WAZUH
        wazuh.log_login(
            user_id=result.user.id if result.user else None,
            user_name=request.usuario,
            source_ip=client_ip,
            success=result.success,
            http_status=200 if result.success else 401,
            error_message=result.error,
            auth_mode=auth_mode
        )

        return result

    except Exception as e:
        logger.error(f"Login endpoint error: {str(e)}", exc_info=True)

        # Log error to WAZUH
        wazuh.log_login(
            user_id=None,
            user_name=request.usuario,
            source_ip=client_ip,
            success=False,
            http_status=500,
            error_message=str(e),
            auth_mode=auth_mode
        )

        raise HTTPException(
            status_code=500,
            detail="Error interno del servidor"
        )
