# Syntax to accept build-time var.

ARG BASE_IMAGE=node:latest

# Adding port argument to avoid input

ARG APP_PORT=3000

# Use the base image specified at buil time

FROM ${BASE_IMAGE}

# Adding Labels to Image and Inspect

LABEL org.opencontainers.image.source="https://github.com/example/repo"
LABEL org.opencontainers.image.description="Example Node.js App"

# Setting the enviroment PORT for APP

ENV PORT=${APP_PORT}

# Set the working dir. for container 

WORKDIR /app 

# Create non-root User with Dockerfile

RUN groupadd -r appuser && useradd --no-log-init -r -g appuser appuser \
    && chown -R appuser:appuser /app

# Switch user to new created one 

USER appuser

# Copy package.json and package-lock.json to work dir.

COPY package*.json ./

# Check if non-root user has needed privileges

COPY package*.json ./
USER root
RUN chown -R appuser:appuser /app
USER appuser
RUN npm install --cache /app/.npm-cache

# Install Node.js dependecies

RUN npm install --cache /app/.npm-cache

# Copy the rest
COPY . .

# Set app to listen PORT 5000 by default
EXPOSE $PORT

#Define the command to run app with usin CMD which defines runtime
CMD ["node", "index.js"]

