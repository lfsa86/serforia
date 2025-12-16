"""
Main FastAPI application
"""
import logging
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from dotenv import load_dotenv

from .core import settings
from .routes import query_router, auth_router
from .services.auth_service import get_auth_service

# HTTP Basic Auth for /docs protection
security = HTTPBasic()


async def verify_docs_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    """
    Validate docs access using SGI credentials (same as app login).
    The browser popup captures credentials and validates against SGI.
    """
    auth_service = get_auth_service()
    result = await auth_service.login(
        usuario=credentials.username,
        password=credentials.password,
        client_ip="docs-access"
    )
    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Create FastAPI app (disable default docs to serve locally)
app = FastAPI(
    title="SERFOR API",
    description="Sistema inteligente para consultas sobre datos forestales del Perú",
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
)

# Mount static files for Swagger UI assets
static_path = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=static_path), name="static")


@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html(username: str = Depends(verify_docs_credentials)):
    """Serve Swagger UI with local assets (no CDN dependency). Protected by HTTP Basic Auth."""
    return get_swagger_ui_html(
        openapi_url="/openapi.json",
        title="SERFOR API - Docs",
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get("/openapi.json", include_in_schema=False)
async def get_openapi_endpoint(username: str = Depends(verify_docs_credentials)):
    """Serve OpenAPI schema. Protected by HTTP Basic Auth."""
    return get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/auth", tags=["authentication"])
app.include_router(query_router, prefix="/api", tags=["queries"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "SERFOR API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    logger = logging.getLogger(__name__)
    logger.info("SERFOR API starting up...")
    logger.info(f"Database: {settings.DB_SERVER}")
    logger.info(f"CORS Origins: {settings.cors_origins_list}")
    logger.info(f"Auth Mode: {'DEV (bypass)' if settings.AUTH_DEV_MODE else 'SGI Seguridad'}")
    logger.info(f"SGI URL: {settings.SGI_BASE_URL}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger = logging.getLogger(__name__)
    logger.info("SERFOR API shutting down...")
