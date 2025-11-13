.PHONY: help build up down logs test clean

help:
	@echo "Available commands:"
	@echo "  make build     - Build Docker containers"
	@echo "  make up        - Start all services"
	@echo "  make down      - Stop all services"
	@echo "  make logs      - View logs"
	@echo "  make test      - Run tests"
	@echo "  make clean     - Clean up"

build:
	docker-compose build

up:
	docker-compose up -d
	@echo "Services started!"
	@echo "Backend: http://localhost:8000"
	@echo "Frontend: http://localhost:3000"
	@echo "API Docs: http://localhost:8000/docs"

down:
	docker-compose down

logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-worker:
	docker-compose logs -f worker

test:
	docker-compose exec backend pytest tests/

clean:
	docker-compose down -v
	docker system prune -f

restart:
	docker-compose restart

migrate:
	docker-compose exec backend python scripts/migrate.py

seed:
	docker-compose exec backend python scripts/seed_data.py

shell-backend:
	docker-compose exec backend bash

shell-db:
	docker-compose exec postgres psql -U user -d ocr_db