from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional
from loguru import logger
from app.schemas.business_models import ApiResponse, CompetitorAccountAnalysis
from app.services.competitor_account_service import competitor_account_service

router = APIRouter(prefix="/api/v1/competitor-accounts", tags=["对标账号分析"])


@router.get("/{account_id}/heat", response_model=ApiResponse)
async def get_account_heat_info(
    account_id: str = Path(..., description="账号ID")
):
    """
    获取单个账号的热度信息
    """
    try:
        logger.info(f"API调用: 获取账号热度信息, account_id: {account_id}")
        
        result = await competitor_account_service.get_account_heat_info(account_id)
        
        return ApiResponse.success_response(
            data=result,
            message="获取账号热度信息成功"
        )
        
    except Exception as e:
        logger.error(f"获取账号热度信息失败: {account_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取账号热度信息失败: {str(e)}"
        )


@router.get("/heat-ranking", response_model=ApiResponse)
async def get_account_heat_ranking(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取对标账号热度榜单
    """
    try:
        logger.info(f"API调用: 获取对标账号热度榜单, limit: {limit}")
        
        result = await competitor_account_service.get_account_heat_ranking(limit)
        
        return ApiResponse.success_response(
            data=result,
            message="获取对标账号热度榜单成功"
        )
        
    except Exception as e:
        logger.error(f"获取对标账号热度榜单失败, limit: {limit}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取对标账号热度榜单失败: {str(e)}"
        )


@router.get("/heat-ranking/{account_type}", response_model=ApiResponse)
async def get_account_heat_ranking_by_type(
    account_type: str = Path(..., description="账号类型（verified/enterprise/normal）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取指定账号类型的热度榜单
    """
    try:
        logger.info(f"API调用: 获取指定类型账号热度榜单, account_type: {account_type}, limit: {limit}")
        
        if account_type not in ["verified", "enterprise", "normal"]:
            raise HTTPException(
                status_code=400,
                detail="账号类型必须是 verified、enterprise 或 normal"
            )
        
        result = await competitor_account_service.get_account_heat_ranking_by_type(
            account_type, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取指定类型账号热度榜单成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取指定类型账号热度榜单失败, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取指定类型账号热度榜单失败: {str(e)}"
        )


@router.get("/same-level", response_model=ApiResponse)
async def get_accounts_by_follower_range(
    min_followers: int = Query(..., ge=0, description="最小粉丝数"),
    max_followers: int = Query(..., ge=0, description="最大粉丝数"),
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取同层级账号（粉丝数量范围）
    """
    try:
        logger.info(f"API调用: 获取同层级账号, min_followers: {min_followers}, max_followers: {max_followers}, limit: {limit}")
        
        if min_followers > max_followers:
            raise HTTPException(
                status_code=400, 
                detail="最小粉丝数不能大于最大粉丝数"
            )
        
        result = await competitor_account_service.get_accounts_by_follower_range(
            min_followers, max_followers, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取同层级账号成功"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取同层级账号失败, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取同层级账号失败: {str(e)}"
        )


@router.get("/verified-ranking", response_model=ApiResponse)
async def get_verified_account_ranking(
    limit: int = Query(20, ge=1, le=100, description="返回数量限制")
):
    """
    获取认证账号榜单
    """
    try:
        logger.info(f"API调用: 获取认证账号榜单, limit: {limit}")
        
        result = await competitor_account_service.get_verified_account_ranking(limit)
        
        return ApiResponse.success_response(
            data=result,
            message="获取认证账号榜单成功"
        )
        
    except Exception as e:
        logger.error(f"获取认证账号榜单失败, limit: {limit}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取认证账号榜单失败: {str(e)}"
        )


@router.post("/{account_id}/sync", response_model=ApiResponse)
async def sync_account_data(
    account_id: str = Path(..., description="账号ID")
):
    """
    同步账号数据
    """
    try:
        logger.info(f"API调用: 同步账号数据, account_id: {account_id}")
        
        result = await competitor_account_service.sync_account_data(account_id)
        
        return ApiResponse.success_response(
            data=result,
            message="同步账号数据成功"
        )
        
    except Exception as e:
        logger.error(f"同步账号数据失败: {account_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"同步账号数据失败: {str(e)}"
        ) 