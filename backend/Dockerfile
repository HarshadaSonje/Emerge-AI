FROM python:3.12-slim

WORKDIR /app

# Install PostgreSQL dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Cloud Run uses PORT environment variable
CMD exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8080}
