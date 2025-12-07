FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
# libgomp1 is required for LightGBM
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --no-cache-dir --upgrade pip

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port for Streamlit (default: 8501)
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run Streamlit on default port 8501
CMD ["streamlit", "run", "deployment/streamlit/app_final.py", "--server.port=8501", "--server.address=0.0.0.0"]
