from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from loguru import logger
from app.schemas.business_models import (
    ApiResponse, 
    PopularVideoAnalysis, 
    PopularVideoRanking,
    VideoType
)
from app.services.popular_video_service import popular_video_service

router = APIRouter(prefix="/api/v1/popular-videos", tags=["爆款视频分析"])


@router.get("/{video_id}/interaction", response_model=ApiResponse)
async def get_video_interaction_data(video_id: str):
    """
    获取单条爆款视频的互动数据
    """
    try:
        logger.info(f"API调用: 获取爆款视频互动数据, video_id: {video_id}")
        
        result = await popular_video_service.get_popular_video_interaction_data(video_id)
        
        return ApiResponse.success_response(
            data=result,
            message="获取爆款视频互动数据成功"
        )
        
    except Exception as e:
        logger.error(f"获取爆款视频互动数据失败: {video_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取爆款视频互动数据失败: {str(e)}"
        )


@router.get("/full-popular", response_model=ApiResponse)
async def get_full_popular_videos(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取全量爆款视频TOP榜单
    """
    try:
        logger.info(f"API调用: 获取全量爆款视频榜单, limit: {limit}")
        
        result = await popular_video_service.get_full_popular_videos(limit)
        
        return ApiResponse.success_response(
            data=result,
            message="获取全量爆款视频榜单成功"
        )
        
    except Exception as e:
        logger.error(f"获取全量爆款视频榜单失败, limit: {limit}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取全量爆款视频榜单失败: {str(e)}"
        )


@router.get("/same-level", response_model=ApiResponse)
async def get_same_level_popular_videos(
    min_followers: int = Query(..., ge=0, description="最小粉丝数"),
    max_followers: int = Query(..., ge=0, description="最大粉丝数"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取同层级爆款视频（粉丝量级一致）
    """
    try:
        logger.info(f"API调用: 获取同层级爆款视频, min_followers: {min_followers}, max_followers: {max_followers}, limit: {limit}")
        
        if min_followers > max_followers:
            raise HTTPException(
                status_code=400, 
                detail="最小粉丝数不能大于最大粉丝数"
            )
        
        result = await popular_video_service.get_same_level_popular_videos(
            min_followers, max_followers, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取同层级爆款视频成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取同层级爆款视频失败, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取同层级爆款视频失败: {str(e)}"
        )


@router.get("/low-fan", response_model=ApiResponse)
async def get_low_fan_popular_videos(
    max_followers: int = Query(..., ge=0, description="最大粉丝数"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取低粉爆款视频（最低粉丝等级）
    """
    try:
        logger.info(f"API调用: 获取低粉爆款视频, max_followers: {max_followers}, limit: {limit}")
        
        result = await popular_video_service.get_low_fan_popular_videos(
            max_followers, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取低粉爆款视频成功"
        )
        
    except Exception as e:
        logger.error(f"获取低粉爆款视频失败, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取低粉爆款视频失败: {str(e)}"
        )


@router.get("/ranking", response_model=ApiResponse)
async def get_popular_video_ranking(
    video_type: Optional[str] = Query(None, description="视频类型"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取爆款视频榜单（汇总互动数据和商品销量数据）
    """
    try:
        logger.info(f"API调用: 获取爆款视频榜单, video_type: {video_type}, limit: {limit}")
        
        result = await popular_video_service.get_popular_video_ranking(
            video_type, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取爆款视频榜单成功"
        )
        
    except Exception as e:
        logger.error(f"获取爆款视频榜单失败, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取爆款视频榜单失败: {str(e)}"
        )


@router.post("/{video_id}/sync", response_model=ApiResponse)
async def sync_popular_video_data(video_id: str):
    """
    同步爆款视频数据
    """
    try:
        logger.info(f"API调用: 同步爆款视频数据, video_id: {video_id}")
        
        result = await popular_video_service.sync_popular_video_data(video_id)
        
        return ApiResponse.success_response(
            data=result,
            message="同步爆款视频数据成功"
        )
        
    except Exception as e:
        logger.error(f"同步爆款视频数据失败: {video_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"同步爆款视频数据失败: {str(e)}"
        ) 