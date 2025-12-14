"""
R Service Client
Communicates with the Dockerized R Plumber API
"""

import httpx
import os
from typing import Optional

R_SERVICE_URL = os.getenv("R_SERVICE_URL", "http://localhost:8787")


async def check_r_health() -> dict:
    """Check if R service is healthy"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{R_SERVICE_URL}/health")
            if response.status_code == 200:
                return response.json()
            return {"status": "error", "code": response.status_code}
    except Exception as e:
        return {"status": "unreachable", "error": str(e)}


async def execute_r_script(script: str) -> dict:
    """
    Execute an R script on the R service.
    
    Args:
        script: R code to execute (must return JSON-serializable result)
        
    Returns:
        dict with 'success' and 'result' or 'error'
    """
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{R_SERVICE_URL}/execute",
                json={"script": script}
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "success": False,
                    "error": f"R service returned {response.status_code}"
                }
                
    except httpx.TimeoutException:
        return {"success": False, "error": "R service timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}


async def get_available_teams() -> list:
    """Get list of NFL teams from R service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{R_SERVICE_URL}/teams")
            if response.status_code == 200:
                data = response.json()
                return data.get("teams", [])
            return []
    except Exception:
        return []


async def get_data_schema() -> dict:
    """Get nflfastR data schema from R service"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{R_SERVICE_URL}/schema")
            if response.status_code == 200:
                return response.json()
            return {"success": False}
    except Exception as e:
        return {"success": False, "error": str(e)}
