import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from config.settings import settings
from app.schemas.business_models import (
    PopularVideoAnalysis, 
    VideoType, 
    PopularVideoRanking,
    ProductSalesAnalysis
)
from app.schemas.tikhub_models import VideoInfo, VideoStatistics, VideoAuthor
from app.services.tikhub_client import tikhub_client


class PopularVideoService:
    """爆款视频分析服务"""
    
    def __init__(self):
        self.config = settings.POPULAR_VIDEO_CONFIG
        self.interaction_weights = self.config["interaction_weights"]
        
    def calculate_interaction_score(self, statistics: VideoStatistics) -> float:
        """
        计算互动热度分数
        公式: 点赞 + 评论*1.5 + 转发 + 收藏*1.5
        
        Args:
            statistics: 视频统计数据
            
        Returns:
            互动热度分数
        """
        if not statistics:
            return 0.0
            
        like_count = statistics.digg_count or 0
        comment_count = statistics.comment_count or 0
        share_count = statistics.share_count or 0
        collect_count = statistics.collect_count or 0
        
        score = (
            like_count * self.interaction_weights["like"] +
            comment_count * self.interaction_weights["comment"] +
            share_count * self.interaction_weights["share"] +
            collect_count * self.interaction_weights["collect"]
        )
        
        return float(score)
    
    def convert_tikhub_video_to_analysis(self, video_info: VideoInfo, 
                                       video_type: VideoType) -> PopularVideoAnalysis:
        """
        将TikHub视频数据转换为分析结果
        
        Args:
            video_info: TikHub视频信息
            video_type: 视频类型
            
        Returns:
            爆款视频分析结果
        """
        # 计算互动分数
        interaction_score = self.calculate_interaction_score(video_info.statistics)
        
        # 获取创建时间
        create_time = None
        if video_info.create_time:
            create_time = datetime.fromtimestamp(video_info.create_time)
        
        # 构建分析结果
        analysis = PopularVideoAnalysis(
            video_id=video_info.aweme_id,
            title=video_info.desc,
            description=video_info.desc,
            
            # 作者信息
            account_id=video_info.author.sec_uid if video_info.author else "",
            account_name=video_info.author.nickname if video_info.author else "",
            follower_count=video_info.author.follower_count if video_info.author else 0,
            
            # 互动数据
            like_count=video_info.statistics.digg_count if video_info.statistics else 0,
            comment_count=video_info.statistics.comment_count if video_info.statistics else 0,
            share_count=video_info.statistics.share_count if video_info.statistics else 0,
            collect_count=video_info.statistics.collect_count if video_info.statistics else 0,
            play_count=video_info.statistics.play_count if video_info.statistics else 0,
            
            # 分析结果
            interaction_score=interaction_score,
            video_type=video_type,
            
            # 时间信息
            create_time=create_time,
            analysis_time=datetime.now(),
            
            # 媒体信息
            cover_url=video_info.video_data.cover if video_info.video_data else None,
            play_url=video_info.video_data.play_addr if video_info.video_data else None
        )
        
        return analysis
    
    async def get_popular_video_interaction_data(self, video_id: str) -> PopularVideoAnalysis:
        """
        获取单条爆款视频的互动数据
        
        Args:
            video_id: 视频ID
            
        Returns:
            爆款视频分析结果
        """
        logger.info(f"获取爆款视频互动数据: {video_id}")
        
        try:
            # 调用TikHub API获取视频数据
            response = await tikhub_client.get_video_data(video_id)
            
            if response.status_code != 0 or not response.data:
                raise ValueError(f"获取视频数据失败: {response.message}")
            
            # 转换为分析结果
            analysis = self.convert_tikhub_video_to_analysis(
                response.data, 
                VideoType.FULL_POPULAR
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"获取爆款视频互动数据失败: {video_id}, 错误: {e}")
            raise
    
    async def get_full_popular_videos(self, limit: int = 20) -> List[PopularVideoAnalysis]:
        """
        获取全量爆款视频TOP榜单
        
        Args:
            limit: 返回数量限制
            
        Returns:
            爆款视频分析结果列表
        """
        logger.info(f"获取全量爆款视频TOP榜单: limit={limit}")
        
        try:
            # 获取热门视频列表
            response = await tikhub_client.get_home_feed(count=limit * 2)  # 多获取一些用于筛选
            
            # TikHub API 成功时返回 status_code 为 200
            if response.status_code != 200 or not response.data:
                raise ValueError(f"获取热门视频失败: {response.message}")
            
            video_list = response.data.aweme_list
            
            # 转换为分析结果并计算互动分数
            analyses = []
            for video in video_list:
                analysis = self.convert_tikhub_video_to_analysis(video, VideoType.FULL_POPULAR)
                analyses.append(analysis)
            
            # 按互动分数排序
            analyses.sort(key=lambda x: x.interaction_score, reverse=True)
            
            # 取TOP百分比
            top_count = int(len(analyses) * self.config["full_popular_top_percent"])
            top_analyses = analyses[:max(top_count, limit)]
            
            # 设置排名
            for i, analysis in enumerate(top_analyses):
                analysis.ranking = i + 1
            
            return top_analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取全量爆款视频失败: {e}")
            raise
    
    async def get_same_level_popular_videos(self, min_followers: int, max_followers: int, 
                                          limit: int = 20) -> List[PopularVideoAnalysis]:
        """
        获取同层级爆款视频（粉丝量级一致）
        
        Args:
            min_followers: 最小粉丝数
            max_followers: 最大粉丝数
            limit: 返回数量限制
            
        Returns:
            爆款视频分析结果列表
        """
        logger.info(f"获取同层级爆款视频: {min_followers}-{max_followers}, limit={limit}")
        
        try:
            # 获取更多视频用于筛选
            response = await tikhub_client.get_home_feed(count=limit * 3)
            
            # TikHub API 成功时返回 status_code 为 200
            if response.status_code != 200 or not response.data:
                raise ValueError(f"获取视频失败: {response.message}")
            
            video_list = response.data.aweme_list
            
            # 筛选同层级视频
            same_level_videos = []
            for video in video_list:
                if video.author and video.author.follower_count:
                    follower_count = video.author.follower_count
                    if min_followers <= follower_count <= max_followers:
                        same_level_videos.append(video)
            
            # 转换为分析结果
            analyses = []
            for video in same_level_videos:
                analysis = self.convert_tikhub_video_to_analysis(video, VideoType.SAME_LEVEL)
                analyses.append(analysis)
            
            # 按互动分数排序
            analyses.sort(key=lambda x: x.interaction_score, reverse=True)
            
            # 取TOP百分比
            top_count = int(len(analyses) * self.config["same_level_top_percent"])
            top_analyses = analyses[:max(top_count, limit)]
            
            # 设置排名
            for i, analysis in enumerate(top_analyses):
                analysis.ranking = i + 1
            
            return top_analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取同层级爆款视频失败: {e}")
            raise
    
    async def get_low_fan_popular_videos(self, max_followers: int, 
                                       limit: int = 20) -> List[PopularVideoAnalysis]:
        """
        获取低粉爆款视频（最低粉丝等级）
        
        Args:
            max_followers: 最大粉丝数
            limit: 返回数量限制
            
        Returns:
            爆款视频分析结果列表
        """
        logger.info(f"获取低粉爆款视频: max_followers={max_followers}, limit={limit}")
        
        try:
            # 获取更多视频用于筛选
            response = await tikhub_client.get_home_feed(count=limit * 4)
            
            # TikHub API 成功时返回 status_code 为 200
            if response.status_code != 200 or not response.data:
                raise ValueError(f"获取视频失败: {response.message}")
            
            video_list = response.data.aweme_list
            
            # 筛选低粉视频
            low_fan_videos = []
            for video in video_list:
                if video.author and video.author.follower_count:
                    follower_count = video.author.follower_count
                    if follower_count <= max_followers:
                        low_fan_videos.append(video)
            
            # 转换为分析结果
            analyses = []
            for video in low_fan_videos:
                analysis = self.convert_tikhub_video_to_analysis(video, VideoType.LOW_FAN)
                analyses.append(analysis)
            
            # 按互动分数排序
            analyses.sort(key=lambda x: x.interaction_score, reverse=True)
            
            # 取TOP百分比
            top_count = int(len(analyses) * self.config["low_fan_top_percent"])
            top_analyses = analyses[:max(top_count, limit)]
            
            # 设置排名
            for i, analysis in enumerate(top_analyses):
                analysis.ranking = i + 1
            
            return top_analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取低粉爆款视频失败: {e}")
            raise
    
    async def get_popular_video_ranking(self, video_type: Optional[str] = None, 
                                      limit: int = 20) -> List[PopularVideoRanking]:
        """
        获取爆款视频榜单（汇总互动数据和商品销量数据）
        
        Args:
            video_type: 视频类型
            limit: 返回数量限制
            
        Returns:
            爆款视频榜单列表
        """
        logger.info(f"获取爆款视频榜单: type={video_type}, limit={limit}")
        
        try:
            # 根据类型获取爆款视频
            if video_type == "same_level":
                # 这里需要传入具体的粉丝数范围，暂时使用默认值
                analyses = await self.get_same_level_popular_videos(10000, 100000, limit)
            elif video_type == "low_fan":
                analyses = await self.get_low_fan_popular_videos(10000, limit)
            else:
                analyses = await self.get_full_popular_videos(limit)
            
            # 构建榜单结果
            rankings = []
            for i, analysis in enumerate(analyses):
                # 这里应该调用商品销售服务获取销售数据
                # 暂时使用空列表
                product_sales = []
                
                # 计算综合评分（互动分数 + 商品销售额）
                comprehensive_score = analysis.interaction_score
                if product_sales:
                    sales_score = sum(p.sales_amount for p in product_sales)
                    comprehensive_score += sales_score * 0.1  # 销售额权重
                
                ranking = PopularVideoRanking(
                    video_analysis=analysis,
                    product_sales=product_sales,
                    comprehensive_score=comprehensive_score,
                    final_ranking=i + 1
                )
                rankings.append(ranking)
            
            # 按综合评分重新排序
            rankings.sort(key=lambda x: x.comprehensive_score, reverse=True)
            
            # 更新最终排名
            for i, ranking in enumerate(rankings):
                ranking.final_ranking = i + 1
            
            return rankings
            
        except Exception as e:
            logger.error(f"获取爆款视频榜单失败: {e}")
            raise
    
    async def sync_popular_video_data(self, video_id: str) -> PopularVideoAnalysis:
        """
        同步爆款视频数据
        
        Args:
            video_id: 视频ID
            
        Returns:
            同步后的爆款视频分析结果
        """
        logger.info(f"同步爆款视频数据: {video_id}")
        
        try:
            # 获取最新视频数据
            analysis = await self.get_popular_video_interaction_data(video_id)
            
            # 这里应该保存到数据库
            # 暂时直接返回分析结果
            
            return analysis
            
        except Exception as e:
            logger.error(f"同步爆款视频数据失败: {video_id}, 错误: {e}")
            raise


# 创建全局服务实例
popular_video_service = PopularVideoService() 