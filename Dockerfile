FROM python:3.12-alpine

# Set environment variables early
ENV APP_HOME=/app \
    PORT=5000

WORKDIR ${APP_HOME}

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Final command
CMD ["uvicorn", "main:app", "--port", "5000", "--host", "0.0.0.0"]
