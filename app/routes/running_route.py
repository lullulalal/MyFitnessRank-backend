# app/api/running.py

from fastapi import APIRouter, Depends
from ..schemas.running_schema import RunningRequest, RunningResponse
from ..services.running_service import RunningAnalyzer

router = APIRouter()

@router.post("/running", response_model=RunningResponse)
async def running_analysis(request: RunningRequest):
    analyzer = RunningAnalyzer(request)
    return analyzer.analyze()
