# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install curl
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed dependencies specified in requirements.txt
RUN pip install --trusted-host pypi.python.org -r requirements.txt

# Make port 5000 available to the world outside this container 
EXPOSE 5000

# Define environment variable
ENV FLASK_APP app.py

# Healthcheck to ensure the service is running
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
 CMD curl --fail http://localhost:5000/healthz || exit 1

# Run app.py when the container launches 
CMD ["flask", "run", "--host=0.0.0.0"]
