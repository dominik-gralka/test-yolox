# YOLOX Model Setup Guide

Anleitung zum Herunterladen und Einrichten der YOLOX-Modellgewichte.

## 📥 Modellgewichte herunterladen

YOLOX bietet verschiedene Modellvarianten mit unterschiedlicher Größe und Performance:

| Modell | Größe | APval | Speed (V100) | Params | FLOPs | Weights |
|--------|-------|-------|--------------|--------|-------|---------|
| YOLOX-Nano | 416 | 25.8 | 0.91ms | 0.91M | 1.08G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth) |
| YOLOX-Tiny | 416 | 32.8 | 1.28ms | 5.06M | 6.45G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth) |
| YOLOX-S | 640 | 40.5 | 2.61ms | 9.0M | 26.8G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth) |
| YOLOX-M | 640 | 46.9 | 4.88ms | 25.3M | 73.8G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.pth) |
| YOLOX-L | 640 | 49.7 | 7.93ms | 54.2M | 155.6G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_l.pth) |
| YOLOX-X | 640 | 51.1 | 12.61ms | 99.1M | 281.9G | [Download](https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_x.pth) |

## 🚀 Schnellstart

### 1. Modell herunterladen

**Empfohlen: YOLOX-S** (gute Balance zwischen Speed und Accuracy)

```bash
# Via wget
cd models/
wget https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth

# Oder via curl
curl -L -o models/yolox_s.pth https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth
```

### 2. Konfiguration anpassen

Erstellen oder bearbeiten Sie `.env`:

```bash
cp .env.example .env
```

In `.env` anpassen:
```bash
MODEL_NAME=yolox-s
MODEL_PATH=./models/yolox_s.pth
DEVICE=cuda  # oder 'cpu'
```

### 3. API starten

```bash
# Lokal
python -m app.main

# Oder mit Docker
docker-compose up -d
```

## 📋 Alle Modelle herunterladen

Script zum Download aller Modelle:

```bash
#!/bin/bash
# download_models.sh

cd models/

echo "Downloading YOLOX models..."

# YOLOX-Nano (fastest, lowest accuracy)
echo "Downloading YOLOX-Nano..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_nano.pth

# YOLOX-Tiny
echo "Downloading YOLOX-Tiny..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_tiny.pth

# YOLOX-S (recommended)
echo "Downloading YOLOX-S..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth

# YOLOX-M
echo "Downloading YOLOX-M..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.pth

# YOLOX-L
echo "Downloading YOLOX-L..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_l.pth

# YOLOX-X (best accuracy, slowest)
echo "Downloading YOLOX-X..."
wget -nc https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_x.pth

echo "✓ All models downloaded!"
ls -lh *.pth
```

Ausführen:
```bash
chmod +x download_models.sh
./download_models.sh
```

## 🎯 Modellauswahl

### Nach Anwendungsfall

**Real-time Video (30+ FPS)**
- CPU: YOLOX-Nano oder YOLOX-Tiny
- GPU: YOLOX-S

**High Accuracy (Surveillance, Analytics)**
- YOLOX-L oder YOLOX-X

**Balance (Empfohlen für die meisten Fälle)**
- YOLOX-S oder YOLOX-M

### Nach Hardware

**CPU-only**
```bash
MODEL_NAME=yolox-nano  # oder yolox-tiny
DEVICE=cpu
```

**GPU (z.B. RTX 3060)**
```bash
MODEL_NAME=yolox-s  # oder yolox-m
DEVICE=cuda
```

**High-end GPU (z.B. RTX 4090, A100)**
```bash
MODEL_NAME=yolox-l  # oder yolox-x
DEVICE=cuda
```

## 🔄 Modell wechseln

Um zwischen Modellen zu wechseln:

1. **Neues Modell herunterladen** (falls noch nicht vorhanden)
2. **.env anpassen**:
   ```bash
   MODEL_NAME=yolox-m
   MODEL_PATH=./models/yolox_m.pth
   ```
3. **API neu starten**:
   ```bash
   # Lokal
   # Strg+C und dann:
   python -m app.main

   # Docker
   docker-compose restart
   ```

## 🎓 Eigenes Modell trainieren

### YOLOX auf eigenen Daten trainieren

1. **YOLOX Repository klonen**:
   ```bash
   git clone https://github.com/Megvii-BaseDetection/YOLOX.git
   cd YOLOX
   pip install -v -e .
   ```

2. **Daten vorbereiten** (COCO-Format):
   ```
   your_dataset/
   ├── annotations/
   │   ├── instances_train.json
   │   └── instances_val.json
   └── images/
       ├── train/
       └── val/
   ```

