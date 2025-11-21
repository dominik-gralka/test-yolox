"""Model management and lifecycle - Singleton pattern for efficient resource usage"""
import torch
from loguru import logger
from typing import Optional
import threading
import os


class ModelManager:
    """Singleton model manager for YOLOX inference

    This ensures only one model instance is loaded per worker process,
    making the service stateless at the API level while maintaining
    efficient resource usage.
    """

    _instance: Optional['ModelManager'] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.model = None
            self.device = None
            self.exp = None
            self.num_classes = 80  # COCO classes
            self.initialized = False

    def load_model(self, model_path: str, device: str = "cuda", model_name: str = "yolox-s") -> None:
        """Load YOLOX model

        Args:
            model_path: Path to model weights
            device: Device to load model on (cuda/cpu)
            model_name: YOLOX model variant (yolox-nano, yolox-tiny, yolox-s, yolox-m, yolox-l, yolox-x)
        """
        if self.initialized:
            logger.info("Model already loaded")
            return

        try:
            logger.info(f"Loading YOLOX model {model_name} from {model_path}")

            # Determine device
            if device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                device = "cpu"

            self.device = torch.device(device)

            # Import YOLOX
            try:
                from yolox.exp import get_exp
            except ImportError:
                logger.error("YOLOX not installed. Please install: pip install git+https://github.com/Megvii-BaseDetection/YOLOX.git")
                raise

            # Get experiment configuration
            logger.info(f"Initializing {model_name} experiment configuration")
            self.exp = get_exp(None, model_name)

            # Get model from experiment
            model = self.exp.get_model()
            logger.info(f"Model architecture created: {model_name}")

            # Load weights if path exists
            if os.path.exists(model_path):
                logger.info(f"Loading weights from {model_path}")
                ckpt = torch.load(model_path, map_location=self.device)

                # Handle different checkpoint formats
                if "model" in ckpt:
                    model.load_state_dict(ckpt["model"])
                    logger.info("Loaded model weights from 'model' key")
                else:
                    model.load_state_dict(ckpt)
                    logger.info("Loaded model weights directly")
            else:
                logger.warning(f"Model weights not found at {model_path}")
                logger.warning("Model will use random initialization - download weights for inference!")
                logger.info("Download weights from: https://github.com/Megvii-BaseDetection/YOLOX/releases")

            # Move model to device and set to eval mode
            model.to(self.device)
            model.eval()

            self.model = model
            self.initialized = True

            logger.info(f"✓ Model loaded successfully on {device}")
            logger.info(f"  Input size: {self.exp.test_size}")
            logger.info(f"  Number of classes: {self.exp.num_classes}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            logger.exception("Full traceback:")
            raise

    def get_model(self):
        """Get loaded model instance"""
        if not self.initialized:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.model

    def get_device(self):
        """Get device where model is loaded"""
        if not self.initialized:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.device

    def get_exp(self):
        """Get YOLOX experiment configuration"""
        if not self.initialized:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        return self.exp

    def is_ready(self) -> bool:
        """Check if model is loaded and ready"""
        return self.initialized


def get_model_manager() -> ModelManager:
    """Get ModelManager singleton instance"""
    return ModelManager()
