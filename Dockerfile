# DockerForge Dockerfile
# A comprehensive Docker management tool with AI-powered troubleshooting

# Use a multi-stage build for smaller image size
FROM python:3.10-slim AS builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Build the package
RUN pip install --no-cache-dir -e .

# Final stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy built package from builder stage
COPY --from=builder /app /app
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Create volume for data persistence
VOLUME /app/data

# Create volume for configuration
VOLUME /app/config

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DOCKERFORGE_CONFIG_PATH=/app/config/dockerforge.yaml \
    DOCKERFORGE_DATA_DIR=/app/data

# Expose port for potential web interface
EXPOSE 8080

# Set entrypoint
ENTRYPOINT ["python", "-m", "src.cli"]

# Set default command
CMD ["--help"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m src.cli check || exit 1

# Metadata
LABEL maintainer="DockerForge Team <info@dockerforge.example.com>" \
      version="0.1.0" \
      description="A comprehensive Docker management tool with AI-powered troubleshooting"
