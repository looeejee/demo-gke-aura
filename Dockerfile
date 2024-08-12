# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install the dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the templates directory into /app/templates in the container
COPY templates /app/templates

# Copy the app.py file into /app in the container
COPY app.py /app/

# Expose port 80 for the Flask app
EXPOSE 80

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the Flask app
CMD ["flask", "run", "--host=0.0.0.0", "--port=80"]
