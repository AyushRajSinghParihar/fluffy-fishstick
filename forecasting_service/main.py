import os
import pandas as pd
from fastapi import FastAPI, HTTPException
from typing import List
import mlflow

# --- Global variable to hold the model ---
model = None

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Pravāh Forecasting Service",
    on_startup=[lambda: load_model()] # Load model on startup
)

def load_model():
    """
    Loads the latest 'Production' stage model from the MLflow Model Registry.
    """
    global model
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    model_name = "demand-forecaster"
    stage = "Production"
    
    print(f"Loading model '{model_name}' in stage '{stage}' from {mlflow_tracking_uri}...")
    
    try:
        # Load the model from the registry
        model = mlflow.pyfunc.load_model(model_uri=f"models:/{model_name}/{stage}")
        print("Model loaded successfully.")
    except Exception as e:
        print(f"Error loading model: {e}. The service will not be able to make predictions.")
        # In a real app, you might have a fallback model or a more robust error handling
        model = None

# --- API Endpoints ---
@app.get("/health", status_code=200)
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.get("/predict", response_model=List[float])
def get_prediction():
    """
    Returns a 24-hour load forecast using the loaded ML model.
    """
    if model is None:
        raise HTTPException(
            status_code=503, 
            detail="Model is not available. Please ensure a model is trained and promoted to 'Production' stage."
        )

    print("Generating prediction for the next 24 hours...")
    
    # 1. Create a DataFrame for the next 24 hours
    now = pd.Timestamp.now()
    future_dates = pd.to_datetime([now + pd.Timedelta(hours=i) for i in range(24)])
    future_df = pd.DataFrame(index=future_dates)
    
    # 2. Engineer the same features the model was trained on
    future_df['hour'] = future_df.index.hour
    future_df['dayofweek'] = future_df.index.dayofweek
    future_df['month'] = future_df.index.month
    future_df['year'] = future_df.index.year
    # For Solar and Wind, we'll use a simple placeholder (e.g., median) since we don't have future data
    # In a real system, these would come from a weather forecast
    future_df['Solar'] = 15.0 # Placeholder
    future_df['Wind'] = 20.0  # Placeholder
    
    # 3. Make predictions
    predictions = model.predict(future_df)
    
    return predictions.tolist()