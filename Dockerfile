FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Use the PORT env var provided by Cloud Run (default 8000 for local)
ENV PORT=8000

# Run the application
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT}
