"""Health check endpoints"""
from fastapi import APIRouter
from app.schemas.detection import HealthResponse
from app.core.model_manager import get_model_manager
from app import __version__

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint

    Returns service status and model readiness.
    Use this for Kubernetes liveness/readiness probes.
    """
    model_manager = get_model_manager()

    return HealthResponse(
        status="healthy" if model_manager.is_ready() else "initializing",
        model_loaded=model_manager.is_ready(),
        device=str(model_manager.get_device()) if model_manager.is_ready() else "none",
        version=__version__
    )


@router.get("/ready", tags=["Health"])
async def readiness_check():
    """Readiness check endpoint

    Returns 200 if service is ready to accept traffic, 503 otherwise.
    """
    model_manager = get_model_manager()

    if model_manager.is_ready():
        return {"status": "ready"}
    else:
        from fastapi import Response
        return Response(
            content='{"status": "not ready"}',
            status_code=503,
            media_type="application/json"
        )
