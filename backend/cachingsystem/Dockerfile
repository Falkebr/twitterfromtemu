# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the caching system code into the container
COPY cache.py /app/cache.py

# Set the command to run the caching system
CMD ["python", "cache.py"]