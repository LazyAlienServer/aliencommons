# Pull Base Image
FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Set Environment Variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PATH="/code/.venv/bin:$PATH"

WORKDIR /code

# Install Dependencies
COPY ./pyproject.toml ./uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# Copy Project
COPY . .
