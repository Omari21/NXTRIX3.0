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

# Expose port (Railway will set the PORT environment variable)
EXPOSE $PORT

# Set environment variables
ENV STREAMLIT_ENV=production
ENV PYTHONPATH=/app

# Start command
CMD streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0