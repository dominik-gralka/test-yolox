"""Model management and lifecycle - Singleton pattern for efficient resource usage"""
import torch
from loguru import logger
from typing import Optional
import threading


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
            self.initialized = False

    def load_model(self, model_path: str, device: str = "cuda") -> None:
        """Load YOLOX model

        Args:
            model_path: Path to model weights
            device: Device to load model on (cuda/cpu)
        """
        if self.initialized:
            logger.info("Model already loaded")
            return

        try:
            logger.info(f"Loading YOLOX model from {model_path}")

            # Determine device
            if device == "cuda" and not torch.cuda.is_available():
                logger.warning("CUDA not available, falling back to CPU")
                device = "cpu"

            self.device = torch.device(device)

            # Load YOLOX model
            # Note: This is a placeholder. In production, you would use:
            # from yolox.exp import get_exp
            # exp = get_exp(None, model_name)
            # model = exp.get_model()
            # model.load_state_dict(torch.load(model_path, map_location=self.device))
            # model.to(self.device)
            # model.eval()

            # For now, we'll create a placeholder structure
            self.model = self._create_placeholder_model(model_path)

            self.initialized = True
            logger.info(f"Model loaded successfully on {device}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def _create_placeholder_model(self, model_path: str):
        """Create a placeholder model structure

        This should be replaced with actual YOLOX model loading
        """
        class PlaceholderModel:
            def __init__(self, device):
                self.device = device
                self.eval_mode = True

            def eval(self):
                self.eval_mode = True
                return self

        return PlaceholderModel(self.device)

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

    def is_ready(self) -> bool:
        """Check if model is loaded and ready"""
        return self.initialized


def get_model_manager() -> ModelManager:
    """Get ModelManager singleton instance"""
    return ModelManager()
