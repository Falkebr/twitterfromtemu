# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the caching system code into the container
COPY cache.py /app/cache.py
COPY requirements.txt /app/requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Set the command to run the caching system
CMD ["uvicorn", "cache:app", "--host", "0.0.0.0", "--port", "5000"]