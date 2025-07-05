from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class VideoType(str, Enum):
    """视频类型"""
    FULL_POPULAR = "full_popular"      # 全量爆款
    SAME_LEVEL = "same_level"          # 同层级爆款
    LOW_FAN = "low_fan"                # 低粉爆款


class AccountType(str, Enum):
    """账号类型"""
    NORMAL = "normal"         # 普通账号
    VERIFIED = "verified"     # 认证账号
    ENTERPRISE = "enterprise" # 企业账号


class PopularVideoAnalysis(BaseModel):
    """爆款视频分析结果"""
    video_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    
    # 作者信息
    account_id: str
    account_name: str
    follower_count: Optional[int] = 0
    
    # 互动数据
    like_count: Optional[int] = 0
    comment_count: Optional[int] = 0
    share_count: Optional[int] = 0
    collect_count: Optional[int] = 0
    play_count: Optional[int] = 0
    
    # 分析结果
    interaction_score: float = 0.0    # 互动热度分数
    video_type: VideoType
    ranking: Optional[int] = None     # 排名
    
    # 时间信息
    create_time: Optional[datetime] = None
    analysis_time: Optional[datetime] = None
    
    # 媒体信息
    cover_url: Optional[str] = None
    play_url: Optional[str] = None


class CompetitorAccountAnalysis(BaseModel):
    """对标账号分析结果"""
    account_id: str
    account_name: str
    avatar_url: Optional[str] = None
    description: Optional[str] = None
    
    # 基础数据
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0
    video_count: Optional[int] = 0
    total_like_count: Optional[int] = 0
    
    # 平均数据
    avg_play_count: Optional[int] = 0
    avg_like_count: Optional[int] = 0
    avg_comment_count: Optional[int] = 0
    avg_share_count: Optional[int] = 0
    
    # 分析结果
    heat_score: float = 0.0           # 热度分数
    heat_ranking: Optional[int] = None # 热度排名
    account_type: AccountType
    verification_status: bool = False
    
    # 时间信息
    last_active_time: Optional[datetime] = None
    analysis_time: Optional[datetime] = None


class ProductSalesAnalysis(BaseModel):
    """商品销售分析结果"""
    product_id: str
    product_name: str
    product_image: Optional[str] = None
    product_price: Optional[float] = 0.0
    
    # 销售数据
    video_id: Optional[str] = None
    sales_count: Optional[int] = 0      # 销量
    sales_amount: Optional[float] = 0.0 # 销售额
    commission_rate: Optional[float] = 0.0 # 佣金比例
    
    # 商品信息
    category: Optional[str] = None
    brand: Optional[str] = None
    shop_name: Optional[str] = None
    
    # 时间信息
    sale_date: Optional[datetime] = None
    analysis_time: Optional[datetime] = None


class PopularVideoRanking(BaseModel):
    """爆款视频榜单"""
    video_analysis: PopularVideoAnalysis
    product_sales: List[ProductSalesAnalysis] = []
    
    # 综合评分
    comprehensive_score: float = 0.0
    final_ranking: Optional[int] = None


class ApiResponse(BaseModel):
    """API 响应基础模型"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    timestamp: Optional[datetime] = None
    
    @classmethod
    def success_response(cls, data: Any = None, message: str = "操作成功"):
        return cls(
            success=True,
            message=message,
            data=data,
            timestamp=datetime.now()
        )
    
    @classmethod
    def error_response(cls, message: str = "操作失败", data: Any = None):
        return cls(
            success=False,
            message=message,
            data=data,
            timestamp=datetime.now()
        )


class VideoAnalysisRequest(BaseModel):
    """视频分析请求"""
    video_id: str
    analysis_type: VideoType
    limit: Optional[int] = 20
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None


class AccountAnalysisRequest(BaseModel):
    """账号分析请求"""
    account_id: Optional[str] = None
    analysis_type: str = "heat_info"  # heat_info, heat_ranking, same_level, verified_ranking
    limit: Optional[int] = 20
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    account_type: Optional[str] = None


class ProductSalesRequest(BaseModel):
    """商品销售分析请求"""
    target_id: str  # 可以是video_id或product_id
    analysis_type: str = "video_products"  # video_products, product_sales, top_sales, category_sales
    limit: Optional[int] = 10
    category: Optional[str] = None 