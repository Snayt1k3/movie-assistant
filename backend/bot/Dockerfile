FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /backend
COPY pyproject.toml uv.lock* ./
COPY common ./common
COPY bot ./bot
RUN uv sync --package bot --no-dev

ENV PATH="/backend/.venv/bin:$PATH"
WORKDIR /backend/bot
CMD ["python", "main.py"]
