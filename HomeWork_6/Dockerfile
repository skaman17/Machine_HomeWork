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

# Copy package.json and package-lock.json to work dir.

COPY package*.json ./

# Install Node.js dependecies

RUN npm install

# Copy the rest
COPY . .

# Copy mine script and make it exec.

COPY start-app.sh .
RUN chmod +x start-app.sh

# Set app to listen PORT 3000 by default

EXPOSE 3000

# Use the script as the entry point

ENTRYPOINT ["./start-app.sh"]

#Health check 
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:3000/healthz || exit 1