3. **Training starten**:
   ```bash
   python tools/train.py -f exps/default/yolox_s.py -d 1 -b 8 --fp16 \
       -o --data_dir /path/to/your_dataset
   ```

4. **Trainierte Weights verwenden**:
   ```bash
   # Weights nach models/ kopieren
   cp YOLOX_outputs/yolox_s/latest_ckpt.pth ../yolox-api/models/my_custom_model.pth

   # In .env konfigurieren
   MODEL_NAME=yolox-s
   MODEL_PATH=./models/my_custom_model.pth
   ```

### Custom Dataset mit anderen Klassen

Wenn Ihr Modell nicht COCO-Klassen verwendet:

1. **COCO_CLASSES in `app/services/inference.py` anpassen**:
   ```python
   COCO_CLASSES = [
       "my_class_1",
       "my_class_2",
       "my_class_3",
       # ... Ihre Klassen
   ]
   ```

2. **Anzahl der Klassen in config anpassen**:
   ```bash
   # In .env (wird derzeit nicht verwendet, aber für Zukunft)
   NUM_CLASSES=10  # Ihre Anzahl
   ```

## 🧪 Testen der Installation

### 1. Lokales Testen

```python
# test_model.py
import torch
from app.core.model_manager import get_model_manager

# Model laden
manager = get_model_manager()
manager.load_model(
    model_path="./models/yolox_s.pth",
    device="cuda",  # oder "cpu"
    model_name="yolox-s"
)

print("✓ Model erfolgreich geladen!")
print(f"  Device: {manager.get_device()}")
print(f"  Model: {manager.get_model()}")
```

Ausführen:
```bash
python test_model.py
```

### 2. API-Testen mit Beispielbild

```bash
# Beispielbild herunterladen
wget https://raw.githubusercontent.com/Megvii-BaseDetection/YOLOX/main/assets/dog.jpg

# API starten (in einem Terminal)
python -m app.main

# In einem anderen Terminal: Detection testen
curl -X POST "http://localhost:8000/api/v1/detect" \
  -F "file=@dog.jpg" \
  -F "confidence_threshold=0.5"
```

## 🐛 Troubleshooting

### "Model weights not found"

```bash
# Prüfen ob Datei existiert
ls -lh models/yolox_s.pth

# Falls nicht: Herunterladen
wget -P models/ https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_s.pth
```

### "YOLOX not installed"

```bash
# YOLOX installieren
pip install git+https://github.com/Megvii-BaseDetection/YOLOX.git

# Oder aus requirements.txt
pip install -r requirements.txt
```

### CUDA Out of Memory

```bash
# Kleineres Modell verwenden
MODEL_NAME=yolox-s  # statt yolox-l

# Oder auf CPU wechseln
DEVICE=cpu
```

### Langsame Inferenz auf CPU

```bash
# Kleinste Modelle verwenden
MODEL_NAME=yolox-nano

# Oder INPUT_SIZE reduzieren
INPUT_SIZE=416  # statt 640
```

## 📊 Performance Benchmarks

Gemessen auf verschiedener Hardware mit YOLOX-S:

| Hardware | Inferenzzeit | FPS | Empfehlung |
|----------|-------------|-----|------------|
| CPU (i7-10700) | ~200ms | 5 | Nano/Tiny verwenden |
| GPU (GTX 1660) | ~15ms | 66 | ✓ Gut |
| GPU (RTX 3060) | ~8ms | 125 | ✓ Sehr gut |
| GPU (RTX 4090) | ~3ms | 333 | ✓ Exzellent |

## 📚 Weitere Ressourcen

- [YOLOX GitHub](https://github.com/Megvii-BaseDetection/YOLOX)
- [YOLOX Paper](https://arxiv.org/abs/2107.08430)
- [YOLOX Releases](https://github.com/Megvii-BaseDetection/YOLOX/releases)
- [Training Guide](https://github.com/Megvii-BaseDetection/YOLOX/blob/main/docs/train_custom_data.md)

## 💼 Kommerzielle Nutzung

YOLOX ist unter Apache 2.0 Lizenz veröffentlicht, was kommerzielle Nutzung erlaubt.

**Wichtig**: Prüfen Sie die Lizenzen der verwendeten Trainingsdaten:
- COCO Dataset: [Terms of Use](https://cocodataset.org/#termsofuse)
- Eigene Daten: Stellen Sie sicher, dass Sie die Rechte haben
