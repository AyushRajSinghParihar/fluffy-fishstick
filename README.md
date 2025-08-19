# Production-Grade Micro-Pravah

This project is a fully containerized, end-to-end platform for forecasting electricity demand and simulating the optimal dispatch of power across an electric grid. It serves as a miniature, production-grade version of the "Google Maps for the Electric Grid" concept, demonstrating a robust MLOps and backend engineering skill set.

The system automatically trains a machine learning model, serves forecasts via a high-performance API, and runs complex power grid simulations through a separate backend service, with an interactive web frontend to visualize the results.

[![CI Pipeline](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/YOUR_REPOSITORY/actions/workflows/ci.yml)

## Features

*   **Automated ML Pipeline:** A "train-and-serve" workflow that automatically trains a demand forecasting model and makes it available for prediction.
*   **Microservice Architecture:** The system is composed of decoupled services (training, forecasting, simulation, frontend) that communicate via APIs, enabling independent scaling and development.
*   **Optimal Power Flow Simulation:** Utilizes `pandapower` to run an Optimal Power Flow (OPF) simulation, determining the most cost-effective way to generate electricity without overloading the grid.
*   **Interactive Frontend:** A web application built with Streamlit provides a user-friendly interface for running simulations and visualizing forecasts, grid stress, and detailed operational data.
*   **Containerized & Reproducible:** The entire application stack is defined in Docker and can be launched with a single command, ensuring a consistent environment.
*   **CI/CD Integration:** An automated CI pipeline using GitHub Actions runs linting and integration tests on every code change to ensure software quality and reliability.

## Project Architecture

The application is built on a containerized microservice architecture, orchestrated by Docker Compose. A shared Docker volume is used to persist the trained machine learning model, decoupling the training process from the prediction service.

```mermaid
graph TD
    subgraph "Local Environment / CI"
        User[User / Developer] --> Git[Git Push]
        Git --> GHA[GitHub Actions: CI Pipeline]
        GHA --> Linter[1. Lint Code]
        GHA --> Tests[2. Run Integration Tests]
    end

    subgraph "Docker Environment (docker compose up)"
        TC[Training Container (Runs once)] -- Saves model.pkl --> V[fa:fa-database Shared Volume: model_artifacts]
        V -- Loads model.pkl --> FC[Forecasting API Service (FastAPI)]
        
        FE[Frontend (Streamlit)] -- API Request --> FC
        FE -- API Request --> SC[Simulation API Service (FastAPI)]
        FC -- Sends Forecast --> SC
    end

    Client[Browser] <--> FE

    style V fill:#f9f,stroke:#333,stroke-width:2px
```

## Tech Stack

| Component            | Technology                                    | Purpose                                                     |
| -------------------- | --------------------------------------------- | ----------------------------------------------------------- |
| **Backend Services** | Python, FastAPI                               | High-performance, asynchronous APIs for serving predictions and simulations. |
| **Grid Simulation**  | `pandapower`, `pypower`                       | Industry-standard library for power system analysis and OPF. |
| **ML Forecasting**   | `LightGBM`, `scikit-learn`                    | Training a lightweight yet powerful gradient boosting model.  |
| **MLOps Pipeline**   | Docker Compose, Shared Docker Volume, `joblib`  | Orchestrating an automated train-and-serve model lifecycle. |
| **Frontend**         | Streamlit                                     | Building an interactive, data-driven web application in pure Python. |
| **Orchestration**    | Docker, Docker Compose                        | Containerizing services for a reproducible and isolated environment. |
| **CI/CD & Testing**  | GitHub Actions, `pytest`, `httpx`, `ruff`     | Automating linting and integration testing to ensure code quality. |


## Quickstart: Running the Application Locally

The entire platform can be launched with a single command.

### Prerequisites

*   Docker and Docker Compose installed.

### Instructions

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY.git
    cd YOUR_REPOSITORY
    ```

2.  **Launch the application:**
    This command will build the Docker images for all services and start them in the background. The training service will run first, and the other services will start after it completes.
    ```bash
    docker compose up --build -d
    ```

3.  **Access the Frontend:**
    After about a minute (to allow for model training), open your web browser and navigate to:
    **[http://localhost:8501](http://localhost:8501)**

4.  **Explore the APIs (Optional):**
    The backend APIs also expose automatic documentation:
    *   **Forecasting API:** [http://localhost:8000/docs](http://localhost:8000/docs)
    *   **Simulation API:** [http://localhost:8001/docs](http://localhost:8001/docs)

5.  **Stopping the Application:**
    When you're finished, stop and remove all the containers:
    ```bash
    docker compose down --volumes
    ```

## Running the Automated Tests Locally

To verify the health and correctness of the backend APIs, you can run the integration test suite.

1.  Make sure the application is running (use the `docker compose up` command above).
2.  Create and activate a Python virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
3.  Install the test dependencies:
    ```bash
    pip install -r tests/requirements.txt
    ```
4.  Run pytest:
    ```bash
    pytest
    ```

## Future Work

This project provides a strong foundation. Potential future improvements include:

*   **Replacing MLOps:** Using MLflow back instead of the pragmatic version for better versioning and model management
*   **Enhanced Anomaly Simulation:** Fully implementing the "Line Failure" feature in the backend to allow for dynamic congestion simulations.
*   **Advanced Forecasting:** Integrating external features like weather forecasts to improve model accuracy.
*   **Production Deployment:** Creating a deployment pipeline to a cloud provider like AWS ECS or Google Cloud Run.
*   **Monitoring:** Adding a monitoring stack (e.g., Prometheus + Grafana) to track API performance and system health.