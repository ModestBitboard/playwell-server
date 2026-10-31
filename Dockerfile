FROM python:3.11-slim

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
