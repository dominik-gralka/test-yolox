"""YOLOX inference service - Stateless inference logic"""
import cv2
import numpy as np
import torch
import time
from typing import List, Tuple
from loguru import logger

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
        input_size: Tuple[int, int] = (640, 640)
    ) -> Tuple[torch.Tensor, dict]:
        """Preprocess image for YOLOX inference using YOLOX's preprocessing

        Args:
            image_bytes: Raw image bytes
            input_size: Target input size (height, width)

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

        # Use YOLOX's preprocess function
        try:
            from yolox.data.data_augment import preproc
            img, ratio = preproc(img, input_size, swap=(2, 0, 1))

            # Convert to tensor
            img_tensor = torch.from_numpy(img).unsqueeze(0).float()

            image_info["ratio"] = ratio

        except ImportError:
            # Fallback to manual preprocessing if YOLOX not available
            logger.warning("YOLOX preproc not available, using manual preprocessing")

            # Resize while maintaining aspect ratio
            ratio = min(input_size[0] / original_height, input_size[1] / original_width)
            new_height = int(original_height * ratio)
            new_width = int(original_width * ratio)

            img_resized = cv2.resize(img, (new_width, new_height))

            # Pad to target size
            padded_img = np.ones((input_size[0], input_size[1], 3), dtype=np.uint8) * 114
            padded_img[:new_height, :new_width] = img_resized

            # Convert BGR to RGB and normalize
            padded_img = cv2.cvtColor(padded_img, cv2.COLOR_BGR2RGB)
            img_tensor = torch.from_numpy(padded_img).float()
            img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)  # HWC to NCHW
            img_tensor /= 255.0

            image_info["ratio"] = ratio

        return img_tensor, image_info

    def postprocess_predictions(
        self,
        outputs: torch.Tensor,
        image_info: dict,
        confidence_threshold: float = 0.3,
        nms_threshold: float = 0.45,
        num_classes: int = 80
    ) -> List[Detection]:
        """Postprocess YOLOX model outputs to detections

        Args:
            outputs: Raw model outputs [batch, num_boxes, 5+num_classes]
            image_info: Information about original image
            confidence_threshold: Confidence threshold
            nms_threshold: NMS threshold
            num_classes: Number of classes

        Returns:
            List of Detection objects
        """
        detections = []

        if outputs is None or outputs.shape[0] == 0:
            return detections

        # outputs shape: [batch, num_boxes, 5+num_classes]
        # where 5 = [x, y, w, h, obj_conf]

        try:
            from yolox.utils import postprocess

            # Apply postprocessing (NMS, etc.)
            output = postprocess(
                outputs,
                num_classes=num_classes,
                conf_thre=confidence_threshold,
                nms_thre=nms_threshold
            )

            if output[0] is None:
                return detections

            # output[0] shape: [num_detections, 7]
            # where 7 = [x1, y1, x2, y2, obj_conf, class_conf, class_id]
            predictions = output[0].cpu().numpy()

            # Scale boxes back to original image size
            ratio = image_info.get("ratio", 1.0)

            for pred in predictions:
                x1, y1, x2, y2, obj_conf, class_conf, class_id = pred

                # Scale coordinates back to original image
                x1 /= ratio
                y1 /= ratio
                x2 /= ratio
                y2 /= ratio

                # Get class name
                class_id = int(class_id)
                class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"class_{class_id}"

                # Create detection object
                detection = Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=float(class_conf),
                    bbox=BoundingBox(
                        x1=float(x1),
                        y1=float(y1),
                        x2=float(x2),
                        y2=float(y2)
                    )
                )
                detections.append(detection)

        except ImportError:
            logger.error("YOLOX postprocess not available")
            # Fallback: basic processing without NMS
            if len(outputs.shape) == 3:
                predictions = outputs[0]  # Get first batch
            else:
                predictions = outputs

            # Filter by confidence
            obj_conf = predictions[:, 4]
            mask = obj_conf > confidence_threshold
            predictions = predictions[mask]

            if predictions.shape[0] > 0:
                # Get class predictions
                class_conf, class_pred = torch.max(predictions[:, 5:], dim=1)

                # Combined confidence
                final_conf = obj_conf[mask] * class_conf

                # Filter by final confidence
                mask2 = final_conf > confidence_threshold
                predictions = predictions[mask2]
                class_pred = class_pred[mask2]
                final_conf = final_conf[mask2]

                ratio = image_info.get("ratio", 1.0)

                for i in range(predictions.shape[0]):
                    pred = predictions[i]
                    x_center, y_center, width, height = pred[:4]

                    # Convert from center format to corner format
                    x1 = (x_center - width / 2) / ratio
                    y1 = (y_center - height / 2) / ratio
                    x2 = (x_center + width / 2) / ratio
                    y2 = (y_center + height / 2) / ratio

                    class_id = int(class_pred[i])
                    class_name = COCO_CLASSES[class_id] if class_id < len(COCO_CLASSES) else f"class_{class_id}"

                    detection = Detection(
                        class_id=class_id,
                        class_name=class_name,
                        confidence=float(final_conf[i]),
                        bbox=BoundingBox(
                            x1=float(x1),
                            y1=float(y1),
                            x2=float(x2),
                            y2=float(y2)
                        )
                    )
                    detections.append(detection)

        logger.debug(f"Postprocessing complete: {len(detections)} detections")
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
            # Get model and experiment
            model = self.model_manager.get_model()
            device = self.model_manager.get_device()
            exp = self.model_manager.get_exp()

            # Use experiment's test size if available
            test_size = getattr(exp, 'test_size', (input_size, input_size))
            num_classes = getattr(exp, 'num_classes', 80)

            # Preprocess image
            img_tensor, image_info = self.preprocess_image(image_bytes, test_size)

            # Move to device
            img_tensor = img_tensor.to(device)

            # Run inference
            with torch.no_grad():
                outputs = model(img_tensor)

            # Postprocess
            detections = self.postprocess_predictions(
                outputs,
                image_info,
                confidence_threshold,
                nms_threshold,
                num_classes
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
            logger.exception("Full traceback:")
            raise


def get_inference_service() -> YOLOXInferenceService:
    """Get inference service instance"""
    return YOLOXInferenceService()
