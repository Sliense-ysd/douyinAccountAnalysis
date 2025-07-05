from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class TikHubBaseResponse(BaseModel):
    """TikHub API 基础响应"""
    message: Optional[str] = None
    status_code: Optional[int] = None
    code: Optional[int] = None  # 有时候用code而不是status_code
    router: Optional[str] = None
    params: Optional[Dict[str, Any]] = None
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class VideoStatistics(BaseModel):
    """视频统计数据"""
    aweme_id: Optional[str] = None
    comment_count: Optional[int] = 0
    digg_count: Optional[int] = 0  # 点赞数
    download_count: Optional[int] = 0
    play_count: Optional[int] = 0
    share_count: Optional[int] = 0
    collect_count: Optional[int] = 0  # 收藏数


class VideoAuthor(BaseModel):
    """视频作者信息"""
    sec_uid: Optional[str] = None
    uid: Optional[str] = None
    unique_id: Optional[str] = None
    nickname: Optional[str] = None
    avatar_thumb: Optional[Any] = None  # 可能是字符串或字典
    avatar_medium: Optional[Any] = None
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0
    aweme_count: Optional[int] = 0
    total_favorited: Optional[int] = 0
    signature: Optional[str] = None
    verification_type: Optional[int] = 0
    is_verified: Optional[bool] = False


class VideoMusic(BaseModel):
    """视频音乐信息"""
    id: Optional[Any] = None  # 可能是字符串或整数
    title: Optional[str] = None
    play_url: Optional[Any] = None  # 可能是字符串或字典
    cover_thumb: Optional[Any] = None  # 可能是字符串或字典
    author_name: Optional[str] = None
    duration: Optional[int] = 0


class VideoData(BaseModel):
    """视频数据信息"""
    aweme_id: Optional[str] = None
    vid: Optional[str] = None
    uri: Optional[str] = None
    url_list: Optional[Any] = None  # 可能是列表或字典
    cover: Optional[Any] = None  # 可能是字符串或字典
    play_addr: Optional[Any] = None  # 可能是字符串或字典
    download_addr: Optional[Any] = None  # 可能是字符串或字典
    dynamic_cover: Optional[Any] = None  # 可能是字符串或字典
    origin_cover: Optional[Any] = None  # 可能是字符串或字典
    ratio: Optional[Any] = None  # 可能是字符串或数字
    height: Optional[int] = None
    width: Optional[int] = None
    duration: Optional[int] = None
    bitrate: Optional[int] = None
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class ImageData(BaseModel):
    """图片数据信息"""
    url_list: Optional[List[str]] = None
    width: Optional[int] = None
    height: Optional[int] = None


class VideoInfo(BaseModel):
    """视频完整信息"""
    aweme_id: Optional[str] = None
    video_id: Optional[str] = None  # 现在设为可选
    aweme_type: Optional[int] = 0
    desc: Optional[str] = None
    create_time: Optional[int] = None
    author: Optional[VideoAuthor] = None
    music: Optional[VideoMusic] = None
    statistics: Optional[VideoStatistics] = None
    video_data: Optional[VideoData] = None
    video: Optional[VideoData] = None  # 有时候叫video而不是video_data
    images_data: Optional[List[ImageData]] = None
    risk_infos: Optional[Any] = None
    is_ads: Optional[bool] = False
    is_top: Optional[bool] = False
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class TikHubVideoResponse(TikHubBaseResponse):
    """TikHub 视频响应"""
    data: Optional[VideoInfo] = None


class UserStats(BaseModel):
    """用户统计数据"""
    follower_count: Optional[int] = 0
    following_count: Optional[int] = 0
    aweme_count: Optional[int] = 0
    total_favorited: Optional[int] = 0
    favoriting_count: Optional[int] = 0
    max_follower_count: Optional[int] = 0
    mplatform_followers_count: Optional[int] = 0


class UserInfo(BaseModel):
    """用户信息"""
    sec_uid: str
    uid: Optional[str] = None
    short_id: Optional[str] = None
    unique_id: Optional[str] = None
    nickname: str
    signature: Optional[str] = None
    avatar_thumb: Optional[str] = None
    avatar_medium: Optional[str] = None
    avatar_larger: Optional[str] = None
    verification_type: Optional[int] = 0
    is_private_account: Optional[bool] = False
    custom_verify: Optional[str] = None
    enterprise_verify_reason: Optional[str] = None
    is_star: Optional[bool] = False
    room_id: Optional[str] = None
    live_status: Optional[int] = 0
    country: Optional[str] = None
    language: Optional[str] = None


class UserData(BaseModel):
    """用户数据"""
    user: Optional[UserInfo] = None
    stats: Optional[UserStats] = None
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class TikHubUserResponse(TikHubBaseResponse):
    """TikHub 用户响应"""
    data: Optional[UserData] = None


class UserVideosData(BaseModel):
    """用户视频列表数据"""
    aweme_list: Optional[List[VideoInfo]] = None
    max_cursor: Optional[int] = None
    min_cursor: Optional[int] = None
    has_more: Optional[bool] = False
    time: Optional[int] = None
    total: Optional[int] = None
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class TikHubUserVideosResponse(TikHubBaseResponse):
    """TikHub 用户视频列表响应"""
    data: Optional[UserVideosData] = None


class SearchData(BaseModel):
    """搜索数据"""
    aweme_list: Optional[List[VideoInfo]] = None
    cursor: Optional[int] = None
    has_more: Optional[bool] = False
    log_pb: Optional[Dict[str, Any]] = None
    total: Optional[int] = None
    
    # 接受任何其他字段
    class Config:
        extra = "allow"


class TikHubSearchResponse(TikHubBaseResponse):
    """TikHub 搜索响应"""
    data: Optional[SearchData] = None 