# Multi-stage build for minimal image size
FROM python:3.11-alpine AS builder

# Install build dependencies
RUN apk add --no-cache gcc musl-dev linux-headers

# Create virtual environment and install dependencies
WORKDIR /app
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Final stage - minimal runtime image
FROM python:3.11-alpine

# Install only runtime dependencies
RUN apk add --no-cache libgcc

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set up application
WORKDIR /app
COPY app.py .
COPY templates/ templates/

# Use virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Create non-root user for security
# Note: Docker socket access requires either root or docker group membership
# For production, run with: docker run --user $(id -u):$(getent group docker | cut -d: -f3)
RUN adduser -D -u 1000 appuser && \
    chown -R appuser:appuser /app

# Don't switch to appuser yet - will be handled at runtime
# This allows flexibility for docker socket permissions

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:5000/api/system || exit 1

# Run application
CMD ["python", "app.py"]