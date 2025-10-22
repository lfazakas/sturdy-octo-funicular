FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc && rm -rf /var/lib/apt/lists/*

RUN pip install poetry
RUN poetry config virtualenvs.in-project true \
    && poetry config cache-dir /tmp/poetry_cache

COPY pyproject.toml poetry.lock* README.md ./
COPY app/ ./app/

RUN poetry install --only=main --no-root && rm -rf $POETRY_CACHE_DIR

ENV PATH="/app/.venv/bin:$PATH"

RUN useradd --create-home --shell /bin/bash app && chown -R app:app /app
USER app

EXPOSE 8000

CMD ["poetry", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
