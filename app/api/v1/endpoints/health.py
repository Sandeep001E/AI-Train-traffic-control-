from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.database import get_db, get_redis
from app.core.config import settings
import time
import psutil
from datetime import datetime

router = APIRouter()

@router.get("/")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/detailed")
async def detailed_health_check(db: Session = Depends(get_db)):
    """Detailed health check with system metrics"""
    start_time = time.time()
    
    # Database health check
    db_status = "healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Redis health check
    redis_status = "healthy"
    try:
        redis_client = get_redis()
        redis_client.ping()
    except Exception as e:
        redis_status = f"unhealthy: {str(e)}"
    
    # System metrics
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    response_time = (time.time() - start_time) * 1000  # milliseconds
    
    return {
        "status": "healthy" if db_status == "healthy" and redis_status == "healthy" else "degraded",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "timestamp": datetime.utcnow().isoformat(),
        "response_time_ms": round(response_time, 2),
        "components": {
            "database": db_status,
            "redis": redis_status
        },
        "system_metrics": {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": round(memory.available / (1024**3), 2),
            "disk_percent": disk.percent,
            "disk_free_gb": round(disk.free / (1024**3), 2)
        }
    }

@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Kubernetes readiness probe endpoint"""
    try:
        # Check database connection
        db.execute(text("SELECT 1"))
        
        # Check Redis connection
        redis_client = get_redis()
        redis_client.ping()
        
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not ready", "error": str(e)}

@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe endpoint"""
    return {"status": "alive"}
