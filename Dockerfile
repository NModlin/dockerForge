# Stage 1: Build Vue.js frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/frontend
COPY src/web/frontend/package*.json ./
RUN npm install
COPY src/web/frontend/ ./
RUN npm run build

# Stage 2: Python dependencies and application build
FROM python:3.10-slim AS builder
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install main app dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Install web API dependencies
COPY src/web/api/requirements.txt web-requirements.txt
RUN pip install --no-cache-dir -r web-requirements.txt

# Build the main package
COPY . .
RUN pip install --no-cache-dir -e .

# Final stage
FROM python:3.10-slim
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy built packages from builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy frontend build
COPY --from=frontend-builder /app/frontend/dist /app/static

# Create necessary directories and volumes
RUN mkdir -p /app/data /app/config /app/media /app/logs

# Create symbolic link for API
RUN ln -s /app/src/web/api /app/api
VOLUME /app/data
VOLUME /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKERFORGE_CONFIG_PATH=/app/config/dockerforge.yaml \
    DOCKERFORGE_DATA_DIR=/app/data

# Expose both ports
EXPOSE 8080 54321

# Copy supervisor configuration to manage multiple processes
COPY docker-entrypoint.sh /docker-entrypoint.sh
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
RUN chmod +x /docker-entrypoint.sh

# Set entrypoint
ENTRYPOINT ["/docker-entrypoint.sh"]

# Default command (can be overridden)
CMD ["all"]

# Metadata
LABEL maintainer="DockerForge Team <info@dockerforge.example.com>" \
      version="0.1.0" \
      description="DockerForge - All-in-one Docker management tool with web UI"
