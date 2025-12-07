# Using Python 3.11 Slim as the base image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Set the environment variables
ENV FLASK_APP=run.py
ENV FLASK_RUN_HOST=0.0.0.0
# Using production environment for server robustness (Gunicorn will be used)
ENV FLASK_ENV=production

# Copy entire requirements.txt and install system dependencies
COPY requirements.txt ./
# Using --no-cache-dir to reduce image size and optimize it
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && pip install --no-cache-dir -r requirements.txt --default-timeout=1500 \
    && apt-get remove -y build-essential \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy the entire application code to the working directory
COPY . .

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the Flask application using Gunicorn
# -w 4: 4 worker processes
# -b 0.0.0.0:5000: bind to all interfaces on port 5000
# --reload: auto-reload on code changes (useful for development)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "--reload", "run:app"]
# Note: Ensure that 'run.py' contains the Flask app instance named 'app'
