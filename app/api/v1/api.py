from fastapi import APIRouter
from app.api.v1.endpoints import trains, sections, decisions, analytics, simulation, health

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(trains.router, prefix="/trains", tags=["trains"])
api_router.include_router(sections.router, prefix="/sections", tags=["sections"])
api_router.include_router(decisions.router, prefix="/decisions", tags=["decisions"])
api_router.include_router(simulation.router, prefix="/simulation", tags=["simulation"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
