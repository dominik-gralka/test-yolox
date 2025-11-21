# YOLOX Object Detection API

Eine zustandslose und skalierbare REST API für YOLOX Object Detection, optimiert für kommerzielle Nutzung.

## 🚀 Features

- **Zustandslos (Stateless)**: Jede Anfrage ist unabhängig, ideal für Load Balancing
- **Horizontal skalierbar**: Einfaches Skalieren durch Hinzufügen von Containern/Pods
- **Production-ready**: Inklusive Health Checks, Monitoring und Logging
- **Docker & Kubernetes**: Vollständige Containerisierung und K8s-Manifeste
- **API-Dokumentation**: Automatische OpenAPI/Swagger-Dokumentation
- **Monitoring**: Prometheus-Metriken für Observability

## 📋 Voraussetzungen

- Python 3.10+
- Docker & Docker Compose (optional, empfohlen)
- CUDA-fähige GPU (optional, für bessere Performance)
- YOLOX Model Weights (z.B. `yolox_s.pth`)

## 🛠️ Installation

### Lokale Installation

```bash
# Repository klonen
git clone <repository-url>
cd test-yolox

# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder
venv\Scripts\activate  # Windows

# Dependencies installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env bearbeiten und anpassen

# Model Weights herunterladen
# Legen Sie Ihre YOLOX-Modellgewichte in den Ordner models/
# z.B. models/yolox_s.pth
```

### Docker Installation (Empfohlen)

```bash
# Repository klonen
git clone <repository-url>
cd test-yolox

# Model Weights bereitstellen
# Legen Sie Ihre YOLOX-Modellgewichte in den Ordner models/

# Container bauen und starten
docker-compose up -d

# Logs anzeigen
docker-compose logs -f
```

## 🚀 Quickstart

### Lokaler Start

```bash
# API starten
python -m app.main

# Oder mit Uvicorn (mehr Kontrolle)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Start

```bash
# Service starten
docker-compose up -d

# Mit Nginx Load Balancer
docker-compose --profile with-nginx up -d
```

### Kubernetes Deployment

```bash
# Manifeste anwenden
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Status prüfen
kubectl get pods -l app=yolox-api
kubectl get svc yolox-api-service
```

## 📖 API Verwendung

### Interaktive Dokumentation

Nach dem Start ist die API unter folgenden URLs erreichbar:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

### Beispiel: Object Detection

**cURL:**

```bash
curl -X POST "http://localhost:8000/api/v1/detect" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg" \
  -F "confidence_threshold=0.5"
```

**Python:**

```python
import requests

url = "http://localhost:8000/api/v1/detect"
files = {"file": open("image.jpg", "rb")}
params = {"confidence_threshold": 0.5}

response = requests.post(url, files=files, data=params)
result = response.json()

print(f"Detections: {result['num_detections']}")
for detection in result['detections']:
    print(f"- {detection['class_name']}: {detection['confidence']:.2f}")
```

**JavaScript/TypeScript:**

```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);
formData.append('confidence_threshold', '0.5');

const response = await fetch('http://localhost:8000/api/v1/detect', {
  method: 'POST',
  body: formData
});

const result = await response.json();
console.log(`Found ${result.num_detections} objects`);
```

### Response Format

```json
{
  "success": true,
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
  "num_detections": 1,
  "inference_time_ms": 45.2,
  "image_size": {
    "width": 640,
    "height": 480
  }
}
```

### Beispiel: Video Object Detection

Die API unterstützt auch Video-Verarbeitung! Videos werden Frame-für-Frame verarbeitet.

**cURL:**

```bash
# Einfache Video-Detection (alle Frames)
curl -X POST "http://localhost:8000/api/v1/detect/video" \
  -F "file=@/path/to/video.mp4" \
  -F "confidence_threshold=0.5"

# Optimiert für längere Videos (jeden 5. Frame)
curl -X POST "http://localhost:8000/api/v1/detect/video" \
  -F "file=@/path/to/video.mp4" \
  -F "sampling_rate=5" \
  -F "max_frames=300"
```

**Python:**

```python
import requests

# Kurzes Video: Alle Frames verarbeiten
files = {"file": open("short_video.mp4", "rb")}
data = {
    "confidence_threshold": 0.5,
    "sampling_rate": 1  # Alle Frames
}
response = requests.post("http://localhost:8000/api/v1/detect/video", files=files, data=data)
result = response.json()

# Langes Video: Jeden 10. Frame verarbeiten
files = {"file": open("long_video.mp4", "rb")}
data = {
    "confidence_threshold": 0.5,
    "sampling_rate": 10,  # Jeden 10. Frame
    "max_frames": 300,     # Max 300 Frames
    "return_detections_only": True  # Nur Frames mit Detections
}
response = requests.post("http://localhost:8000/api/v1/detect/video", files=files, data=data)
result = response.json()

