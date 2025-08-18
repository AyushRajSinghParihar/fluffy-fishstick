FROM ghcr.io/mlflow/mlflow:v2.11.1

# Install PostgreSQL adapter and curl for health checks
RUN pip install psycopg2-binary && \
    apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

CMD ["mlflow", "server", "--backend-store-uri", "postgresql://user:password@postgres:5432/db", "--default-artifact-root", "/mlflow/artifacts", "--host", "0.0.0.0"]