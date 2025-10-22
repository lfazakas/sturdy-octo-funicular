lint:
	poetry run flake8 app/ tests/
	poetry run mypy app/

format:
	poetry run black app/ tests/ scripts/
	poetry run isort app/ tests/ scripts/

test:
	poetry run pytest

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

clean:
	docker-compose down -v
	docker system prune -f

restart:
	docker-compose restart
	
