# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /backend

# Copy the logger code into the container
COPY logger.py /backend/logger.py

# Install dependencies if requirements.txt exists
COPY requirements.txt /backend/requirements.txt
RUN if [ -f requirements.txt ]; then pip install --no-cache-dir -r requirements.txt; fi

# Set the command to run the logger
CMD ["python", "logger.py"]