print(f"Processed {result['total_frames']} frames")
print(f"Found detections in {result['frames_with_detections']} frames")
print(f"Processing speed: {result['avg_fps']:.2f} fps")
```

**Performance-Tipps für Videos:**
- **Kurze Videos (< 30s)**: `sampling_rate=1` (alle Frames)
- **Mittlere Videos (30s-2min)**: `sampling_rate=3-5`
- **Lange Videos (> 2min)**: `sampling_rate=10` oder `max_frames=300`
- Nutzen Sie `return_detections_only=true` für kleinere Responses

**Vollständiges Beispiel:**
```bash
# Siehe examples/video_client_example.py für einen kompletten Client
python examples/video_client_example.py
```

## 🔍 API Endpoints

| Endpoint | Methode | Beschreibung |
|----------|---------|--------------|
| `/` | GET | Service-Informationen |
| `/docs` | GET | Swagger UI Dokumentation |
| `/api/v1/detect` | POST | Object Detection auf einem Bild |
| `/api/v1/detect/video` | POST | Object Detection auf einem Video (Frame-für-Frame) |
| `/api/v1/detect/video/formats` | GET | Unterstützte Video-Formate anzeigen |
| `/api/v1/health` | GET | Health Check für Monitoring |
| `/api/v1/ready` | GET | Readiness Check für K8s |
| `/api/v1/metrics` | GET | Prometheus Metriken |

## ⚙️ Konfiguration

Konfiguration erfolgt über Umgebungsvariablen (siehe `.env.example`):

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_WORKERS=4

# Model Configuration
MODEL_NAME=yolox-s
MODEL_PATH=./models/yolox_s.pth
CONFIDENCE_THRESHOLD=0.3
NMS_THRESHOLD=0.45
INPUT_SIZE=640

# Performance
MAX_BATCH_SIZE=8
DEVICE=cuda  # oder 'cpu'

# Logging
LOG_LEVEL=INFO
```

## 📊 Monitoring & Observability

### Health Checks

```bash
# Liveness Check
curl http://localhost:8000/api/v1/health

# Readiness Check
curl http://localhost:8000/api/v1/ready
```

### Prometheus Metriken

```bash
# Metriken abrufen
curl http://localhost:8000/api/v1/metrics
```

Verfügbare Metriken:
- `yolox_detection_requests_total`: Gesamtzahl der Anfragen
- `yolox_detection_duration_seconds`: Inference-Dauer
- `yolox_active_requests`: Aktive Anfragen
- `yolox_model_info`: Model-Informationen

## 🔄 Skalierung

### Horizontales Skalieren mit Docker Compose

```bash
# Mehrere API-Instanzen starten
docker-compose up -d --scale yolox-api=3
```

### Autoscaling mit Kubernetes

Das HPA (Horizontal Pod Autoscaler) skaliert automatisch basierend auf:
- CPU-Auslastung (Ziel: 70%)
- Memory-Auslastung (Ziel: 80%)
- Min: 2 Pods, Max: 10 Pods

```bash
# HPA Status prüfen
kubectl get hpa yolox-api-hpa
```

### Load Balancing

#### Mit Nginx (Docker Compose)

```bash
docker-compose --profile with-nginx up -d
```

#### Mit Kubernetes Ingress

Automatisches Load Balancing über Kubernetes Service und Ingress.

## 🏗️ Architektur

### Stateless Design

- **Keine Session-Speicherung**: Jede Anfrage ist unabhängig
- **Singleton Model Manager**: Effiziente Ressourcennutzung pro Worker
- **Shared-Nothing**: Kein geteilter State zwischen Instanzen
- **12-Factor App**: Folgt Best Practices für Cloud-native Apps

### Komponenten

```
┌─────────────────┐
│  Load Balancer  │  (Nginx/K8s Ingress)
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───┐
│ API  │  │ API  │  (Horizontally scaled)
│ Pod 1│  │ Pod 2│
└───┬──┘  └──┬───┘
    │        │
    └────┬───┘
         │
    ┌────▼────┐
    │  Model  │  (Shared storage or baked into image)
    └─────────┘
```

## 🔐 Production Considerations

### Sicherheit

1. **API Keys**: Implementieren Sie API-Key-Authentifizierung
2. **Rate Limiting**: Nutzen Sie Nginx oder API Gateway für Rate Limits
3. **HTTPS**: Verwenden Sie TLS/SSL (siehe Ingress-Konfiguration)
4. **CORS**: Passen Sie CORS-Origins in Production an

### Performance

1. **GPU-Beschleunigung**: Setzen Sie `DEVICE=cuda` für GPU-Inferenz
2. **Batch Processing**: Nutzen Sie `/detect/batch` für mehrere Bilder
3. **Caching**: Implementieren Sie Redis für häufige Anfragen
4. **CDN**: Nutzen Sie CDN für statische Assets

### Monitoring

1. **Prometheus**: Integrieren Sie Prometheus für Metriken
2. **Grafana**: Erstellen Sie Dashboards für Visualisierung
3. **Logging**: Zentralisieren Sie Logs (ELK-Stack, Loki)
4. **Tracing**: Implementieren Sie OpenTelemetry

## 🐛 Troubleshooting

### API startet nicht

```bash
# Logs prüfen
docker-compose logs yolox-api

# Model-Pfad prüfen
ls -la models/

# Permissions prüfen
chmod 644 models/*.pth
```

### CUDA-Fehler

```bash
# CUDA-Verfügbarkeit prüfen
python -c "import torch; print(torch.cuda.is_available())"

# Auf CPU umschalten
export DEVICE=cpu
```

### Langsame Inferenz

1. GPU verwenden statt CPU
2. Input-Size reduzieren
3. Workers erhöhen
4. Horizontal skalieren

## 📚 Weitere Ressourcen

- [YOLOX GitHub](https://github.com/Megvii-BaseDetection/YOLOX)
- [FastAPI Dokumentation](https://fastapi.tiangolo.com/)
- [Kubernetes Best Practices](https://kubernetes.io/docs/concepts/configuration/overview/)

## 📄 Lizenz

Kommerzielles Projekt. Alle Rechte vorbehalten.

## 🤝 Support

Für Support und Anfragen kontaktieren Sie bitte das Entwicklungsteam.
