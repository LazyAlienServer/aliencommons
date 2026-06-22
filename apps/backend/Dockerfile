# Pull Base Image
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV AUTOBAHN_USE_NVX=0
ENV PATH="/code/.venv/bin:$PATH"

WORKDIR /code

# Install Dependencies
COPY ./pyproject.toml ./uv.lock ./
COPY ./apps/backend/pyproject.toml ./apps/backend/pyproject.toml
COPY ./docs/alienmark/pyproject.toml ./docs/alienmark/pyproject.toml
COPY ./docs/contributors/pyproject.toml ./docs/contributors/pyproject.toml
COPY ./docs/users/pyproject.toml ./docs/users/pyproject.toml
RUN uv sync --locked --no-dev --no-install-workspace --package aliencommons-backend

# Copy Project
COPY . .

WORKDIR /code/apps/backend
