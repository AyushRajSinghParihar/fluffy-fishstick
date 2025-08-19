import pandas as pd
import lightgbm as lgb
import joblib

def train_model():
    print("Starting model training...")
    
    # --- Data Loading and Feature Engineering ---
    data_url = "https://raw.githubusercontent.com/jenfly/opsd/master/opsd_germany_daily.csv"
    df = pd.read_csv(data_url)
    df['Date'] = pd.to_datetime(df['Date'])
    df.set_index('Date', inplace=True)
    df.rename(columns={'Consumption': 'y'}, inplace=True)
    df['hour'] = df.index.hour
    df['dayofweek'] = df.index.dayofweek
    df['month'] = df.index.month
    df['year'] = df.index.year
    df.fillna(df.median(), inplace=True)
    
    features = ['hour', 'dayofweek', 'month', 'year', 'Solar', 'Wind']
    target = 'y'
    X_train, y_train = df[features], df[target]

    # --- Model Training ---
    params = { 'objective': 'regression', 'metric': 'rmse', 'n_estimators': 500, 'learning_rate': 0.05 }
    model = lgb.LGBMRegressor(**params)
    model.fit(X_train, y_train)

    # --- Save the Model to the Shared Volume ---
    model_path = "/artifacts/demand_forecaster.pkl"
    joblib.dump(model, model_path)
    
    print(f"Model training complete. Model saved to {model_path}")

if __name__ == "__main__":
    train_model()