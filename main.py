import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
root_dir = Path(__file__).parent
sys.path.insert(0, str(root_dir))

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger
import uvicorn
from datetime import datetime

# 导入配置
from config.settings import settings

# 导入路由
from app.api.popular_video_api import router as popular_video_router
from app.api.competitor_account_api import router as competitor_account_router
from app.api.product_sales_api import router as product_sales_router

# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.VERSION,
    description="抖音账号诊断分析系统 - Python版本",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 配置日志
logger.remove()
logger.add(
    sys.stdout,
    format=settings.LOG_FORMAT,
    level=settings.LOG_LEVEL,
    colorize=True
)

# 注册路由
app.include_router(popular_video_router)
app.include_router(competitor_account_router)
app.include_router(product_sales_router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理器"""
    logger.error(f"全局异常: {request.url} - {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": f"服务器内部错误: {str(exc)}",
            "data": None,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/")
async def root():
    """根路径"""
    return {
        "success": True,
        "message": "抖音分析系统运行正常",
        "data": {
            "app_name": settings.APP_NAME,
            "version": settings.VERSION,
            "status": "running",
            "timestamp": datetime.now().isoformat()
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "success": True,
        "message": "服务健康",
        "data": {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "tikhub_api": "connected",
                "popular_video_service": "running",
                "competitor_account_service": "running",
                "product_sales_service": "running"
            }
        }
    }


@app.get("/api/info")
async def api_info():
    """API信息"""
    return {
        "success": True,
        "message": "API信息",
        "data": {
            "name": settings.APP_NAME,
            "version": settings.VERSION,
            "description": "抖音账号诊断分析系统API",
            "endpoints": {
                "popular_videos": "/api/v1/popular-videos",
                "competitor_accounts": "/api/v1/competitor-accounts", 
                "product_sales": "/api/v1/product-sales"
            },
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    logger.info(f"启动 {settings.APP_NAME} v{settings.VERSION}")
    logger.info(f"调试模式: {settings.DEBUG}")
    logger.info(f"TikHub API: {settings.TIKHUB_BASE_URL}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    ) 