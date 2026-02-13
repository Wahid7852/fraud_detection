from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from app.models.models import AnalysisResult, AnalysisTrend
from app.core.cache import cached
import os

router = APIRouter()

@router.get("/results")
@cached(ttl=60) # Cache for 1 minute
async def get_ml_results():
    results = await AnalysisResult.find_all().to_list()
    
    if not results:
        return {
            "status": "training",
            "message": "Models are currently training or results not yet available in DB."
        }
    
    # Format results to match the expected frontend structure
    formatted_data = {}
    for res in results:
        formatted_data[res.model_name] = {
            "accuracy": res.accuracy,
            "feature_importance": res.feature_importance
        }
        
    return {
        "status": "success",
        "data": formatted_data
    }

@router.get("/trends")
async def get_trends():
    trend = await AnalysisTrend.find_one()
    if not trend:
        raise HTTPException(status_code=404, detail="Analysis trends not found. Please run training or seed the database.")
    return trend
