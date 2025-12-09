"""
Main FastAPI application
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .core import settings
from .routes import query_router, auth_router

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Create FastAPI app
app = FastAPI(
    title="SERFOR API",
    description="Sistema inteligente para consultas sobre datos forestales del Perú",
    version="1.0.0",
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
