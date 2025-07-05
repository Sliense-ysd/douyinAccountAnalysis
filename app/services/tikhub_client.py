import httpx
import asyncio
from typing import Optional, List, Dict, Any
from loguru import logger
from config.settings import settings
from app.schemas.tikhub_models import (
    TikHubVideoResponse, 
    TikHubUserResponse, 
    TikHubUserVideosResponse,
    TikHubSearchResponse
)


class TikHubClient:
    """TikHub API 客户端"""
    
    def __init__(self):
        self.base_url = settings.TIKHUB_BASE_URL
        self.api_key = settings.TIKHUB_API_KEY
        self.timeout = settings.TIKHUB_TIMEOUT
        self.max_retries = settings.TIKHUB_MAX_RETRIES
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "User-Agent": "DouyinAnalysis/1.0.0"
        }
    
    async def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None, 
                           data: Optional[Dict] = None, retry_count: int = 0) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法
            endpoint: API端点
            params: 查询参数
            data: 请求体数据
            retry_count: 重试次数
            
        Returns:
            响应数据
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    params=params,
                    json=data
                )
                
                response.raise_for_status()
                return response.json()
                
        except httpx.RequestError as e:
            logger.error(f"请求失败: {e}")
            if retry_count < self.max_retries:
                logger.info(f"重试请求, 第{retry_count + 1}次")
                await asyncio.sleep(2 ** retry_count)  # 指数退避
                return await self._make_request(method, endpoint, params, data, retry_count + 1)
            raise
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP错误: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"未知错误: {e}")
            raise
    
    async def get_video_data(self, aweme_id: str) -> TikHubVideoResponse:
        """
        获取单个视频数据
        
        Args:
            aweme_id: 视频ID
            
        Returns:
            视频数据响应
        """
        logger.info(f"获取视频数据: {aweme_id}")
        
        endpoint = "/api/v1/douyin/web/fetch_one_video"
        params = {"aweme_id": aweme_id}
        
        response_data = await self._make_request("GET", endpoint, params=params)
        return TikHubVideoResponse(**response_data)
    
    async def get_user_info(self, sec_uid: str) -> TikHubUserResponse:
        """
        获取用户信息
        
        Args:
            sec_uid: 用户ID
            
        Returns:
            用户信息响应
        """
        logger.info(f"获取用户信息: {sec_uid}")
        
        endpoint = "/api/v1/douyin/web/fetch_user_detail"
        params = {"sec_user_id": sec_uid}
        
        response_data = await self._make_request("GET", endpoint, params=params)
        return TikHubUserResponse(**response_data)
    
    async def get_user_videos(self, sec_uid: str, max_cursor: Optional[int] = None, 
                            count: Optional[int] = None) -> TikHubUserVideosResponse:
        """
        获取用户发布的视频列表
        
        Args:
            sec_uid: 用户ID
            max_cursor: 游标
            count: 数量
            
        Returns:
            用户视频列表响应
        """
        logger.info(f"获取用户视频列表: {sec_uid}, cursor: {max_cursor}, count: {count}")
        
        endpoint = "/api/v1/douyin/web/fetch_user_post_videos"
        params = {"sec_user_id": sec_uid}
        
        if max_cursor is not None:
            params["max_cursor"] = max_cursor
        if count is not None:
            params["count"] = count
            
        response_data = await self._make_request("GET", endpoint, params=params)
        return TikHubUserVideosResponse(**response_data)
    
    async def get_user_like_videos(self, sec_uid: str, max_cursor: Optional[int] = None, 
                                  count: Optional[int] = None) -> TikHubUserVideosResponse:
        """
        获取用户喜欢的视频列表
        
        Args:
            sec_uid: 用户ID
            max_cursor: 游标
            count: 数量
            
        Returns:
            用户喜欢视频列表响应
        """
        logger.info(f"获取用户喜欢视频列表: {sec_uid}, cursor: {max_cursor}, count: {count}")
        
        endpoint = "/api/v1/douyin/web/fetch_user_like_videos"
        params = {"sec_user_id": sec_uid}
        
        if max_cursor is not None:
            params["max_cursor"] = max_cursor
        if count is not None:
            params["count"] = count
            
        response_data = await self._make_request("GET", endpoint, params=params)
        return TikHubUserVideosResponse(**response_data)
    
    async def get_home_feed(self, max_cursor: Optional[int] = None, 
                          count: Optional[int] = None) -> TikHubUserVideosResponse:
        """
        获取首页推荐视频
        
        Args:
            max_cursor: 游标
            count: 数量
            
        Returns:
            推荐视频列表响应
        """
        logger.info(f"获取首页推荐视频: cursor: {max_cursor}, count: {count}")
        
        endpoint = "/api/v1/douyin/web/fetch_home_feed"
        params = {}
        
        if max_cursor is not None:
            params["max_cursor"] = max_cursor
        if count is not None:
            params["count"] = count
            
        response_data = await self._make_request("GET", endpoint, params=params)
        
        # 转换API响应格式以匹配我们的模型
        normalized_response = {
            "message": "获取首页推荐视频成功",
            "status_code": response_data.get("code", 0),
            "data": response_data.get("data", {})
        }
        
        return TikHubUserVideosResponse(**normalized_response)
    
    async def search_videos(self, keyword: str, offset: Optional[int] = None, 
                          count: Optional[int] = None) -> TikHubSearchResponse:
        """
        根据关键词搜索视频
        
        Args:
            keyword: 关键词
            offset: 偏移量
            count: 数量
            
        Returns:
            搜索结果响应
        """
        logger.info(f"搜索视频: {keyword}, offset: {offset}, count: {count}")
        
        endpoint = "/api/v1/douyin/web/fetch_general_search"
        params = {"keyword": keyword}
        
        if offset is not None:
            params["offset"] = offset
        if count is not None:
            params["count"] = count
            
        response_data = await self._make_request("GET", endpoint, params=params)
        return TikHubSearchResponse(**response_data)
    
    async def batch_get_videos(self, aweme_ids: List[str]) -> List[TikHubVideoResponse]:
        """
        批量获取视频数据
        
        Args:
            aweme_ids: 视频ID列表
            
        Returns:
            视频数据响应列表
        """
        logger.info(f"批量获取视频数据: {len(aweme_ids)} 个视频")
        
        tasks = [self.get_video_data(aweme_id) for aweme_id in aweme_ids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"获取视频 {aweme_ids[i]} 失败: {response}")
                # 创建一个错误响应
                error_response = TikHubVideoResponse(
                    message=f"获取视频失败: {response}",
                    status_code=-1,
                    data=None
                )
                results.append(error_response)
            else:
                results.append(response)
        
        return results
    
    async def batch_get_users(self, sec_uids: List[str]) -> List[TikHubUserResponse]:
        """
        批量获取用户信息
        
        Args:
            sec_uids: 用户ID列表
            
        Returns:
            用户信息响应列表
        """
        logger.info(f"批量获取用户信息: {len(sec_uids)} 个用户")
        
        tasks = [self.get_user_info(sec_uid) for sec_uid in sec_uids]
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                logger.error(f"获取用户 {sec_uids[i]} 失败: {response}")
                # 创建一个错误响应
                error_response = TikHubUserResponse(
                    message=f"获取用户失败: {response}",
                    status_code=-1,
                    data=None
                )
                results.append(error_response)
            else:
                results.append(response)
        
        return results


# 创建全局客户端实例
tikhub_client = TikHubClient() 