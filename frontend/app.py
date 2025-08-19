import streamlit as st
import requests
import pandas as pd
import numpy as np

# Configuration
st.set_page_config(page_title="Pravah Grid Simulation", layout="wide")

FORECASTING_API_URL = "http://forecasting-api:8000/predict"
SIMULATION_API_URL = "http://simulation-api:8000/run_simulation"

# UI Elements
st.title("Pravah Demo: AI-Driven Grid Simulation")
st.markdown("This application demonstrates an end-to-end MLOps pipeline for forecasting electricity demand and simulating grid operations.")

st.sidebar.header("Simulation Controls")
run_button = st.sidebar.button("Run New Simulation", type="primary")
st.sidebar.markdown("---")
# The "anomaly" feature: a checkbox to simulate a line failure
# For the case9 network, a critical line is line index 7 (connecting buses 7 and 8)
simulate_failure = st.sidebar.checkbox("Simulate Line 7 Failure (Congestion Scenario)")


# Main Application Logic
if run_button:
    with st.spinner('Step 1/2: Generating 24-hour demand forecast...'):
        try:
            # 1. Call the Forecasting API
            forecast_response = requests.get(FORECASTING_API_URL, timeout=10)
            forecast_response.raise_for_status() # Will raise an exception for 4xx/5xx errors
            forecast_data = forecast_response.json()
            
            st.success("✅ Forecast generated successfully.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to Forecasting API: {e}")
            st.stop()

    with st.spinner('Step 2/2: Running grid simulation...'):
        try:
            # 2. Prepare payload and call the Simulation API
            payload = {"hourly_load_mw": forecast_data}
            
            # (This is a placeholder for the anomaly feature - we'll implement the backend logic later if needed)
            # if simulate_failure:
            #     payload["failed_line_id"] = 7 

            sim_response = requests.post(SIMULATION_API_URL, json=payload, timeout=60)
            sim_response.raise_for_status()
            sim_results = sim_response.json()["simulation_results"]
            
            st.success("✅ Grid simulation complete.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to Simulation API: {e}")
            st.stop()

    # Data Visualization
    st.markdown("---")
    st.header("Results")

    # Create two columns for side-by-side charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Demand Forecast")
        forecast_df = pd.DataFrame({
            'Hour': range(24),
            'Forecasted Load (MW)': forecast_data
        })
        st.line_chart(forecast_df.set_index('Hour'))

    with col2:
        st.subheader("Grid Stress (Max Line Loading)")
        # Process results to find the most stressed line at each hour
        max_loading = [max(hour_data['line_loading_percent']) for hour_data in sim_results]
        stress_df = pd.DataFrame({
            'Hour': range(24),
            'Max Line Loading (%)': max_loading
        })
        st.line_chart(stress_df.set_index('Hour'))
        # Add a color-coded indicator for peak stress
        peak_stress = max(max_loading)
        if peak_stress > 80:
            st.error(f"**Peak Grid Stress:** {peak_stress:.2f}% (High Congestion Risk)")
        elif peak_stress > 50:
            st.warning(f"**Peak Grid Stress:** {peak_stress:.2f}% (Moderate Congestion)")
        else:
            st.success(f"**Peak Grid Stress:** {peak_stress:.2f}% (Grid Stable)")


    st.subheader("Detailed Simulation Output")
    # Create a clean DataFrame from the detailed results
    display_df = pd.DataFrame({
        "Hour": [r['hour'] for r in sim_results],
        "Total Load (MW)": [r['total_load_mw'] for r in sim_results],
        "Max Line Loading (%)": [max(r['line_loading_percent']) for r in sim_results],
        "Total Cost (€)": [r['total_cost_per_hour'] for r in sim_results],
        "Gen Dispatch (MW)": [r['generator_dispatch_mw'] for r in sim_results],
        "Ext. Grid Dispatch (MW)": [r['external_grid_dispatch_mw'] for r in sim_results]
    })
    st.dataframe(display_df)