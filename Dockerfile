FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy model for Presidio
RUN python -m spacy download en_core_web_sm

# Copy the rest of the application
COPY . .

# Install the package
RUN pip install -e .

# Create directory for local storage
RUN mkdir -p /tmp/fedmcp

# Expose port
EXPOSE 8000

# Run the server
CMD ["python", "-m", "src.main"]