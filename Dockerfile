FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Cloud Run will set PORT, but we'll default to 8080 for local dev
ENV PORT=8080

# Expose the port (not strictly required for Cloud Run, but useful for local runs)
EXPOSE 8080

# Use a shell so that ${PORT} is expanded
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
