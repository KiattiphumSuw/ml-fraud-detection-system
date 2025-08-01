init:
	python3.12 -m venv .venv

activate:
	source .venv/bin/activate

run:
	uvicorn server:app --host 0.0.0.0 --port 8080 --reload

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

start: build up
	@echo "initialized DB, built images, and brought containers up"