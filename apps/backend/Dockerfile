# Pull Base Image
FROM python:3.14-slim

# Set Environment Variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install Dependencies
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# Copy Project
COPY . .
