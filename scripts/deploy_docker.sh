#!/bin/bash

# Set variables
IMAGE_NAME="my-flask-app"
LOCAL_TAG="latest"
DOCKER_USERNAME="vikashraj1825"
REPO_NAME="my-flask-app-container"
VERSION="1.0"
DOCKERFILE_PATH="../"  # Adjust this to the correct path

# Echo starting
echo "Starting Docker deployment process..."

# Build the Docker image
# if docker build -t $IMAGE_NAME:$LOCAL_TAG $DOCKERFILE_PATH; then
#     echo "Docker image has been built successfully."
# else
#     echo "Failed to build Docker image."
#     exit 1
# fi

# Tagging the Docker image
echo "Tagging the image..."
docker tag $IMAGE_NAME:$LOCAL_TAG $DOCKER_USERNAME/$REPO_NAME:$VERSION

# Logging in to Docker Hub
echo "Logging into Docker Hub..."
# docker login

# Pushing the Image to Docker Hub
echo "Pushing the image to Docker Hub..."
if docker push $DOCKER_USERNAME/$REPO_NAME:$VERSION; then
    echo "Docker image has been pushed to Docker Hub successfully."
else
    echo "Failed to push Docker image to Docker Hub."
    exit 1
fi