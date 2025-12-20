# Stage 1: Build the frontend
FROM node:20-slim AS frontend-builder
WORKDIR /src
# Install frontend dependencies
COPY frontend/package*.json ./
RUN npm ci
# Copy the rest of the frontend source
COPY frontend/ ./
# Build the static assets
RUN npm run build

# Stage 2: Python runtime for the backend
FROM python:3.11-slim
# System dependencies for WeasyPrint and other libs
RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    python3-pip \
    python3-setuptools \
    python3-wheel \
    python3-cffi \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fonts-liberation \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
# Install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything from backend/ into /app/backend
COPY backend/ ./backend/

# Copy the built frontend assets into the appropriate location in the backend
COPY --from=frontend-builder /src/dist ./backend/frontend/dist

# Set PYTHONPATH to /app so that 'from backend.xxx import' works
ENV PYTHONPATH=/app

WORKDIR /app/backend

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
