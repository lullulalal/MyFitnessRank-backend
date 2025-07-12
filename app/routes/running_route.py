# app/api/running.py

from fastapi import APIRouter, Depends
from sqlmodel import Session
from ..schemas.running_schema import RunningRequest, RunningResponse
from ..services.running_service import RunningAnalyzer
from ..core.db import get_session

router = APIRouter()

@router.post("/running", response_model=RunningResponse)
async def running_analysis(
    request: RunningRequest,
    session: Session = Depends(get_session),
):
    analyzer = RunningAnalyzer(request, session)
    return analyzer.analyze()
