#!/usr/bin/env python3
"""
YOLOX API Client Example

Zeigt verschiedene Möglichkeiten, die YOLOX API zu nutzen.
"""

import requests
from pathlib import Path
from typing import Optional
import json


class YOLOXClient:
    """Client für die YOLOX Object Detection API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Args:
            base_url: Basis-URL der API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"

    def health_check(self) -> dict:
        """Prüft den Health-Status der API"""
        response = requests.get(f"{self.api_base}/health")
        response.raise_for_status()
        return response.json()

    def detect(
        self,
        image_path: str,
        confidence_threshold: Optional[float] = None,
        nms_threshold: Optional[float] = None,
        input_size: Optional[int] = None
    ) -> dict:
        """
        Führt Object Detection auf einem Bild aus

        Args:
            image_path: Pfad zum Bild
            confidence_threshold: Confidence-Schwellenwert (0.0-1.0)
            nms_threshold: NMS-Schwellenwert (0.0-1.0)
            input_size: Eingabegröße für das Modell

        Returns:
            Detection-Ergebnisse
        """
        # Datei öffnen
        with open(image_path, 'rb') as f:
            files = {'file': f}

            # Optional: Parameter hinzufügen
            data = {}
            if confidence_threshold is not None:
                data['confidence_threshold'] = confidence_threshold
            if nms_threshold is not None:
                data['nms_threshold'] = nms_threshold
            if input_size is not None:
                data['input_size'] = input_size

            # Anfrage senden
            response = requests.post(
                f"{self.api_base}/detect",
                files=files,
                data=data
            )
            response.raise_for_status()

        return response.json()

    def print_detections(self, result: dict):
        """Gibt Detection-Ergebnisse formatiert aus"""
        print(f"\n{'='*60}")
        print(f"Detection Results")
        print(f"{'='*60}")
        print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
        print(f"Detections: {result['num_detections']}")
        print(f"Inference Time: {result['inference_time_ms']:.2f}ms")
        print(f"Image Size: {result['image_size']['width']}x{result['image_size']['height']}")

        if result['detections']:
            print(f"\n{'Object':<20} {'Confidence':<12} {'Bounding Box'}")
            print(f"{'-'*60}")
            for det in result['detections']:
                bbox = det['bbox']
                bbox_str = f"({bbox['x1']:.0f},{bbox['y1']:.0f})-({bbox['x2']:.0f},{bbox['y2']:.0f})"
                print(f"{det['class_name']:<20} {det['confidence']:<12.2%} {bbox_str}")
        print(f"{'='*60}\n")


def main():
    """Beispiel-Nutzung"""

    # Client initialisieren
    client = YOLOXClient(base_url="http://localhost:8000")

    # 1. Health Check
    print("Checking API health...")
    try:
        health = client.health_check()
        print(f"✓ API is {health['status']}")
        print(f"  Model loaded: {health['model_loaded']}")
        print(f"  Device: {health['device']}")
        print(f"  Version: {health['version']}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Health check failed: {e}")
        return

    # 2. Object Detection
    # Hinweis: Ersetzen Sie diesen Pfad durch ein echtes Bild
    image_path = "path/to/your/image.jpg"

    if not Path(image_path).exists():
        print(f"\n⚠ Beispielbild nicht gefunden: {image_path}")
        print("Bitte ersetzen Sie 'image_path' durch einen gültigen Bildpfad")
        return

    print(f"\nRunning detection on: {image_path}")

    try:
        # Detection durchführen
        result = client.detect(
            image_path=image_path,
            confidence_threshold=0.5
        )

        # Ergebnisse anzeigen
        client.print_detections(result)

        # Optional: Ergebnisse speichern
        output_path = "detection_results.json"
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to: {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Detection failed: {e}")
    except FileNotFoundError:
        print(f"✗ Image not found: {image_path}")


if __name__ == "__main__":
    main()
