"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from .core import settings
from .routes import query_router

# Load environment variables
load_dotenv()

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
    print("🚀 SERFOR API starting up...")
    print(f"📊 Database: {settings.DB_SERVER}")
    print(f"🌐 CORS Origins: {settings.cors_origins_list}")


@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    print("👋 SERFOR API shutting down...")
