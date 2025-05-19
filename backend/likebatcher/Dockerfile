# Use the official Python image as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /backend

# Copy the entire project into the container
COPY . /twitterfromtemu

# Install dependencies
RUN pip install --no-cache-dir -r backend/likebatcher/requirements.txt || pip install --no-cache-dir -r /twitterfromtemu/backend/likebatcher/requirements.txt || pip install --no-cache-dir -r requirements.txt

# Set the command to run the likebatcher as a module
CMD ["python", "-m", "backend.likebatcher.likebatcher"]
