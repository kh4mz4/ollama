# Python 3.13 image
FROM python:3.13-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Work directory
WORKDIR /app

# System dependencies (agar kerak bo‘lsa)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Requirements ni copy qilish
COPY requirements.txt .

# Dependencies install
RUN pip install --no-cache-dir -r requirements.txt

# Projectni copy qilish
COPY . .

# Port (FastAPI default)
EXPOSE 8000

# Run command (uvicorn orqali)
CMD ["uvicorn", "process.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
