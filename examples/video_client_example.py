#!/usr/bin/env python3
"""
YOLOX Video API Client Example

Zeigt, wie man Videos über die API verarbeitet.
"""

import requests
from pathlib import Path
from typing import Optional
import json
import time


class YOLOXVideoClient:
    """Client für die YOLOX Video Detection API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        """
        Args:
            base_url: Basis-URL der API (default: http://localhost:8000)
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/api/v1"

    def detect_video(
        self,
        video_path: str,
        confidence_threshold: Optional[float] = None,
        nms_threshold: Optional[float] = None,
        input_size: Optional[int] = None,
        sampling_rate: int = 1,
        max_frames: Optional[int] = None,
        return_detections_only: bool = True
    ) -> dict:
        """
        Führt Object Detection auf einem Video aus

        Args:
            video_path: Pfad zum Video
            confidence_threshold: Confidence-Schwellenwert (0.0-1.0)
            nms_threshold: NMS-Schwellenwert (0.0-1.0)
            input_size: Eingabegröße für das Modell
            sampling_rate: Jeden Nth Frame verarbeiten (1=alle Frames)
            max_frames: Maximum Anzahl zu verarbeitender Frames
            return_detections_only: Nur Frames mit Detections zurückgeben

        Returns:
            Detection-Ergebnisse für Video
        """
        # Datei öffnen
        with open(video_path, 'rb') as f:
            files = {'file': f}

            # Parameter hinzufügen
            data = {
                'sampling_rate': sampling_rate,
                'return_detections_only': return_detections_only
            }

            if confidence_threshold is not None:
                data['confidence_threshold'] = confidence_threshold
            if nms_threshold is not None:
                data['nms_threshold'] = nms_threshold
            if input_size is not None:
                data['input_size'] = input_size
            if max_frames is not None:
                data['max_frames'] = max_frames

            # Anfrage senden
            print(f"Uploading and processing video: {video_path}")
            start_time = time.time()

            response = requests.post(
                f"{self.api_base}/detect/video",
                files=files,
                data=data
            )
            response.raise_for_status()

            upload_time = time.time() - start_time
            print(f"Upload and processing completed in {upload_time:.2f}s")

        return response.json()

    def get_supported_formats(self) -> dict:
        """Gibt unterstützte Video-Formate zurück"""
        response = requests.get(f"{self.api_base}/detect/video/formats")
        response.raise_for_status()
        return response.json()

    def print_video_results(self, result: dict, verbose: bool = False):
        """Gibt Video-Detection-Ergebnisse formatiert aus"""
        print(f"\n{'='*70}")
        print(f"Video Detection Results")
        print(f"{'='*70}")

        # Status
        print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")

        # Video Info
        video_info = result['video_info']
        print(f"\nVideo Information:")
        print(f"  Resolution: {video_info['width']}x{video_info['height']}")
        print(f"  FPS: {video_info['fps']:.2f}")
        print(f"  Duration: {video_info['duration_sec']:.2f}s")
        print(f"  Total Frames in Video: {video_info['total_frames']}")

        # Processing Stats
        print(f"\nProcessing Statistics:")
        print(f"  Frames Processed: {result['total_frames']}")
        print(f"  Frames with Detections: {result['frames_with_detections']}")
        print(f"  Processing Time: {result['processing_time_ms']:.2f}ms ({result['processing_time_ms']/1000:.2f}s)")
        print(f"  Average Processing FPS: {result['avg_fps']:.2f}")

        # Detection Rate
        if result['total_frames'] > 0:
            detection_rate = (result['frames_with_detections'] / result['total_frames']) * 100
            print(f"  Detection Rate: {detection_rate:.1f}%")

        # Frame-by-frame results
        frame_detections = result['frame_detections']
        if frame_detections:
            print(f"\nDetections by Frame ({len(frame_detections)} frames):")

            if verbose:
                # Show all frames
                for fd in frame_detections:
                    timestamp = fd['timestamp_ms'] / 1000
                    print(f"\n  Frame {fd['frame_number']} (t={timestamp:.2f}s): {fd['num_detections']} objects")
                    for det in fd['detections']:
                        bbox = det['bbox']
                        print(f"    - {det['class_name']}: {det['confidence']:.2%} at "
                              f"({bbox['x1']:.0f},{bbox['y1']:.0f})-({bbox['x2']:.0f},{bbox['y2']:.0f})")
            else:
                # Show summary
                print(f"  (Use verbose=True to see all frames)")

                # Show first few frames with detections
                show_count = min(5, len(frame_detections))
                for fd in frame_detections[:show_count]:
                    timestamp = fd['timestamp_ms'] / 1000
                    classes = [det['class_name'] for det in fd['detections']]
                    class_summary = ', '.join(set(classes))
                    print(f"  Frame {fd['frame_number']} (t={timestamp:.2f}s): {fd['num_detections']} objects ({class_summary})")

                if len(frame_detections) > show_count:
                    print(f"  ... and {len(frame_detections) - show_count} more frames")

            # Class summary
            class_counts = {}
            for fd in frame_detections:
                for det in fd['detections']:
                    class_name = det['class_name']
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1

            if class_counts:
                print(f"\nObject Summary (across all frames):")
                for class_name, count in sorted(class_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"  {class_name}: {count} detections")

        print(f"{'='*70}\n")


def main():
    """Beispiel-Nutzung"""

    # Client initialisieren
    client = YOLOXVideoClient(base_url="http://localhost:8000")

    # 1. Unterstützte Formate anzeigen
    print("Fetching supported video formats...")
    try:
        formats = client.get_supported_formats()
        print(f"\nSupported formats: {', '.join(formats['supported_formats'])}")
        print(f"Recommended: {formats['recommended_format']} with {formats['recommended_codec']}")
    except requests.exceptions.RequestException as e:
        print(f"✗ Failed to get formats: {e}")
        return

    # 2. Video Detection
    # Hinweis: Ersetzen Sie diesen Pfad durch ein echtes Video
    video_path = "path/to/your/video.mp4"

    if not Path(video_path).exists():
        print(f"\n⚠ Beispielvideo nicht gefunden: {video_path}")
        print("Bitte ersetzen Sie 'video_path' durch einen gültigen Videopfad")
        print("\nBeispiel-Verwendungen:")
        print("\n1. Alle Frames verarbeiten (kurzes Video):")
        print("   result = client.detect_video('video.mp4', sampling_rate=1)")
        print("\n2. Jeden 5. Frame verarbeiten (mittleres Video):")
        print("   result = client.detect_video('video.mp4', sampling_rate=5)")
        print("\n3. Maximal 100 Frames (langes Video):")
        print("   result = client.detect_video('video.mp4', max_frames=100)")
        print("\n4. Hohe Confidence, jeden 10. Frame:")
        print("   result = client.detect_video('video.mp4', confidence_threshold=0.7, sampling_rate=10)")
        return

    print(f"\n{'='*70}")
    print(f"Processing video: {video_path}")
    print(f"{'='*70}")

    try:
        # Video Detection durchführen
        # Für kurze Videos (< 30 Sekunden): sampling_rate=1
        # Für mittlere Videos (30s - 2min): sampling_rate=3-5
        # Für lange Videos (> 2min): sampling_rate=10 oder max_frames=300

        result = client.detect_video(
            video_path=video_path,
            confidence_threshold=0.5,
            sampling_rate=5,  # Jeden 5. Frame verarbeiten
            return_detections_only=True  # Nur Frames mit Detections
        )

        # Ergebnisse anzeigen
        client.print_video_results(result, verbose=False)

        # Optional: Ergebnisse speichern
        output_path = "video_detection_results.json"
        with open(output_path, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"Results saved to: {output_path}")

    except requests.exceptions.RequestException as e:
        print(f"✗ Video detection failed: {e}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_detail = e.response.json()
                print(f"Error details: {error_detail}")
            except:
                print(f"Response: {e.response.text}")
    except FileNotFoundError:
        print(f"✗ Video not found: {video_path}")


if __name__ == "__main__":
    main()
