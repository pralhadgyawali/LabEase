# Use Python 3.12 slim image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create directory for SQLite database
RUN mkdir -p /app/data && \
    chmod 755 /app/data

# Run migrations
RUN python manage.py migrate --noinput

# Collect static files (if needed)
# RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
python manage.py migrate --noinput\n\
exec python manage.py runserver 0.0.0.0:8000\n\
' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Run the application
CMD ["/app/entrypoint.sh"]
