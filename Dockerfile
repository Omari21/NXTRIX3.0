# Use Python 3.11 to avoid compatibility issues
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install requirements
RUN pip install --upgrade pip setuptools wheel
RUN pip install -r requirements.txt

# Copy application code
COPY . .

# Make the startup script executable
RUN chmod +x /app/start.py

# Expose port (Railway will set the PORT environment variable)
EXPOSE 8000

# Set environment variables
ENV STREAMLIT_ENV=production
ENV PYTHONPATH=/app

# Start command using Python script
CMD ["python", "/app/start.py"]