from fastapi import APIRouter, HTTPException, Query, Path
from typing import List, Optional, Dict, Any
from loguru import logger
from app.schemas.business_models import ApiResponse, ProductSalesAnalysis
from app.services.product_sales_service import product_sales_service

router = APIRouter(prefix="/api/v1/product-sales", tags=["商品带货分析"])


@router.get("/video/{video_id}", response_model=ApiResponse)
async def get_video_product_sales_data(
    video_id: str = Path(..., description="视频ID")
):
    """
    获取指定视频的商品带货数据
    """
    try:
        logger.info(f"API调用: 获取视频商品带货数据, video_id: {video_id}")
        
        result = await product_sales_service.get_video_product_sales_data(video_id)
        
        return ApiResponse.success_response(
            data=result,
            message="获取视频商品带货数据成功"
        )
        
    except Exception as e:
        logger.error(f"获取视频商品带货数据失败: {video_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取视频商品带货数据失败: {str(e)}"
        )


@router.get("/product/{product_id}", response_model=ApiResponse)
async def get_product_sales_data(
    product_id: str = Path(..., description="商品ID")
):
    """
    获取单个商品的销售数据
    """
    try:
        logger.info(f"API调用: 获取商品销售数据, product_id: {product_id}")
        
        result = await product_sales_service.get_product_sales_data(product_id)
        
        return ApiResponse.success_response(
            data=result,
            message="获取商品销售数据成功"
        )
        
    except Exception as e:
        logger.error(f"获取商品销售数据失败: {product_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取商品销售数据失败: {str(e)}"
        )


@router.get("/top-sales", response_model=ApiResponse)
async def get_top_products_by_sales(
    limit: int = Query(10, ge=1, le=100, description="返回数量限制")
):
    """
    获取TOP销售商品榜单
    """
    try:
        logger.info(f"API调用: 获取TOP销售商品榜单, limit: {limit}")
        
        result = await product_sales_service.get_top_products_by_sales(limit)
        
        return ApiResponse.success_response(
            data=result,
            message="获取TOP销售商品榜单成功"
        )
        
    except Exception as e:
        logger.error(f"获取TOP销售商品榜单失败, limit: {limit}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取TOP销售商品榜单失败: {str(e)}"
        )


@router.get("/category/{category}", response_model=ApiResponse)
async def get_product_sales_by_category(
    category: str = Path(..., description="商品类目"),
    limit: int = Query(10, ge=1, le=100, description="返回数量限制")
):
    """
    获取指定类目的商品销售数据
    """
    try:
        logger.info(f"API调用: 获取指定类目商品销售数据, category: {category}, limit: {limit}")
        
        result = await product_sales_service.get_product_sales_by_category(
            category, limit
        )
        
        return ApiResponse.success_response(
            data=result,
            message="获取指定类目商品销售数据成功"
        )
        
    except Exception as e:
        logger.error(f"获取指定类目商品销售数据失败, category: {category}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取指定类目商品销售数据失败: {str(e)}"
        )


@router.post("/video/{video_id}/sync", response_model=ApiResponse)
async def sync_product_sales_data(
    video_id: str = Path(..., description="视频ID")
):
    """
    同步商品带货数据
    """
    try:
        logger.info(f"API调用: 同步商品带货数据, video_id: {video_id}")
        
        result = await product_sales_service.sync_product_sales_data(video_id)
        
        return ApiResponse.success_response(
            data=result,
            message="同步商品带货数据成功"
        )
        
    except Exception as e:
        logger.error(f"同步商品带货数据失败: {video_id}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"同步商品带货数据失败: {str(e)}"
        )


@router.get("/summary", response_model=ApiResponse)
async def get_product_sales_summary(
    time_range: int = Query(7, ge=1, le=30, description="时间范围（天）")
):
    """
    获取商品销售汇总数据
    """
    try:
        logger.info(f"API调用: 获取商品销售汇总数据, time_range: {time_range}")
        
        result = await product_sales_service.get_product_sales_summary(time_range)
        
        return ApiResponse.success_response(
            data=result,
            message="获取商品销售汇总数据成功"
        )
        
    except Exception as e:
        logger.error(f"获取商品销售汇总数据失败, time_range: {time_range}, 错误: {e}")
        raise HTTPException(
            status_code=500, 
            detail=f"获取商品销售汇总数据失败: {str(e)}"
        ) 