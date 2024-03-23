# This is a Dockerfile that performs the following steps:
# 1. Pulls the base image from the Docker Hub
# 2. Installs the necessary packages
# 3. Copies the source code to the container
# 4. Sets the working directory
# 5. Exposes the port
# 6. Runs the application

# Pull the base image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the source code to the container
COPY . /app

# Install the necessary packages
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install -e .

# Expose the logs
RUN ln -sf /dev/stdout /app/app.log

# Expose the port
EXPOSE 5353

# Run the application
CMD ["python", "health_data/app.py"]