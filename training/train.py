import os
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
import mlflow
import mlflow.lightgbm

def train_model():
    """
    Downloads data, trains a LightGBM model, and logs it to MLflow.
    """
    # 1. --- Configuration ---
    # Get the MLflow tracking URI from the environment variable
    mlflow_tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    mlflow.set_tracking_uri(mlflow_tracking_uri)
    print(f"MLflow Tracking URI: {mlflow_tracking_uri}")

    # 2. --- Data Loading and Feature Engineering ---
    # Download hourly energy consumption data
    data_url = "https://raw.githubusercontent.com/jenfly/opsd/master/opsd_germany_daily.csv"
    print("Downloading data...")
    df = pd.read_csv(data_url)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.rename(columns={'Consumption': 'y'}, inplace=True)
    
    # Create time-series features
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['year'] = df.index.year
    
    # Handle missing values simply
    df.fillna(df.median(), inplace=True)
    
    print("Data prepared. Features:", df.columns.tolist())

    # 3. --- Model Training ---
    # Define features (X) and target (y)
    features = ['hour', 'dayofweek', 'month', 'year', 'Solar', 'Wind']
    target = 'y'

    X_train, X_test, y_train, y_test = train_test_split(df[features], df[target], test_size=0.2, shuffle=False)

    # Start an MLflow run
    with mlflow.start_run() as run:
        print(f"Starting MLflow Run: {run.info.run_id}")
        
        # Define model parameters
        params = {
            'objective': 'regression',
            'metric': 'rmse',
            'n_estimators': 1000,
            'learning_rate': 0.05,
            'feature_fraction': 0.8,
            'bagging_fraction': 0.8,
            'bagging_freq': 1,
            'verbose': -1,
            'n_jobs': -1,
            'seed': 42
        }

        # Train the model
        model = lgb.LGBMRegressor(**params)
        model.fit(X_train, y_train,
                  eval_set=[(X_test, y_test)],
                  eval_metric='rmse',
                  callbacks=[lgb.early_stopping(100, verbose=False)])

        # 4. --- Model Evaluation and Logging ---
        predictions = model.predict(X_test)
        rmse = mean_squared_error(y_test, predictions, squared=False)

        print(f"Model trained. RMSE: {rmse}")

        # Log parameters and metrics to MLflow
        mlflow.log_params(params)
        mlflow.log_metric("rmse", rmse)
        
        # Log the model to MLflow, registering it in the Model Registry
        mlflow.lightgbm.log_model(
            lgb_model=model,
            artifact_path="model",
            registered_model_name="demand-forecaster"
        )
        print("Model logged and registered in MLflow Model Registry as 'demand-forecaster'.")

if __name__ == "__main__":
    train_model()