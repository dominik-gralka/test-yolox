"""Video object detection endpoints"""
from fastapi import APIRouter, File, UploadFile, HTTPException, Form
from typing import Optional
from loguru import logger

from app.schemas.video import VideoDetectionResponse, FrameDetection
from app.services.video_inference import get_video_inference_service
from app.core.config import get_settings

router = APIRouter()


@router.post("/detect/video", response_model=VideoDetectionResponse, tags=["Video Detection"])
async def detect_objects_in_video(
    file: UploadFile = File(..., description="Video file to process"),
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
    ),
    sampling_rate: Optional[int] = Form(
        1,
        ge=1,
        description="Process every Nth frame (1=all frames, 2=every other, etc.)"
    ),
    max_frames: Optional[int] = Form(
        None,
        ge=1,
        description="Maximum frames to process (optional limit for long videos)"
    ),
    return_detections_only: Optional[bool] = Form(
        True,
        description="Only return frames with detections"
    )
):
    """Detect objects in a video file

    Processes a video frame-by-frame and returns detected objects for each frame.

    **Supported formats**: MP4, AVI, MOV, MKV, WEBM

    **Performance tips**:
    - Use `sampling_rate` > 1 to process fewer frames (e.g., 2 = every other frame)
    - Set `max_frames` to limit processing time for long videos
    - Enable `return_detections_only=true` to reduce response size

    **Parameters**:
    - **file**: Video file to process (required)
    - **confidence_threshold**: Minimum confidence score (0.0-1.0, optional)
    - **nms_threshold**: Non-maximum suppression threshold (0.0-1.0, optional)
    - **input_size**: Model input size in pixels (optional)
    - **sampling_rate**: Process every Nth frame (default: 1 = all frames)
    - **max_frames**: Maximum frames to process (optional, useful for long videos)
    - **return_detections_only**: Only return frames with detections (default: true)

    **Returns**:
    - Video metadata (resolution, fps, duration)
    - Detections per frame with timestamps
    - Processing statistics

    **Note**: For very long videos (>1 minute), consider using:
    - Higher `sampling_rate` (e.g., 5-10)
    - Or `max_frames` limit (e.g., 300 for ~10 seconds at 30fps)

    **Example**: Process every 5th frame with max 100 frames:
    ```bash
    curl -X POST "http://localhost:8000/api/v1/detect/video" \\
      -F "file=@video.mp4" \\
      -F "sampling_rate=5" \\
      -F "max_frames=100"
    ```
    """
    settings = get_settings()

    # Validate file type
    if not file.content_type or not file.content_type.startswith("video/"):
        # Also accept application/octet-stream as it's common for video uploads
        if file.content_type != "application/octet-stream":
            raise HTTPException(
                status_code=400,
                detail=f"Invalid file type. Expected video, got {file.content_type}"
            )

    # Use config defaults if not provided
    conf_thresh = confidence_threshold or settings.confidence_threshold
    nms_thresh = nms_threshold or settings.nms_threshold
    inp_size = input_size or settings.input_size

    # Validate sampling_rate
    if sampling_rate < 1:
        raise HTTPException(
            status_code=400,
            detail="sampling_rate must be >= 1"
        )

    try:
        # Read video data
        video_bytes = await file.read()

        if len(video_bytes) == 0:
            raise HTTPException(status_code=400, detail="Empty file uploaded")

        # Log file size for monitoring
        file_size_mb = len(video_bytes) / (1024 * 1024)
        logger.info(f"Processing video: {file_size_mb:.2f} MB")

        # Warn if file is very large
        if file_size_mb > 100:
            logger.warning(
                f"Large video file detected ({file_size_mb:.2f} MB). "
                "Consider using sampling_rate or max_frames to reduce processing time."
            )

        # Run video inference
        video_service = get_video_inference_service()
        frame_detections, video_info, processing_time = await video_service.process_video(
            video_bytes=video_bytes,
            confidence_threshold=conf_thresh,
            nms_threshold=nms_thresh,
            input_size=inp_size,
            sampling_rate=sampling_rate,
            max_frames=max_frames,
            return_detections_only=return_detections_only
        )

        # Calculate statistics
        frames_with_detections = sum(1 for fd in frame_detections if fd.num_detections > 0)
        total_frames_processed = len(frame_detections) if not return_detections_only else None

        # Calculate avg FPS
        avg_fps = len(frame_detections) / (processing_time / 1000) if processing_time > 0 else 0

        # Determine total frames based on return_detections_only flag
        if return_detections_only:
            # When returning only frames with detections, total_frames = frames_with_detections
            total_frames = frames_with_detections
        else:
            # When returning all frames, total_frames = all processed frames
            total_frames = len(frame_detections)

        return VideoDetectionResponse(
            success=True,
            video_info=video_info,
            total_frames=total_frames,
            frames_with_detections=frames_with_detections,
            processing_time_ms=processing_time,
            avg_fps=avg_fps,
            frame_detections=frame_detections
        )

    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Video detection failed: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error during video detection"
        )


@router.get("/detect/video/formats", tags=["Video Detection"])
async def get_supported_video_formats():
    """Get list of supported video formats

    Returns information about supported video formats and codec recommendations.
    """
    return {
        "supported_formats": [
            "MP4",
            "AVI",
            "MOV",
            "MKV",
            "WEBM",
            "FLV"
        ],
        "recommended_format": "MP4",
        "recommended_codec": "H.264/H.265",
        "notes": [
            "MP4 with H.264 is the most compatible format",
            "Use sampling_rate parameter to speed up processing",
            "Consider max_frames limit for videos longer than 1 minute",
            "return_detections_only=true reduces response size significantly"
        ],
        "performance_tips": {
            "short_videos": "Use sampling_rate=1 (process all frames)",
            "medium_videos": "Use sampling_rate=2-5 (process every 2-5 frames)",
            "long_videos": "Use sampling_rate=10-30 or set max_frames limit"
        }
    }
