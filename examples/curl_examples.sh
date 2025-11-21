#!/bin/bash
# YOLOX API - cURL Examples

API_URL="http://localhost:8000"
API_BASE="${API_URL}/api/v1"

echo "YOLOX API - cURL Examples"
echo "=========================="
echo ""

# 1. Root endpoint
echo "1. Root Endpoint:"
echo "curl ${API_URL}/"
curl -s ${API_URL}/ | jq .
echo ""

# 2. Health Check
echo "2. Health Check:"
echo "curl ${API_BASE}/health"
curl -s ${API_BASE}/health | jq .
echo ""

# 3. Readiness Check
echo "3. Readiness Check:"
echo "curl ${API_BASE}/ready"
curl -s ${API_BASE}/ready | jq .
echo ""

# 4. Object Detection
echo "4. Object Detection:"
IMAGE_PATH="path/to/your/image.jpg"

if [ -f "${IMAGE_PATH}" ]; then
    echo "curl -X POST ${API_BASE}/detect \\"
    echo "  -F 'file=@${IMAGE_PATH}' \\"
    echo "  -F 'confidence_threshold=0.5'"

    curl -X POST "${API_BASE}/detect" \
      -F "file=@${IMAGE_PATH}" \
      -F "confidence_threshold=0.5" | jq .
else
    echo "⚠ Image not found: ${IMAGE_PATH}"
    echo "Please update IMAGE_PATH variable"
fi
echo ""

# 5. Object Detection with all parameters
echo "5. Object Detection with all parameters:"
if [ -f "${IMAGE_PATH}" ]; then
    echo "curl -X POST ${API_BASE}/detect \\"
    echo "  -F 'file=@${IMAGE_PATH}' \\"
    echo "  -F 'confidence_threshold=0.5' \\"
    echo "  -F 'nms_threshold=0.45' \\"
    echo "  -F 'input_size=640'"

    curl -X POST "${API_BASE}/detect" \
      -F "file=@${IMAGE_PATH}" \
      -F "confidence_threshold=0.5" \
      -F "nms_threshold=0.45" \
      -F "input_size=640" | jq .
fi
echo ""

# 6. Prometheus Metrics
echo "6. Prometheus Metrics:"
echo "curl ${API_BASE}/metrics"
curl -s ${API_BASE}/metrics | head -20
echo "..."
echo ""

# 7. OpenAPI Schema
echo "7. OpenAPI Schema:"
echo "curl ${API_URL}/openapi.json"
curl -s ${API_URL}/openapi.json | jq '.info'
echo ""

echo "=========================="
echo "For interactive API documentation, visit:"
echo "  Swagger UI: ${API_URL}/docs"
echo "  ReDoc:      ${API_URL}/redoc"
