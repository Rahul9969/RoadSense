# ==============================================================================
# RoadSense Backend Container - Production AWS EC2 / Container Deployment
# ==============================================================================
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including libpq for PostgreSQL/RDS)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency specifications
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend application source
COPY . .

# Set environment defaults
ENV FLASK_ENV=production \
    PORT=6969 \
    PYTHONUNBUFFERED=1

# Expose backend port
EXPOSE 6969

# Health check matching the CloudWatch/ALB health check endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:6969/api/health || exit 1

# Launch using production-grade WSGI Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:6969", "--workers", "2", "--threads", "4", "--timeout", "60", "backend_main:create_app()"]
