"""Main FastAPI application - Stateless and Scalable YOLOX API"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.core.config import get_settings
from app.core.model_manager import get_model_manager
from app.api.routes import health, detection, metrics
from app import __version__


# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager

    Handles startup and shutdown events for the API service.
    - Startup: Load model into memory
    - Shutdown: Cleanup resources
    """
    # Startup
    settings = get_settings()
    logger.info(f"Starting {settings.api_title} v{__version__}")
    logger.info(f"Device: {settings.device}")
    logger.info(f"Model: {settings.model_name}")

    # Load model
    try:
        model_manager = get_model_manager()
        model_manager.load_model(
            model_path=settings.model_path,
            device=settings.device
        )
        logger.info("✓ Model loaded successfully")
    except Exception as e:
        logger.error(f"✗ Failed to load model: {e}")
        logger.warning("API starting without model - health checks will fail")

    yield

    # Shutdown
    logger.info("Shutting down API service")


# Create FastAPI application
app = FastAPI(
    title=get_settings().api_title,
    description=get_settings().api_description,
    version=__version__,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1")
app.include_router(detection.router, prefix="/api/v1")
app.include_router(metrics.router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint

    Returns basic API information and links to documentation.
    """
    return {
        "service": "YOLOX Object Detection API",
        "version": __version__,
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=False,  # Set to True for development
        workers=1  # Use workers > 1 in production with gunicorn
    )
