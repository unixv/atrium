.PHONY: dev up down logs check frontend-check backend-check sprites clean

# Beginner-friendly project commands.
dev up:
	docker compose up --build

down:
	docker compose down

logs:
	docker compose logs -f server web mongo

check: frontend-check backend-check

frontend-check:
	cd frontend && npm install && npm run build

backend-check:
	cd backend && python -m compileall atrium

sprites:
	python scripts/extract_reference_assets.py

clean:
	rm -rf frontend/dist frontend/node_modules backend/atrium/__pycache__ backend/atrium/**/__pycache__
