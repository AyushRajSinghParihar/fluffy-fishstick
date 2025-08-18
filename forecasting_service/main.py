from fastapi import FastAPI
from typing import List

app = FastAPI(title="Pravah Forecasting Service")

@app.get("/health", status_code=200)
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.get("/predict", response_model=List[float])
def get_prediction():
    """
    Returns a mock 24-hour load forecast.
    In Phase 2, this will use a real ML model.
    """
    # A realistic-looking mock forecast for a 24-hour period
    mock_forecast = [
        100.5, 95.2, 90.1, 88.7, 92.3, 105.6, 120.8, 135.4, 145.1, 150.3, 
        155.6, 158.2, 160.1, 157.9, 152.0, 148.5, 153.2, 165.4, 180.9, 
        190.1, 175.8, 160.3, 140.7, 120.5
    ]
    return mock_forecast