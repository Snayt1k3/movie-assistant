FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /backend
COPY pyproject.toml uv.lock* ./
COPY common ./common
COPY api ./api
RUN uv sync --package api --no-dev

ENV PATH="/backend/.venv/bin:$PATH"
WORKDIR /backend/api
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
