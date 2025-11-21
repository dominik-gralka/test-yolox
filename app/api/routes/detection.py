"""Object detection endpoints"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
from loguru import logger

from app.schemas.detection import DetectionResponse, Detection
from app.services.inference import get_inference_service
from app.core.config import get_settings

router = APIRouter()


@router.post("/detect", response_model=DetectionResponse, tags=["Detection"])
async def detect_objects(
    file: UploadFile = File(..., description="Image file to process"),
    confidence_threshold: Optional[float] = Form(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence threshold (default: from config)"
    ),
    nms_threshold: Optional[float] = Form(
        None,
        ge=0.0,
        le=1.0,
        description="NMS threshold (default: from config)"
    ),
    input_size: Optional[int] = Form(
        None,
        description="Input size (default: from config)"
    )
):
    """Detect objects in an image

    Upload an image file and receive detected objects with bounding boxes.

    **Supported formats**: JPEG, PNG, BMP, WEBP

    **Parameters**:
    - **file**: Image file to process (required)
    - **confidence_threshold**: Minimum confidence score (0.0-1.0, optional)
    - **nms_threshold**: Non-maximum suppression threshold (0.0-1.0, optional)
    - **input_size**: Model input size in pixels (optional)

    **Returns**:
    - List of detected objects with class, confidence, and bounding box
    - Inference time in milliseconds
    - Original image dimensions
    """
    settings = get_settings()

    # Validate file type (allow None for clients that don't set content_type)
    if file.content_type and not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Expected image, got {file.content_type}"
        )

    # Use config defaults if not provided
    conf_thresh = confidence_threshold or settings.confidence_threshold
    nms_thresh = nms_threshold or settings.nms_threshold
    inp_size = input_size or settings.input_size

    try:
        # Read image data
        image_bytes = await file.read()

        if len(image_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Run inference
        inference_service = get_inference_service()
        detections, inference_time, image_size = await inference_service.detect_objects(
            image_bytes=image_bytes,
            confidence_threshold=conf_thresh,
            nms_threshold=nms_thresh,
            input_size=inp_size
        )

        return DetectionResponse(
            success=True,
            detections=detections,
            num_detections=len(detections),
            inference_time_ms=inference_time,
            image_size=image_size
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Detection failed: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during detection")


@router.post("/detect/batch", tags=["Detection"])
async def detect_objects_batch(
    files: list[UploadFile] = File(..., description="Multiple image files to process")
):
    """Batch object detection (planned feature)

    Process multiple images in a single request.
    Currently returns 501 Not Implemented.
    """
    raise HTTPException(
        status_code=501,
        detail="Batch detection coming soon. Use /detect for single image inference."
    )
