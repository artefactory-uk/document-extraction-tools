# Use the official MLflow image as the base image
FROM ghcr.io/mlflow/mlflow:v3.8.1

# Install the PostgreSQL driver
RUN pip install psycopg2-binary
