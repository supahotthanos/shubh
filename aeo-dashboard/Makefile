.PHONY: bootstrap migrate seed dev test lint down

bootstrap:
	docker compose up -d postgres redis

migrate:
	cd backend && alembic upgrade head

seed:
	cd backend && python -m scripts.seed

dev:
	docker compose up

down:
	docker compose down

test:
	cd backend && pytest -q

lint:
	cd frontend && npm run lint
