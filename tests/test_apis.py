import httpx

FORECASTING_API_URL = "http://localhost:8000"
SIMULATION_API_URL = "http://localhost:8001"

def test_forecasting_api_health():
    """Tests if the forecasting API's health check is working."""
    response = httpx.get(f"{FORECASTING_API_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_simulation_api_health():
    """Tests if the simulation API's health check is working."""
    response = httpx.get(f"{SIMULATION_API_URL}/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_get_prediction():
    """Tests if the predict endpoint returns a valid forecast."""
    response = httpx.get(f"{FORECASTING_API_URL}/predict")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 24
    assert all(isinstance(x, float) for x in data)

def test_run_simulation_success():
    """Tests the simulation API with a valid payload."""
    payload = {"hourly_load_mw": [50.0] * 24}
    
    response = httpx.post(f"{SIMULATION_API_URL}/run_simulation", json=payload, timeout=30.0)
    
    assert response.status_code == 200
    data = response.json()
    assert "simulation_results" in data
    assert len(data["simulation_results"]) == 24

def test_run_simulation_validation_error():
    """Tests that the simulation API fails correctly with an invalid payload."""
    payload = {"hourly_load_mw": [50.0] * 23}
    
    response = httpx.post(f"{SIMULATION_API_URL}/run_simulation", json=payload)
    
    assert response.status_code == 422