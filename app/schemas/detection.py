"""Pydantic schemas for detection requests and responses"""
from pydantic import BaseModel, Field
from typing import List, Optional


class BoundingBox(BaseModel):
    """Bounding box coordinates"""
    x1: float = Field(..., description="Top-left x coordinate")
    y1: float = Field(..., description="Top-left y coordinate")
    x2: float = Field(..., description="Bottom-right x coordinate")
    y2: float = Field(..., description="Bottom-right y coordinate")


class Detection(BaseModel):
    """Single object detection"""
    class_id: int = Field(..., description="Class ID of detected object")
    class_name: str = Field(..., description="Class name of detected object")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Detection confidence score")
    bbox: BoundingBox = Field(..., description="Bounding box coordinates")


class DetectionResponse(BaseModel):
    """Response from object detection endpoint"""
    success: bool = Field(True, description="Whether detection was successful")
    detections: List[Detection] = Field(..., description="List of detected objects")
    num_detections: int = Field(..., description="Total number of detections")
    inference_time_ms: float = Field(..., description="Inference time in milliseconds")
    image_size: dict = Field(..., description="Input image dimensions")

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "detections": [
                    {
                        "class_id": 0,
                        "class_name": "person",
                        "confidence": 0.95,
                        "bbox": {
                            "x1": 100.0,
                            "y1": 150.0,
                            "x2": 300.0,
                            "y2": 450.0
                        }
                    }
                ],
                "num_detections": 1,
                "inference_time_ms": 45.2,
                "image_size": {"width": 640, "height": 480}
            }
        }


class DetectionRequest(BaseModel):
    """Request parameters for detection"""
    confidence_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for detections (overrides default)"
    )
    nms_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="NMS threshold (overrides default)"
    )
    input_size: Optional[int] = Field(
        None,
        description="Input size for model (overrides default)"
    )


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    device: str = Field(..., description="Device used for inference")
    version: str = Field(..., description="API version")
