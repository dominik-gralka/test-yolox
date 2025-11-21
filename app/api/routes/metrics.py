"""Prometheus metrics endpoint"""
from fastapi import APIRouter
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response

router = APIRouter()

# Metrics
detection_requests_total = Counter(
    'yolox_detection_requests_total',
    'Total number of detection requests',
    ['status']
)

detection_duration_seconds = Histogram(
    'yolox_detection_duration_seconds',
    'Detection request duration in seconds',
    buckets=[0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0]
)

active_requests = Gauge(
    'yolox_active_requests',
    'Number of currently active requests'
)

model_info = Gauge(
    'yolox_model_info',
    'Model information',
    ['model_name', 'device']
)


@router.get("/metrics", tags=["Monitoring"])
async def metrics():
    """Prometheus metrics endpoint

    Returns metrics in Prometheus format for monitoring and alerting.
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
