# Use an official Python runtime as a parent image
FROM python:3.12.3-alpine

# Set the working directory in the container to /app
WORKDIR /app

# Install necessary build tools and system dependencies
RUN apk update && apk add --no-cache \
    gcc g++ make libffi-dev openssl-dev \
    sdl2_ttf sdl2_image sdl2_mixer gstreamer

# Add the current directory contents into the container at /app
ADD . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run gunicorn when the container launches
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:create_app()"]
