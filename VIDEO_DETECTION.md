# Video Object Detection Guide

Umfassender Guide zur Nutzung der Video-Detection-Funktionalität der YOLOX API.

## 🎬 Übersicht

Die YOLOX API kann Videos Frame-für-Frame verarbeiten und Object Detection auf jedem Frame durchführen. Dies ist ideal für:

- Überwachungsvideos analysieren
- Objekte in Videos tracken
- Automatische Video-Annotation
- Content-Analyse und Moderation
- Sport-Analytics
- Verkehrsüberwachung

## 📋 Unterstützte Formate

Die API unterstützt alle gängigen Video-Formate:

- **MP4** (empfohlen, H.264/H.265)
- **AVI**
- **MOV**
- **MKV**
- **WEBM**
- **FLV**

Prüfen Sie unterstützte Formate über:
```bash
curl http://localhost:8000/api/v1/detect/video/formats
```

## 🚀 Grundlegende Nutzung

### Einfaches Beispiel

```bash
curl -X POST "http://localhost:8000/api/v1/detect/video" \
  -F "file=@video.mp4"
```

### Mit Parametern

```bash
curl -X POST "http://localhost:8000/api/v1/detect/video" \
  -F "file=@video.mp4" \
  -F "confidence_threshold=0.5" \
  -F "sampling_rate=5" \
  -F "max_frames=300"
```

## ⚙️ Parameter

| Parameter | Typ | Default | Beschreibung |
|-----------|-----|---------|--------------|
| `file` | File | **Required** | Video-Datei |
| `confidence_threshold` | float | 0.3 | Minimale Confidence (0.0-1.0) |
| `nms_threshold` | float | 0.45 | NMS-Schwellenwert (0.0-1.0) |
| `input_size` | int | 640 | Model Input Size |
| `sampling_rate` | int | 1 | Jeden Nth Frame verarbeiten |
| `max_frames` | int | None | Maximum Anzahl Frames |
| `return_detections_only` | bool | true | Nur Frames mit Detections zurückgeben |

## 📊 Response Format

```json
{
  "success": true,
  "video_info": {
    "width": 1920,
    "height": 1080,
    "fps": 30.0,
    "total_frames": 900,
    "duration_sec": 30.0
  },
  "total_frames": 180,
  "frames_with_detections": 156,
  "processing_time_ms": 8450.2,
  "avg_fps": 21.3,
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
```

## 🎯 Performance-Optimierung

### Sampling Rate

Der `sampling_rate` Parameter bestimmt, welche Frames verarbeitet werden:

- `sampling_rate=1`: Alle Frames (Standard)
- `sampling_rate=2`: Jeden 2. Frame (50% schneller)
- `sampling_rate=5`: Jeden 5. Frame (80% schneller)
- `sampling_rate=10`: Jeden 10. Frame (90% schneller)

**Empfehlungen:**

| Video-Länge | Empfohlener `sampling_rate` |
|-------------|----------------------------|
| < 10 Sekunden | 1-2 |
| 10-30 Sekunden | 2-3 |
| 30s-2 Minuten | 3-5 |
| 2-5 Minuten | 5-10 |
| > 5 Minuten | 10-30 + `max_frames` |

### Max Frames Limit

Für sehr lange Videos, nutzen Sie `max_frames`:

```python
# Verarbeite nur die ersten 10 Sekunden eines 30fps Videos
data = {
    "max_frames": 300,  # 300 frames = 10 seconds at 30fps
    "sampling_rate": 1
}
```

### Return Detections Only

Reduzieren Sie die Response-Größe deutlich:

```python
# Nur Frames mit Detections zurückgeben
data = {
    "return_detections_only": True  # Default
}

# Alle Frames zurückgeben (auch leere)
data = {
    "return_detections_only": False
}
```

## 💡 Verwendungsbeispiele

### 1. Überwachungsvideo analysieren

```python
import requests

# 24-Stunden Überwachungsvideo, nur wichtige Frames
files = {"file": open("surveillance_24h.mp4", "rb")}
data = {
    "confidence_threshold": 0.7,  # Hohe Confidence
    "sampling_rate": 30,           # Jeden 30. Frame (1 fps bei 30fps Video)
    "return_detections_only": True # Nur interessante Frames
}

response = requests.post(
    "http://localhost:8000/api/v1/detect/video",
    files=files,
    data=data
)
result = response.json()

# Zeitstempel mit Detections extrahieren
for frame in result['frame_detections']:
    timestamp = frame['timestamp_ms'] / 1000  # Sekunden
    print(f"Activity at {timestamp:.1f}s: {frame['num_detections']} objects")
```

### 2. Sport-Video analysieren

```python
# Fußball-Spiel: Spieler tracken
files = {"file": open("football_match.mp4", "rb")}
data = {
    "confidence_threshold": 0.5,
    "sampling_rate": 5,  # Jeden 5. Frame (~6fps bei 30fps)
    "return_detections_only": False  # Alle Frames für kontinuierliches Tracking
}

response = requests.post(
    "http://localhost:8000/api/v1/detect/video",
    files=files,
    data=data
)
result = response.json()

# Spieler-Bewegungen analysieren
person_counts = []
for frame in result['frame_detections']:
    num_persons = sum(1 for det in frame['detections'] if det['class_name'] == 'person')
    person_counts.append(num_persons)

avg_players = sum(person_counts) / len(person_counts)
print(f"Durchschnittlich {avg_players:.1f} Spieler im Frame")
```

### 3. Content Moderation

