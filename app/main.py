from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import uvicorn
import structlog
from pathlib import Path

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import engine, Base
from app import models  # noqa: F401  Ensure models are imported for metadata

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="An intelligent decision-support system for Indian Railway Department section controllers",
    openapi_url="/api/v1/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1")

# Serve static files (frontend)
if Path("frontend/dist").exists():
    app.mount("/static", StaticFiles(directory="frontend/dist"), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    logger.info("Starting Railway Intelligent Decision Support System")
    
    # Create database tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Railway Intelligent Decision Support System")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the main application page"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Railway Intelligent Decision Support System</title>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body { 
                font-family: Arial, sans-serif; 
                margin: 0; 
                padding: 20px; 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                min-height: 100vh;
            }
            .container { 
                max-width: 800px; 
                margin: 0 auto; 
                text-align: center;
                padding: 40px 20px;
            }
            .logo {
                font-size: 3em;
                margin-bottom: 20px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            .subtitle {
                font-size: 1.2em;
                margin-bottom: 40px;
                opacity: 0.9;
            }
            .features {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 40px 0;
            }
            .feature {
                background: rgba(255,255,255,0.1);
                padding: 20px;
                border-radius: 10px;
                backdrop-filter: blur(10px);
            }
            .links {
                margin-top: 40px;
            }
            .links a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                padding: 10px 20px;
                border: 2px solid white;
                border-radius: 25px;
                transition: all 0.3s;
            }
            .links a:hover {
                background: white;
                color: #667eea;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">🚂 RIDSS</div>
            <h1>Railway Intelligent Decision Support System</h1>
            <p class="subtitle">AI-Powered Train Scheduling & Optimization for Indian Railways</p>
            
            <div class="features">
                <div class="feature">
                    <h3>🤖 AI Optimization</h3>
                    <p>Advanced algorithms for train precedence and crossing decisions</p>
                </div>
                <div class="feature">
                    <h3>⚡ Real-time Scheduling</h3>
                    <p>Dynamic conflict-free schedule generation with rapid re-optimization</p>
                </div>
                <div class="feature">
                    <h3>📊 Performance Analytics</h3>
                    <p>Comprehensive KPIs and dashboards for continuous improvement</p>
                </div>
                <div class="feature">
                    <h3>🔄 What-if Simulation</h3>
                    <p>Scenario analysis for alternative routings and strategies</p>
                </div>
            </div>
            
            <div class="links">
                <a href="/docs">API Documentation</a>
                <a href="/redoc">API Reference</a>
                <a href="/api/v1/health">Health Check</a>
            </div>
        </div>
    </body>
    </html>
    """

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower()
    )
