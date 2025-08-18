import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List
import pandapower as pp
import pandapower.networks as nw

# Initialize the FastAPI app
app = FastAPI(title="Pravah Simulation Service")

#  Pydantic Model for Input Validation 
class SimulationRequest(BaseModel):
    hourly_load_mw: List[float] = Field(
        ..., 
        min_length=24, 
        max_length=24, 
        description="A list of 24 hourly load forecasts in MW."
    )

#  API Endpoints 
@app.get("/health", status_code=200)
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok"}

@app.post("/run_simulation")
def run_simulation(request: SimulationRequest):
    """
    Runs a power flow simulation for a 24-hour period using pandapower.
    """
    results = []
    
    # Create and Configure the Grid Model
    net = nw.case9()

    # Clear any pre-existing cost data before defining our own.
    if not net.poly_cost.empty:
        net.poly_cost = net.poly_cost.iloc[0:0] # A safe way to clear a DataFrame

    # Define constraints for all power sources
    net.gen['min_p_mw'] = 0
    net.gen['max_p_mw'] = [300, 280]
    net.ext_grid['min_p_mw'] = 0
    net.ext_grid['max_p_mw'] = 250

    # Now, safely create our own costs
    pp.create_poly_cost(net, 0, 'ext_grid', cp1_eur_per_mw=10)
    pp.create_poly_cost(net, 0, 'gen', cp1_eur_per_mw=20)
    pp.create_poly_cost(net, 1, 'gen', cp1_eur_per_mw=30)

    #  Run the Simulation Loop 
    base_loads = net.load.p_mw.copy()

    for hour, total_load_mw in enumerate(request.hourly_load_mw):
        scaling_factor = total_load_mw / base_loads.sum()
        net.load.p_mw = base_loads * scaling_factor

        try:
            pp.runopp(net)
            
            hourly_result = {
                "hour": hour,
                "total_load_mw": round(net.load.p_mw.sum(), 2),
                "line_loading_percent": net.res_line.loading_percent.round(2).tolist(),
                "generator_dispatch_mw": net.res_gen.p_mw.round(2).tolist(),
                "external_grid_dispatch_mw": net.res_ext_grid.p_mw.round(2).tolist(),
                "total_cost_per_hour": round(net.res_cost, 2)
            }
            results.append(hourly_result)

        except Exception as e:
            raise HTTPException(
                status_code=422,
                detail=f"Optimal Power Flow failed to converge at hour {hour} for total load {total_load_mw:.2f} MW. Error: {str(e)}"
            )

    return {"simulation_results": results}