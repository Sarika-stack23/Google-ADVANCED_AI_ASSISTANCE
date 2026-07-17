# Build stage
FROM python:3.11-slim as builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Run stage
FROM python:3.11-slim

WORKDIR /app

# Copy dependencies from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY src /app/backend/src

# Set environment variables
ENV PYTHONPATH=/app
ENV ENVIRONMENT=production

# Cloud Run injects PORT, but default to 8080
ENV PORT=8080

EXPOSE $PORT

# Start FastAPI application
CMD ["sh", "-c", "uvicorn backend.src.main:app --host 0.0.0.0 --port ${PORT}"]
