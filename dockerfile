FROM python:3.13-slim

WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose the default uvicorn port
EXPOSE 8000

# Run the FastAPI server
CMD ["uvicorn", "process.api_server:app", "--host", "0.0.0.0", "--port", "8000"]
