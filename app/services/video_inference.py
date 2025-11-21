"""Video inference service - Process videos frame by frame"""
import cv2
import numpy as np
import time
import tempfile
from typing import List, Tuple, Dict, Optional
from loguru import logger
import io

from app.schemas.video import FrameDetection
from app.schemas.detection import Detection
from app.services.inference import YOLOXInferenceService


class VideoInferenceService:
    """Service for running YOLOX inference on videos

    Processes videos frame-by-frame and returns detections for each frame.
    Supports frame sampling to reduce processing time.
    """

    def __init__(self):
        self.image_inference_service = YOLOXInferenceService()

    def get_video_info(self, video_path: str) -> Dict:
        """Extract video metadata

        Args:
            video_path: Path to video file

        Returns:
            Dictionary with video metadata
        """
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            raise ValueError(f"Failed to open video: {video_path}")

        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0

        cap.release()

        return {
            "width": width,
            "height": height,
            "fps": fps,
            "total_frames": frame_count,
            "duration_sec": duration
        }

    async def process_video(
        self,
        video_bytes: bytes,
        confidence_threshold: float = 0.3,
        nms_threshold: float = 0.45,
        input_size: int = 640,
        sampling_rate: int = 1,
        max_frames: Optional[int] = None,
        return_detections_only: bool = True
    ) -> Tuple[List[FrameDetection], Dict, float]:
        """Process video and detect objects in frames

        Args:
            video_bytes: Video file as bytes
            confidence_threshold: Detection confidence threshold
            nms_threshold: NMS threshold
            input_size: Model input size
            sampling_rate: Process every Nth frame
            max_frames: Maximum frames to process
            return_detections_only: Only return frames with detections

        Returns:
            Tuple of (frame_detections, video_info, processing_time_ms)
        """
        start_time = time.time()
        frame_detections: List[FrameDetection] = []

        # Save video bytes to temporary file
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            tmp_file.write(video_bytes)
            tmp_path = tmp_file.name

        try:
            # Get video info
            video_info = self.get_video_info(tmp_path)
            logger.info(
                f"Processing video: {video_info['width']}x{video_info['height']}, "
                f"{video_info['fps']:.2f} fps, {video_info['total_frames']} frames"
            )

            # Open video
            cap = cv2.VideoCapture(tmp_path)
            frame_number = 0
            processed_frames = 0

            while cap.isOpened():
                ret, frame = cap.read()

                if not ret:
                    break

                # Check max frames limit
                if max_frames and processed_frames >= max_frames:
                    logger.info(f"Reached max_frames limit: {max_frames}")
                    break

                # Sample frames based on sampling_rate
                if frame_number % sampling_rate == 0:
                    # Convert frame to bytes
                    success, buffer = cv2.imencode('.jpg', frame)
                    if not success:
                        logger.warning(f"Failed to encode frame {frame_number}")
                        frame_number += 1
                        continue

                    frame_bytes = buffer.tobytes()

                    # Run detection on frame
                    try:
                        detections, inference_time, _ = await self.image_inference_service.detect_objects(
                            image_bytes=frame_bytes,
                            confidence_threshold=confidence_threshold,
                            nms_threshold=nms_threshold,
                            input_size=input_size
                        )

                        # Calculate timestamp
                        timestamp_ms = (frame_number / video_info['fps']) * 1000 if video_info['fps'] > 0 else 0

                        # Store results (optionally filter empty frames)
                        if not return_detections_only or len(detections) > 0:
                            frame_detection = FrameDetection(
                                frame_number=frame_number,
                                timestamp_ms=timestamp_ms,
                                detections=detections,
                                num_detections=len(detections)
                            )
                            frame_detections.append(frame_detection)

                        processed_frames += 1

                        if processed_frames % 10 == 0:
                            logger.debug(
                                f"Processed {processed_frames} frames, "
                                f"found {len(frame_detections)} frames with detections"
                            )

                    except Exception as e:
                        logger.error(f"Failed to process frame {frame_number}: {e}")

                frame_number += 1

            cap.release()

            # Calculate processing statistics
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            avg_fps = processed_frames / (processing_time / 1000) if processing_time > 0 else 0

            logger.info(
                f"Video processing complete: {processed_frames} frames processed "
                f"in {processing_time:.2f}ms ({avg_fps:.2f} fps)"
            )

            return frame_detections, video_info, processing_time

        finally:
            # Clean up temporary file
            import os
            try:
                os.unlink(tmp_path)
            except Exception as e:
                logger.warning(f"Failed to delete temp file {tmp_path}: {e}")

    def calculate_statistics(
        self,
        frame_detections: List[FrameDetection]
    ) -> Dict:
        """Calculate statistics about detections across frames

        Args:
            frame_detections: List of frame detections

        Returns:
            Dictionary with statistics
        """
        if not frame_detections:
            return {
                "frames_with_detections": 0,
                "total_detections": 0,
                "avg_detections_per_frame": 0.0,
                "most_common_classes": []
            }

        frames_with_detections = sum(1 for fd in frame_detections if fd.num_detections > 0)
        total_detections = sum(fd.num_detections for fd in frame_detections)
        avg_detections = total_detections / len(frame_detections) if frame_detections else 0

        # Count class occurrences
        class_counts = {}
        for fd in frame_detections:
            for det in fd.detections:
                class_name = det.class_name
                class_counts[class_name] = class_counts.get(class_name, 0) + 1

        # Sort by count
        most_common = sorted(
            class_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]  # Top 5

        return {
            "frames_with_detections": frames_with_detections,
            "total_detections": total_detections,
            "avg_detections_per_frame": avg_detections,
            "most_common_classes": [
                {"class_name": name, "count": count}
                for name, count in most_common
            ]
        }


def get_video_inference_service() -> VideoInferenceService:
    """Get video inference service instance"""
    return VideoInferenceService()
