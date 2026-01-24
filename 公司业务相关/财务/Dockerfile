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

# Expose port (Railway will override with PORT env var)
EXPOSE 8000

# Environment variables (override in production)
ENV DATABASE_URL=sqlite:///./reimbursement.db
ENV SECRET_KEY=change-me-in-production

# Start command - Use shell form to allow $PORT substitution
# Railway sets PORT env var, default to 8000 if not set
CMD uvicorn web_app.app:app --host 0.0.0.0 --port ${PORT:-8000}
