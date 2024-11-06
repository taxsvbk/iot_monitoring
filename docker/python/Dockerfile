FROM python:3.9-slim

WORKDIR /app

# Install required system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
ENV PYTHONPATH=/app
COPY . /app/

# Make port 5000 available
EXPOSE 5000

# Create a non-root user and switch to it
RUN useradd -m myuser && \
    chown -R myuser:myuser /app
USER myuser

# Run the application
CMD ["python", "-m", "app.app"]