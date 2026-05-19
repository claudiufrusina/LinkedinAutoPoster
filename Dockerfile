# Use official lightweight Python image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set the working directory in the container
WORKDIR /app

# Install system dependencies (tzdata for timezone support, ca-certificates for secure HTTPS calls)
RUN apt-get update && apt-get install -y --no-install-recommends \
    tzdata \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker's caching mechanism
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

# Set default environment variables (can be overridden at runtime)
ENV TZ=UTC
ENV DRY_RUN=false
ENV WEB_PORT=5000

# Expose the web GUI port
EXPOSE 5000

# Command to run both the scheduler and web GUI
CMD ["./start.sh"]
