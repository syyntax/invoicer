# Use a Python 3.9 slim Debian-based image for better compatibility with WeasyPrint dependencies
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Install system dependencies for WeasyPrint (HTML to PDF converter) and other utilities
# WeasyPrint requires Pango, Cairo, and GDK-Pixbuf
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        # Dependencies for WeasyPrint
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libpangocairo-1.0-0 \
        libgdk-pixbuf2.0-0 \
        libcairo2 \
        # General build essentials and other libs for python packages
        build-essential \
        libffi-dev \
        libxml2-dev \
        libxslt1-dev \
        zlib1g-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Copy requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application code
COPY app/ app/

# Create a directory for persistent data (like the SQLite database)
RUN mkdir -p /app/data

# Expose the port Flask runs on
EXPOSE 5000

# Command to run the application
# This will apply database migrations and then run the Flask app
CMD ["bash", "-c", "flask db upgrade && flask run --host 0.0.0.0 --port 5000"]