FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /backend
COPY pyproject.toml uv.lock* ./
COPY common ./common
COPY cron ./cron
RUN uv sync --package cron --no-dev

ENV PATH="/backend/.venv/bin:$PATH"
WORKDIR /backend/cron
CMD ["python", "main.py"]
