#!/bin/bash

# Define variables
IMAGE_NAME="my-flask-app"
CONTAINER_NAME="my-flask-app-container"
DOCKERFILE_PATH="."

# Build the Docker image
docker build -t $IMAGE_NAME $DOCKERFILE_PATH

# Run the Docker container
docker run -d -p 8000:8000 --name $CONTAINER_NAME $IMAGE_NAME