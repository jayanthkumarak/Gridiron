"""
Gridiron FastAPI Backend
NFL Analytics Orchestrator
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import os

from chains import analyze_query
from r_client import check_r_health

app = FastAPI(
    title="Gridiron API",
    description="NFL Analytics powered by nflfastR and LLM",
    version="1.0.0"
)

# CORS for SvelteKit frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",    # Vite dev
        "http://localhost:4173",    # Vite preview
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", "")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class AnalyzeRequest(BaseModel):
    query: str


class ChartConfig(BaseModel):
    type: str  # 'dot', 'slope', 'sparkline'
    data: list
    xLabel: Optional[str] = None
    yLabel: Optional[str] = None


class AnalyzeResponse(BaseModel):
    headline: str
    summary: str
    chart: Optional[ChartConfig] = None
    raw_data: Optional[dict] = None
    error: Optional[str] = None


@app.get("/health")
async def health_check():
    """Check API and R service health"""
    r_status = await check_r_health()
    
    return {
        "status": "ok",
        "api": "healthy",
        "r_service": r_status
    }


@app.post("/analyze", response_model=AnalyzeResponse)
async def analyze(request: AnalyzeRequest):
    """
    Main analysis endpoint.
    Takes a natural language query, generates R code, executes it,
    and synthesizes a memo with visualization config.
    """
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    try:
        result = await analyze_query(request.query)
        return result
    except Exception as e:
        return AnalyzeResponse(
            headline="Analysis Error",
            summary=f"An error occurred while processing your query: {str(e)}",
            error=str(e)
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
