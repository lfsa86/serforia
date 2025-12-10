"""
Authentication service for SGI Seguridad integration
"""
import hashlib
import logging
import httpx
from typing import Optional

from ..core import settings
from ..models.auth import LoginResponse, UserInfo

logger = logging.getLogger(__name__)


def hash_md5(password: str) -> str:
    """
    Hash password to MD5

    Args:
        password: Plain text password

    Returns:
        MD5 hash in lowercase
    """
    return hashlib.md5(password.encode()).hexdigest().lower()


class AuthService:
    """Service for authentication operations"""

    def __init__(self):
        self.base_url = settings.SGI_BASE_URL
        self.sistema_id = settings.SGI_SISTEMA_ID
        self.compagnia_id = settings.SGI_COMPAGNIA_ID
        self.dev_mode = settings.AUTH_DEV_MODE
        self.dev_user = settings.AUTH_DEV_USER
        self.dev_password = settings.AUTH_DEV_PASSWORD
        self.fallback_on_error = settings.AUTH_FALLBACK_ON_ERROR

    async def login(self, usuario: str, password: str, client_ip: str = "unknown") -> LoginResponse:
        """
        Authenticate user against SGI Seguridad or dev mode

        Args:
            usuario: Username
            password: Plain text password
            client_ip: Client IP address for logging

        Returns:
            LoginResponse with authentication result
        """
        # Dev mode bypass
        if self.dev_mode:
            return self._dev_mode_login(usuario, password, client_ip)

        # Production SGI login
        try:
            return await self._sgi_login(usuario, password, client_ip)
        except Exception as e:
            logger.error(
                f"SGI login error | usuario={usuario} | ip={client_ip} | error={str(e)}",
                exc_info=True
            )

            # Fallback to dev mode if enabled
            if self.fallback_on_error:
                logger.warning(
                    f"Using fallback auth | usuario={usuario} | ip={client_ip}"
                )
                return self._dev_mode_login(usuario, password, client_ip)

            return LoginResponse(
                success=False,
                error="Error de autenticación. Por favor, intente nuevamente."
            )

    def _dev_mode_login(self, usuario: str, password: str, client_ip: str) -> LoginResponse:
        """
        Dev mode authentication

        Args:
            usuario: Username
            password: Plain text password
            client_ip: Client IP address

        Returns:
            LoginResponse with mock authentication
        """
        if usuario == self.dev_user and password == self.dev_password:
            logger.info(
                f"DEV login success | usuario={usuario} | ip={client_ip}"
            )
            return LoginResponse(
                success=True,
                token="dev_mock_token_12345",
                user=UserInfo(
                    id=999,
                    nombre=usuario,
                    sistema_id=self.sistema_id,
                    compagnia_id=self.compagnia_id
                )
            )
        else:
            logger.warning(
                f"DEV login failed | usuario={usuario} | ip={client_ip}"
            )
            return LoginResponse(
                success=False,
                error="Credenciales inválidas"
            )

    async def _sgi_login(self, usuario: str, password: str, client_ip: str) -> LoginResponse:
        """
        SGI Seguridad authentication

        Args:
            usuario: Username
            password: Plain text password
            client_ip: Client IP address

        Returns:
            LoginResponse with SGI authentication result
        """
        # Hash password to MD5
        password_hash = hash_md5(password)

        # Prepare request
        url = f"{self.base_url}/auth/login"
        payload = {
            "nombre": usuario,
            "password": password_hash,
            "sistema": {"id": self.sistema_id},
            "compagnia": {"id": self.compagnia_id}
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)

            if response.status_code == 200:
                # SGI devuelve 200 con body vacío cuando las credenciales son inválidas
                response_text = response.text.strip()
                if not response_text:
                    logger.warning(
                        f"SGI login empty response | usuario={usuario} | ip={client_ip}"
                    )
                    return LoginResponse(
                        success=False,
                        error="Credenciales inválidas"
                    )

                try:
                    data = response.json()
                except Exception:
                    logger.warning(
                        f"SGI login invalid JSON | usuario={usuario} | ip={client_ip}"
                    )
                    return LoginResponse(
                        success=False,
                        error="Credenciales inválidas"
                    )

                # Extract user info
                user_data = data.get("usuario", {})
                token = data.get("token", "")

                if not token:
                    logger.warning(
                        f"SGI login no token | usuario={usuario} | ip={client_ip}"
                    )
                    return LoginResponse(
                        success=False,
                        error="Respuesta de autenticación inválida"
                    )

                user_info = UserInfo(
                    id=user_data.get("id", 0),
                    nombre=user_data.get("nombre", usuario),
                    sistema_id=self.sistema_id,
                    compagnia_id=self.compagnia_id
                )

                logger.info(
                    f"SGI login success | usuario={usuario} | user_id={user_info.id} | ip={client_ip}"
                )

                return LoginResponse(
                    success=True,
                    token=token,
                    user=user_info
                )
            else:
                logger.warning(
                    f"SGI login failed | usuario={usuario} | status={response.status_code} | ip={client_ip}"
                )
                return LoginResponse(
                    success=False,
                    error="Credenciales inválidas o servicio no disponible"
                )


_auth_service: Optional[AuthService] = None


def get_auth_service() -> AuthService:
    """
    Get singleton instance of AuthService

    Returns:
        AuthService instance
    """
    global _auth_service
    if _auth_service is None:
        _auth_service = AuthService()
    return _auth_service
