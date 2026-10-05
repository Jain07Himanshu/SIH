import time
from fastapi import APIRouter

router = APIRouter(tags=["Health"])
_START_TIME = time.time()

@router.get("/health")
@router.get("/api/v1/health")
def health_check():
    return {
        "status": "healthy",
        "service": "Grievance Intelligence Engine",
        "version": "1.0.0",
        "uptime_seconds": round(time.time() - _START_TIME, 2),
        "models_loaded": True
    }
