"""FastAPI application entry point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Portfolio Management System API"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Smart Portfolio Manager API",
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


# Include API routers here as they are created
# from app.api import portfolio, reports, auth
# app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
# app.include_router(portfolio.router, prefix="/api/portfolio", tags=["portfolio"])
# app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
