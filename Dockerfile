FROM python:3.11-slim

LABEL org.opencontainers.image.title="Playwell" \
      org.opencontainers.image.description="A (mostly) stateless REST API server for LEGO kit information and instructions" \
      org.opencontainers.image.version="1.0.1" \
      org.opencontainers.image.source="https://github.com/ModestBitboard/playwell-server" \
      org.opencontainers.image.licenses="GPLv3"

# Prevent Python from writing .pyc files and force stdout/stderr to be unbuffered.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Configure runtime variables
ENV PLAYWELL_DATA_DIR=/data
ENV PORT=5346
ENV LOG_LEVEL=info

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy server code
COPY ./app ./app

# Explicitly create data directory
RUN mkdir -p /data

EXPOSE 5346

# Set the run command
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT} --log-level ${LOG_LEVEL}"]
