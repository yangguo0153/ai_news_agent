FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-chi-sim \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create downloads directory
RUN mkdir -p web_app/downloads

# Environment variables (override in production)
ENV DATABASE_URL=sqlite:///./reimbursement.db
ENV SECRET_KEY=change-me-in-production

# Railway uses PORT env var - use explicit shell form
CMD ["/bin/sh", "-c", "uvicorn web_app.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
