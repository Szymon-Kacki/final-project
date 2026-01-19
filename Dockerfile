# lightweight base image
FROM python:3.12-slim

# set environment variables to improve runtime
# PYTHONDONTWRITEBYTECODE: prevents Python from writing .pyc files to disk
# PYTHONUNBUFFERED: ensures that Python output is sent straight to terminal w/o being buffered
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# set working directory
WORKDIR /app

# install system dependencies in a single layer
# --no-install-recommends to get only essential packages
# no leftover files thanks to apt-get clean and removing /var/lib/apt/lists/*
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# copy and install python dependencies separately to improve caching
# (if only application code changes, dependencies layer can be reused)
# --no-cache-dir prevents pip from caching packages locally
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# copy project files
COPY . .

# expose the application port
EXPOSE 8000

# set the default command to run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]