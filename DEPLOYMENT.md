# Deployment Guide

Dieser Guide beschreibt verschiedene Deployment-Szenarien für die YOLOX API.

## 📋 Inhaltsverzeichnis

1. [Lokales Development](#lokales-development)
2. [Docker Deployment](#docker-deployment)
3. [Kubernetes Deployment](#kubernetes-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Best Practices](#production-best-practices)

## Lokales Development

### Quick Start

```bash
# Virtual Environment erstellen
python -m venv venv
source venv/bin/activate

# Dependencies installieren
pip install -r requirements.txt

# Environment-Variablen setzen
cp .env.example .env
# .env bearbeiten

# API starten
python -m app.main
```

### Mit Auto-Reload (Development)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Docker Deployment

### Single Container

```bash
# Image bauen
docker build -t yolox-api:latest .

# Container starten
docker run -d \
  --name yolox-api \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -e DEVICE=cpu \
  yolox-api:latest
```

### Mit GPU-Support

```bash
docker run -d \
  --name yolox-api \
  --gpus all \
  -p 8000:8000 \
  -v $(pwd)/models:/app/models:ro \
  -e DEVICE=cuda \
  yolox-api:latest
```

### Docker Compose

```bash
# Starten
docker-compose up -d

# Skalieren
docker-compose up -d --scale yolox-api=3

# Mit Nginx Load Balancer
docker-compose --profile with-nginx up -d

# Logs
docker-compose logs -f

# Stoppen
docker-compose down
```

## Kubernetes Deployment

### Voraussetzungen

```bash
# Kubectl installiert und konfiguriert
kubectl version

# Optional: Helm installiert
helm version
```

### Deployment Steps

#### 1. Model Weights bereitstellen

```bash
# PersistentVolume erstellen (Beispiel für lokales Storage)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: PersistentVolume
metadata:
  name: yolox-models-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadOnlyMany
  hostPath:
    path: /path/to/models
EOF

# PVC wird durch deployment.yaml erstellt
```

#### 2. Deployment

```bash
# Alle Ressourcen deployen
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/hpa.yaml
kubectl apply -f k8s/ingress.yaml

# Status prüfen
kubectl get all -l app=yolox-api
```

#### 3. Ingress konfigurieren

```bash
# Domain in ingress.yaml anpassen
# Dann erneut anwenden
kubectl apply -f k8s/ingress.yaml

# Ingress Status
kubectl get ingress yolox-api-ingress
```

### GPU Nodes

Für GPU-Support in Kubernetes:

```yaml
# In deployment.yaml unter resources:
resources:
  limits:
    nvidia.com/gpu: 1
```

```bash
# GPU-Operator installieren (falls nicht vorhanden)
helm install --wait --generate-name \
  -n gpu-operator --create-namespace \
  nvidia/gpu-operator
```

### Scaling

```bash
# Manual Scaling
kubectl scale deployment yolox-api --replicas=5

# HPA Status
kubectl get hpa yolox-api-hpa

# HPA Details
kubectl describe hpa yolox-api-hpa
```

## Cloud Deployment

### AWS EKS

```bash
# EKS Cluster erstellen
eksctl create cluster --name yolox-cluster --region us-west-2

# Kubectl Context setzen
aws eks update-kubeconfig --region us-west-2 --name yolox-cluster

# ALB Ingress Controller installieren
kubectl apply -k "github.com/aws/eks-charts/stable/aws-load-balancer-controller//crds?ref=master"

# Deployment
kubectl apply -f k8s/
```

### Google GKE

```bash
# GKE Cluster erstellen
gcloud container clusters create yolox-cluster \
  --zone us-central1-a \
  --num-nodes 3

# Credentials holen
gcloud container clusters get-credentials yolox-cluster

# Deployment
kubectl apply -f k8s/
```

### Azure AKS

```bash
# AKS Cluster erstellen
az aks create \
  --resource-group yolox-rg \
  --name yolox-cluster \
  --node-count 3 \
  --generate-ssh-keys

# Credentials holen
az aks get-credentials --resource-group yolox-rg --name yolox-cluster

# Deployment
kubectl apply -f k8s/
```

### Heroku (Einfaches Deployment)

```bash
# Heroku CLI installieren und einloggen
heroku login

# App erstellen
heroku create yolox-api

# Container Registry nutzen
heroku container:login
heroku container:push web
heroku container:release web

# Logs
heroku logs --tail
```

## Production Best Practices

### 1. Secrets Management

```bash
# Kubernetes Secrets
kubectl create secret generic yolox-secrets \
  --from-literal=api-key=your-secret-key

# In deployment.yaml referenzieren
env:
- name: API_KEY
  valueFrom:
    secretKeyRef:
      name: yolox-secrets
      key: api-key
```

### 2. Monitoring Setup

#### Prometheus

```bash
# Prometheus Operator installieren
kubectl create -f https://raw.githubusercontent.com/prometheus-operator/prometheus-operator/main/bundle.yaml

# ServiceMonitor erstellen
cat <<EOF | kubectl apply -f -
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: yolox-api-monitor
spec:
  selector:
    matchLabels:
      app: yolox-api
  endpoints:
  - port: http
    path: /api/v1/metrics
EOF
```

#### Grafana Dashboard

```bash
# Grafana installieren
helm install grafana grafana/grafana

# Dashboard importieren (erstellen Sie ein Custom Dashboard)
```

### 3. Logging

```bash
# Fluentd für Log-Aggregation
kubectl apply -f https://raw.githubusercontent.com/fluent/fluentd-kubernetes-daemonset/master/fluentd-daemonset-elasticsearch.yaml
```

### 4. SSL/TLS

```bash
# Cert-Manager installieren
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# ClusterIssuer erstellen
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF
```

### 5. Backup & Recovery

```bash
# Velero für Cluster Backups
velero install --provider aws --bucket your-backup-bucket

# Backup erstellen
velero backup create yolox-backup --include-namespaces default
```

### 6. Rate Limiting

Nginx Ingress mit Rate Limiting:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: yolox-api-ingress
  annotations:
    nginx.ingress.kubernetes.io/rate-limit: "100"
    nginx.ingress.kubernetes.io/limit-rps: "10"
```

### 7. Health Checks

```yaml
# In deployment.yaml
livenessProbe:
  httpGet:
    path: /api/v1/health
    port: 8000
  initialDelaySeconds: 60
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /api/v1/ready
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
```

## Performance Tuning

### 1. Worker Konfiguration

```bash
# Für CPU-intensive Tasks
export API_WORKERS=$(($(nproc) * 2 + 1))

# Für GPU (1 Worker pro GPU)
export API_WORKERS=1
```

### 2. Resource Limits

```yaml
# Optimale Resource Limits
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### 3. Connection Pooling

```python
# In main.py
uvicorn.run(
    "app.main:app",
    host="0.0.0.0",
    port=8000,
    workers=4,
    limit_concurrency=100,
    backlog=2048
)
```

## Troubleshooting

### Container startet nicht

```bash
# Logs prüfen
kubectl logs -l app=yolox-api
docker logs yolox-api

# Events prüfen
kubectl describe pod <pod-name>
```

### OOM (Out of Memory)

```bash
# Memory Limits erhöhen
kubectl set resources deployment yolox-api --limits=memory=8Gi

# Oder Worker reduzieren
kubectl set env deployment/yolox-api API_WORKERS=2
```

### Slow Response Times

```bash
# HPA Metriken prüfen
kubectl top pods -l app=yolox-api

# Scaling trigger prüfen
kubectl describe hpa yolox-api-hpa

# Mehr Replicas
kubectl scale deployment yolox-api --replicas=5
```

## Rollback

```bash
# Kubernetes Rollback
kubectl rollout undo deployment/yolox-api

# Zu spezifischer Revision
kubectl rollout undo deployment/yolox-api --to-revision=2

# Rollout Status
kubectl rollout status deployment/yolox-api
```

## Update Strategy

```yaml
# Zero-downtime Rolling Update
spec:
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0
```

```bash
# Neues Image deployen
kubectl set image deployment/yolox-api yolox-api=yolox-api:v2.0.0
```
