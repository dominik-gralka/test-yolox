"""YOLOX inference service - Stateless inference logic"""
import cv2
import numpy as np
import torch
import time
from typing import List, Tuple
from loguru import logger
from PIL import Image
import io

from app.schemas.detection import Detection, BoundingBox
from app.core.model_manager import get_model_manager


# COCO class names (80 classes)
COCO_CLASSES = [
    "person", "bicycle", "car", "motorcycle", "airplane", "bus", "train", "truck", "boat",
    "traffic light", "fire hydrant", "stop sign", "parking meter", "bench", "bird", "cat",
    "dog", "horse", "sheep", "cow", "elephant", "bear", "zebra", "giraffe", "backpack",
    "umbrella", "handbag", "tie", "suitcase", "frisbee", "skis", "snowboard", "sports ball",
    "kite", "baseball bat", "baseball glove", "skateboard", "surfboard", "tennis racket",
    "bottle", "wine glass", "cup", "fork", "knife", "spoon", "bowl", "banana", "apple",
    "sandwich", "orange", "broccoli", "carrot", "hot dog", "pizza", "donut", "cake", "chair",
    "couch", "potted plant", "bed", "dining table", "toilet", "tv", "laptop", "mouse",
    "remote", "keyboard", "cell phone", "microwave", "oven", "toaster", "sink",
    "refrigerator", "book", "clock", "vase", "scissors", "teddy bear", "hair drier",
    "toothbrush"
]


class YOLOXInferenceService:
    """Stateless YOLOX inference service

    Each inference call is independent and maintains no state between requests.
    This enables horizontal scaling and load balancing.
    """

    def __init__(self):
        self.model_manager = get_model_manager()

    def preprocess_image(
        self,
        image_bytes: bytes,
        input_size: int = 640
    ) -> Tuple[torch.Tensor, dict]:
        """Preprocess image for YOLOX inference

        Args:
            image_bytes: Raw image bytes
            input_size: Target input size

        Returns:
            Preprocessed tensor and original image info
        """
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            raise ValueError("Failed to decode image")

        # Store original dimensions
        original_height, original_width = img.shape[:2]
        image_info = {
            "width": original_width,
            "height": original_height
        }

        # Resize image while maintaining aspect ratio
        ratio = min(input_size / original_width, input_size / original_height)
        new_width = int(original_width * ratio)
        new_height = int(original_height * ratio)

        img_resized = cv2.resize(img, (new_width, new_height))

        # Pad to square
        padded_img = np.ones((input_size, input_size, 3), dtype=np.uint8) * 114
        padded_img[:new_height, :new_width] = img_resized

        # Convert to RGB and normalize
        padded_img = cv2.cvtColor(padded_img, cv2.COLOR_BGR2RGB)
        img_tensor = torch.from_numpy(padded_img).float()
        img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)  # HWC to NCHW

        # Normalize
        img_tensor /= 255.0

        image_info["ratio"] = ratio

        return img_tensor, image_info

    def postprocess_predictions(
        self,
        outputs: torch.Tensor,
        image_info: dict,
        confidence_threshold: float = 0.3,
        nms_threshold: float = 0.45
    ) -> List[Detection]:
        """Postprocess model outputs to detections

        Args:
            outputs: Raw model outputs
            image_info: Information about original image
            confidence_threshold: Confidence threshold
            nms_threshold: NMS threshold

        Returns:
            List of Detection objects
        """
        # This is a placeholder implementation
        # In production, this would process actual YOLOX outputs
        # The real implementation would include:
        # 1. Decode predictions
        # 2. Apply NMS
        # 3. Scale boxes back to original image size
        # 4. Create Detection objects

        detections = []

        # Placeholder: Return empty detections
        # Real implementation would process outputs tensor
        logger.debug(f"Processing predictions with conf={confidence_threshold}, nms={nms_threshold}")

        return detections

    async def detect_objects(
        self,
        image_bytes: bytes,
        confidence_threshold: float = 0.3,
        nms_threshold: float = 0.45,
        input_size: int = 640
    ) -> Tuple[List[Detection], float, dict]:
        """Run object detection on image

        Args:
            image_bytes: Raw image bytes
            confidence_threshold: Confidence threshold
            nms_threshold: NMS threshold
            input_size: Model input size

        Returns:
            Tuple of (detections, inference_time_ms, image_size)
        """
        start_time = time.time()

        try:
            # Preprocess image
            img_tensor, image_info = self.preprocess_image(image_bytes, input_size)

            # Move to device
            device = self.model_manager.get_device()
            img_tensor = img_tensor.to(device)

            # Run inference
            model = self.model_manager.get_model()

            # Placeholder inference
            # In production, this would be:
            # with torch.no_grad():
            #     outputs = model(img_tensor)

            # For now, create dummy outputs
            with torch.no_grad():
                outputs = torch.randn(1, 100, 85).to(device)  # Placeholder

            # Postprocess
            detections = self.postprocess_predictions(
                outputs,
                image_info,
                confidence_threshold,
                nms_threshold
            )

            # Calculate inference time
            inference_time = (time.time() - start_time) * 1000  # Convert to ms

            logger.info(
                f"Detection complete: {len(detections)} objects found "
                f"in {inference_time:.2f}ms"
            )

            return detections, inference_time, image_info

        except Exception as e:
            logger.error(f"Inference failed: {e}")
            raise


def get_inference_service() -> YOLOXInferenceService:
    """Get inference service instance"""
    return YOLOXInferenceService()
