from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基本配置
    APP_NAME: str = "抖音分析系统"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # TikHub API 配置
    TIKHUB_BASE_URL: str = "https://api.tikhub.io"
    TIKHUB_API_KEY: str = ""
    TIKHUB_TIMEOUT: int = 30
    TIKHUB_MAX_RETRIES: int = 3
    
    # 数据库配置
    DATABASE_URL: Optional[str] = None
    
    # Redis 配置
    REDIS_URL: Optional[str] = None
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
    # 爆款视频分析配置
    POPULAR_VIDEO_CONFIG: dict = {
        "full_popular_top_percent": 0.05,  # 全量爆款TOP 5%
        "same_level_top_percent": 0.05,    # 同层级爆款TOP 5%
        "low_fan_top_percent": 0.05,       # 低粉爆款TOP 5%
        "interaction_weights": {           # 互动数据权重
            "like": 1.0,
            "comment": 1.5,
            "share": 1.0,
            "collect": 1.5
        }
    }
    
    # 账号分析配置
    ACCOUNT_ANALYSIS_CONFIG: dict = {
        "heat_score_weights": {
            "follower_count": 0.3,
            "avg_play_count": 0.4,
            "avg_like_count": 0.2,
            "avg_comment_count": 0.1
        },
        "follower_levels": {
            "low": {"min": 0, "max": 10000},
            "medium": {"min": 10000, "max": 100000},
            "high": {"min": 100000, "max": 1000000},
            "super": {"min": 1000000, "max": float('inf')}
        }
    }
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 创建全局设置实例
settings = Settings() 