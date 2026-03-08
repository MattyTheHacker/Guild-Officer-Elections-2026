FROM python:3.11-slim

# Install bash (required for your current docker-compose command)
RUN apt-get update && apt-get install -y bash && rm -rf /var/lib/apt/lists/*

# Install datasette and the required plugin natively
RUN pip install datasette datasette-plot

EXPOSE 8001
