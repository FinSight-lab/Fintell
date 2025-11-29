"""FastAPI application entry point"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.core.config import settings
from app.core.logging import setup_logging, get_logger
from app.core.exceptions import PortfolioManagerError

# 配置日志
log_level = settings.LOG_LEVEL if not settings.DEBUG else "DEBUG"
setup_logging(level=log_level)

logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Smart Portfolio Management System API"
)


# ============================================================================
# 全局异常处理器
# ============================================================================

@app.exception_handler(PortfolioManagerError)
async def portfolio_manager_exception_handler(request: Request, exc: PortfolioManagerError):
    """处理自定义异常"""
    logger.error(f"[{exc.error_code}] {request.url.path}: {exc.message}")
    return JSONResponse(
        status_code=400,
        content={
            "success": False,
            "error": exc.to_dict()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """处理未捕获的异常"""
    logger.error(f"未处理的异常 {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "error_code": "INTERNAL_ERROR",
                "message": "服务器内部错误，请稍后重试",
                "details": {"type": type(exc).__name__}
            }
        }
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """应用启动事件"""
    logger.info("=" * 60)
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} 启动中...")
    logger.info(f"   日志级别: {log_level}")
    logger.info(f"   调试模式: {settings.DEBUG}")
    logger.info("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭事件"""
    logger.info("👋 应用正在关闭...")


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


# Include API routers
from app.api import reports

app.include_router(reports.router, prefix="/api/reports", tags=["reports"])

logger.info("✓ API 路由注册完成")
