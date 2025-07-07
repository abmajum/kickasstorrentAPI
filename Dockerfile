FROM python:3.12-slim

# Set environment variables early
ENV APP_HOME /app \
    PORT 5000 \
    DEBIAN_FRONTEND=noninteractive

WORKDIR ${APP_HOME}

# Install dependencies in a single layer and clean up
RUN apt-get update && \
    apt-get install -y wget gnupg ca-certificates && \
    wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    dpkg -i google-chrome-stable_current_amd64.deb || true && \
    apt-get -fy install && \
    rm -rf /var/lib/apt/lists/* && \
    rm google-chrome-stable_current_amd64.deb

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY main.py .

# Final command
CMD ["uvicorn", "main:app", "--port", "5000", "--host", "0.0.0.0"]
