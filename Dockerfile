FROM python:3.11-slim

WORKDIR /app

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application - Fixed with trailing slash
COPY *.py ./

# Set environment variable for the port
ENV PORT=8080

# Command to run the application
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT}