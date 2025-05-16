# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /twitterfromtemu

# Copy the entire project into the container
COPY . /twitterfromtemu

# Install dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Set the command to run the API using module syntax
CMD ["python", "-m", "backend.main"]
