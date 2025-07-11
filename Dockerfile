# Use an official Python image
FROM python:3.11-slim
# Set the working directory
WORKDIR /app
# Install dependencies
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
# Copy the example Flask app (or the full project)
COPY . .
# Run the Flask app
CMD ["python", "example_app.py"]
# Build the image
#docker build -t flask-dashboard .
# Run it
#docker run -p 5000:5000 flask-dashboard
