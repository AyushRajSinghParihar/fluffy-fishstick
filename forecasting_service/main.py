import pandas as pd
from fastapi import FastAPI, HTTPException
from typing import List
import joblib
import numpy as np # Import numpy

model = None
MODEL_PATH = "/artifacts/demand_forecaster.pkl"

# A standard residential/commercial electricity usage profile for a 24-hour period.
# These are percentages that represent the "shape" of a day. They sum to 100.
HOURLY_PROFILE_PERCENT = np.array([
    2.8, 2.5, 2.3, 2.2, 2.3, 2.7, 3.5, 4.5, 5.5, 6.0, 6.2, 6.3, 
    6.2, 6.0, 5.8, 5.9, 6.5, 7.5, 8.0, 7.5, 6.5, 5.5, 4.5, 3.6
])
# Normalize to ensure it sums to 1
HOURLY_PROFILE = HOURLY_PROFILE_PERCENT / HOURLY_PROFILE_PERCENT.sum()


app = FastAPI(
    title="Pravāh Forecasting Service",
    on_startup=[lambda: load_model()]
)

def load_model():
    global model
    try:
        model = joblib.load(MODEL_PATH)
        print("Model loaded successfully from /artifacts/demand_forecaster.pkl")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None

@app.get("/health", status_code=200)
def health_check():
    return {"status": "ok"}

@app.get("/predict", response_model=List[float])
def get_prediction():
    if model is None:
        raise HTTPException(status_code=503, detail="Model is not available.")

    # 1. Create features for a single point in time (tomorrow)
    tomorrow = pd.Timestamp.now() + pd.Timedelta(days=1)
    future_df = pd.DataFrame(index=[tomorrow])
    
    future_df['hour'] = future_df.index.hour # Will be 0
    future_df['dayofweek'] = future_df.index.dayofweek
    future_df['month'] = future_df.index.month
    future_df['year'] = future_df.index.year
    # Use placeholder values for Solar and Wind
    future_df['Solar'] = 15.0 
    future_df['Wind'] = 20.0
    
    # 2. Predict the TOTAL consumption for the entire day
    daily_prediction = model.predict(future_df)[0]
    
    # 3. Distribute this total across 24 hours using the profile
    hourly_predictions = daily_prediction * HOURLY_PROFILE
    
    return hourly_predictions.tolist()