```python
# Video auf spezifische Objekte prüfen
files = {"file": open("user_upload.mp4", "rb")}
data = {
    "confidence_threshold": 0.6,
    "sampling_rate": 10,  # Schnelle Analyse
    "max_frames": 100,    # Begrenzt auf erste ~3 Sekunden
    "return_detections_only": True
}

response = requests.post(
    "http://localhost:8000/api/v1/detect/video",
    files=files,
    data=data
)
result = response.json()

# Prüfe auf bestimmte Objekte
restricted_objects = ['weapon', 'knife', 'gun']  # Beispiel
for frame in result['frame_detections']:
    for det in frame['detections']:
        if det['class_name'] in restricted_objects:
            timestamp = frame['timestamp_ms'] / 1000
            print(f"⚠ Warning: {det['class_name']} detected at {timestamp:.1f}s")
```

### 4. Verkehrsüberwachung

```python
# Fahrzeuge und Personen zählen
files = {"file": open("traffic_cam.mp4", "rb")}
data = {
    "confidence_threshold": 0.6,
    "sampling_rate": 15,  # 2fps bei 30fps Video
    "return_detections_only": False
}

response = requests.post(
    "http://localhost:8000/api/v1/detect/video",
    files=files,
    data=data
)
result = response.json()

# Statistiken erstellen
vehicle_classes = ['car', 'truck', 'bus', 'motorcycle', 'bicycle']
stats = {cls: 0 for cls in vehicle_classes}
stats['person'] = 0

for frame in result['frame_detections']:
    for det in frame['detections']:
        if det['class_name'] in stats:
            stats[det['class_name']] += 1

print("Verkehrsstatistik:")
for obj, count in stats.items():
    print(f"  {obj}: {count} Sichtungen")
```

## 🔧 Python Client

Nutzen Sie den mitgelieferten Client für einfachere Verwendung:

```python
from examples.video_client_example import YOLOXVideoClient

client = YOLOXVideoClient()

# Video verarbeiten
result = client.detect_video(
    video_path="video.mp4",
    confidence_threshold=0.5,
    sampling_rate=5
)

# Formatierte Ausgabe
client.print_video_results(result, verbose=True)
```

## ⚡ Performance-Benchmarks

Beispiel-Zeiten für ein 1080p 30fps Video auf verschiedener Hardware:

| Hardware | Frames/sec | 1min Video | Empfohlenes `sampling_rate` |
|----------|------------|------------|----------------------------|
| CPU (8 cores) | 2-5 fps | 6-15 min | 10-15 |
| GPU (RTX 3060) | 20-30 fps | 1-1.5 min | 3-5 |
| GPU (RTX 4090) | 50-80 fps | 22-36 sec | 1-2 |

## 🎓 Best Practices

### 1. Wählen Sie den richtigen Sampling Rate

```python
# Für statische Szenen (Überwachung)
sampling_rate = 30  # 1 fps ausreichend

# Für dynamische Szenen (Sport)
sampling_rate = 3   # ~10 fps für gutes Tracking

# Für schnelle Action
sampling_rate = 1   # Alle Frames
```

### 2. Setzen Sie angemessene Confidence

```python
# Hohe Precision (wenige False Positives)
confidence_threshold = 0.7

# Balance
confidence_threshold = 0.5

# Hohe Recall (alle Objekte finden)
confidence_threshold = 0.3
```

### 3. Begrenzen Sie lange Videos

```python
# Für Preview/Analyse: Erste 30 Sekunden
max_frames = 900  # 30 sec * 30 fps

# Für Monitoring: Jede Minute ein Sample
sampling_rate = 1800  # 1 frame pro 60 Sekunden bei 30fps
```

### 4. Speichern Sie Ergebnisse effizient

```python
import json

# Vollständige Ergebnisse
with open('results_full.json', 'w') as f:
    json.dump(result, f, indent=2)

# Nur Zusammenfassung
summary = {
    'video_info': result['video_info'],
    'total_frames': result['total_frames'],
    'frames_with_detections': result['frames_with_detections'],
    'processing_time_ms': result['processing_time_ms']
}
with open('results_summary.json', 'w') as f:
    json.dump(summary, f, indent=2)
```

## 🚨 Troubleshooting

### Video wird nicht akzeptiert

```
Error: Invalid file type
```

**Lösung**: Prüfen Sie Content-Type:
```bash
file video.mp4  # Sollte "video/mp4" oder ähnlich zeigen
```

### Verarbeitung zu langsam

```python
# Erhöhen Sie sampling_rate
sampling_rate = 10

# Oder setzen Sie max_frames
max_frames = 300
```

### Out of Memory

```python
# Reduzieren Sie Input Size
input_size = 416  # Statt 640

# Oder verarbeiten Sie in Chunks
for chunk in range(0, total_frames, 300):
    # Verarbeite jeweils 300 Frames
    pass
```

### Response zu groß

```python
# Nutzen Sie return_detections_only
return_detections_only = True

# Oder höheres sampling_rate
sampling_rate = 10
```

## 📚 Weitere Ressourcen

- [Vollständiger Python Client](../examples/video_client_example.py)
- [API Dokumentation](http://localhost:8000/docs#/Video%20Detection)
- [Performance Optimierung](../DEPLOYMENT.md#performance-tuning)

## 💼 Kommerzielle Nutzung

Für Production-Deployments:

1. **Async Processing**: Für lange Videos, implementieren Sie asynchrone Verarbeitung
2. **Caching**: Cachen Sie bereits verarbeitete Videos
3. **Storage**: Speichern Sie Ergebnisse in Datenbank statt in Response
4. **Webhooks**: Benachrichtigen Sie Clients wenn Verarbeitung fertig ist
5. **Rate Limiting**: Begrenzen Sie gleichzeitige Video-Verarbeitungen

Beispiel für asynchrone Verarbeitung wird in zukünftigen Versionen hinzugefügt.
