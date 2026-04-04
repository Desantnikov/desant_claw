FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_UNMANAGED_INSTALL=/usr/local/bin \
    PATH="/app/.venv/bin:/usr/local/bin:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

COPY . .

RUN uv sync --frozen --no-dev

EXPOSE 8000

CMD ["uv", "run", "python", "main.py"]