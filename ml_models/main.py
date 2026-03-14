"""
=============================================================================
SENTINELS OF INTEGRITY — ML Inference Service
FastAPI wrapper for the deepfake detection models.
=============================================================================
"""

import logging
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import torch
import numpy as np
import cv2
import time

from ml_models.inference.pipeline import InferencePipeline
from ml_models.config import MLConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sentinels.ml")

app = FastAPI(title="Sentinels ML Engine", version="0.1.0")

# Initialize Pipeline (mocker logic is internal to InferencePipeline)
pipeline = InferencePipeline()

class InferenceResponse(BaseModel):
    is_synthetic: bool
    confidence: float
    artifacts: list[str]
    model_version: str
    processing_time_ms: float

@app.get("/health")
async def health():
    return {"status": "online", "model": "xception-gru-ensemble"}

@app.post("/predict", response_model=InferenceResponse)
async def predict(file: UploadFile = File(...)):
    """Runs deepfake detection on an uploaded video/image."""
    start_time = time.time()
    
    try:
        # In a real scenario, we'd save to temp or stream
        content = await file.read()
        
        # Run inference
        result = pipeline.run(content)
        
        processing_time = (time.time() - start_time) * 1000
        
        return {
            **result,
            "processing_time_ms": processing_time
        }
    except Exception as e:
        logger.error(f"Inference error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
