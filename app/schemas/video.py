"""Pydantic schemas for video detection requests and responses"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from app.schemas.detection import Detection


class FrameDetection(BaseModel):
    """Detections for a single video frame"""
    frame_number: int = Field(..., description="Frame number in the video")
    timestamp_ms: float = Field(..., description="Timestamp in milliseconds")
    detections: List[Detection] = Field(..., description="Objects detected in this frame")
    num_detections: int = Field(..., description="Number of detections in this frame")


class VideoDetectionResponse(BaseModel):
    """Response from video detection endpoint"""
    success: bool = Field(True, description="Whether detection was successful")
    video_info: Dict = Field(..., description="Video metadata")
    total_frames: int = Field(..., description="Total number of frames processed")
    frames_with_detections: int = Field(..., description="Number of frames containing detections")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    avg_fps: float = Field(..., description="Average frames per second processed")
    frame_detections: List[FrameDetection] = Field(
        ...,
        description="Detections per frame (may be sampled based on sampling_rate)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "video_info": {
                    "width": 1920,
                    "height": 1080,
                    "fps": 30.0,
                    "duration_sec": 10.0,
                    "total_frames": 300
                },
                "total_frames": 100,
                "frames_with_detections": 85,
                "processing_time_ms": 4500.2,
                "avg_fps": 22.2,
                "frame_detections": [
                    {
                        "frame_number": 0,
                        "timestamp_ms": 0.0,
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
                        "num_detections": 1
                    }
                ]
            }
        }


class VideoDetectionRequest(BaseModel):
    """Request parameters for video detection"""
    confidence_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence threshold for detections"
    )
    nms_threshold: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="NMS threshold"
    )
    input_size: Optional[int] = Field(
        None,
        description="Input size for model"
    )
    sampling_rate: Optional[int] = Field(
        1,
        ge=1,
        description="Process every Nth frame (1=all frames, 2=every other frame, etc.)"
    )
    max_frames: Optional[int] = Field(
        None,
        ge=1,
        description="Maximum number of frames to process (optional limit)"
    )
    return_detections_only: Optional[bool] = Field(
        True,
        description="If True, only return frames with detections"
    )


class VideoProcessingStatus(BaseModel):
    """Status response for async video processing"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Processing status: pending, processing, completed, failed")
    progress: float = Field(..., ge=0.0, le=100.0, description="Processing progress percentage")
    frames_processed: int = Field(0, description="Number of frames processed so far")
    total_frames: Optional[int] = Field(None, description="Total frames to process")
    result_url: Optional[str] = Field(None, description="URL to download results when completed")
    error: Optional[str] = Field(None, description="Error message if failed")
