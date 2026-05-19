# ============================================================================
# FHIR IPS Bundle Validator - Production Dockerfile
# ============================================================================
# Multi-stage build for smaller final image
# Base image: Python 3.12 slim (Debian-based)

FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies required for Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libxml2-dev \
    libxslt-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (leverage Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# ============================================================================
# Final stage - minimal runtime image
# ============================================================================
FROM python:3.12-slim

# Create non-root user for security
RUN useradd -m -u 1000 streamlit && \
    mkdir -p /app && \
    chown -R streamlit:streamlit /app

WORKDIR /app

# Install only runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    libxml2 \
    libxslt1.1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /home/streamlit/.local

# Copy application files
COPY --chown=streamlit:streamlit . .

# Switch to non-root user
USER streamlit

# Add local Python packages to PATH
ENV PATH=/home/streamlit/.local/bin:$PATH

# Expose Streamlit default port
EXPOSE 8501

# Health check to ensure app is running
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Set Streamlit configuration via environment variables
ENV STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
    STREAMLIT_SERVER_FILE_WATCHER_TYPE=none

# Run the Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
