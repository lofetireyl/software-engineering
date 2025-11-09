# Dockerfile
FROM python:3.12-slim

# Avoid Python buffering logs
ENV PYTHONUNBUFFERED=1

# Work directory inside the container
WORKDIR /app

# Install system deps needed by psycopg2
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
 && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

# Default command (you can override in docker-compose if needed)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
