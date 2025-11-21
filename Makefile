.PHONY: help install dev-install test run docker-build docker-run clean

help:
	@echo "YOLOX API - Available commands:"
	@echo ""
	@echo "  make install        - Install production dependencies"
	@echo "  make dev-install    - Install development dependencies"
	@echo "  make run            - Run API locally"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run Docker container"
	@echo "  make docker-stop    - Stop Docker container"
	@echo "  make k8s-deploy     - Deploy to Kubernetes"
	@echo "  make k8s-delete     - Delete from Kubernetes"
	@echo "  make test           - Run tests"
	@echo "  make clean          - Clean up generated files"
	@echo ""

install:
	pip install -r requirements.txt

dev-install: install
	pip install pytest pytest-cov black flake8 mypy

run:
	python -m app.main

run-dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

docker-build:
	docker build -t yolox-api:latest .

docker-run:
	docker-compose up -d

docker-stop:
	docker-compose down

docker-logs:
	docker-compose logs -f

k8s-deploy:
	kubectl apply -f k8s/deployment.yaml
	kubectl apply -f k8s/hpa.yaml
	kubectl apply -f k8s/ingress.yaml

k8s-delete:
	kubectl delete -f k8s/ingress.yaml
	kubectl delete -f k8s/hpa.yaml
	kubectl delete -f k8s/deployment.yaml

k8s-status:
	kubectl get pods -l app=yolox-api
	kubectl get svc yolox-api-service
	kubectl get hpa yolox-api-hpa

test:
	pytest tests/ -v --cov=app

format:
	black app/

lint:
	flake8 app/
	mypy app/

clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf build/ dist/ .pytest_cache/ .coverage htmlcov/
