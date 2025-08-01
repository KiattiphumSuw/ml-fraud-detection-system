env:
	source /Users/kunnger/Library/Caches/pypoetry/virtualenvs/ml-fraud-detection-system-29_Yfvww-py3.12/bin/activate
run:
	uvicorn server:app --host 0.0.0.0 --port 8080 --reload
build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

start: build up
	@echo "✅ initialized DB, built images, and brought containers up"