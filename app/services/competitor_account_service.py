import asyncio
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger
from config.settings import settings
from app.schemas.business_models import CompetitorAccountAnalysis, AccountType
from app.schemas.tikhub_models import UserInfo, UserStats, VideoInfo
from app.services.tikhub_client import tikhub_client


class CompetitorAccountService:
    """对标账号分析服务"""
    
    def __init__(self):
        self.config = settings.ACCOUNT_ANALYSIS_CONFIG
        self.heat_weights = self.config["heat_score_weights"]
        self.follower_levels = self.config["follower_levels"]
    
    def calculate_heat_score(self, account_data: Dict[str, Any]) -> float:
        """
        计算账号热度分数
        
        Args:
            account_data: 账号数据
            
        Returns:
            热度分数
        """
        score = 0.0
        
        # 粉丝数权重：30%
        follower_count = account_data.get("follower_count", 0)
        score += follower_count * self.heat_weights["follower_count"]
        
        # 平均播放量权重：40%
        avg_play_count = account_data.get("avg_play_count", 0)
        score += avg_play_count * self.heat_weights["avg_play_count"]
        
        # 平均点赞数权重：20%
        avg_like_count = account_data.get("avg_like_count", 0)
        score += avg_like_count * self.heat_weights["avg_like_count"]
        
        # 平均评论数权重：10%
        avg_comment_count = account_data.get("avg_comment_count", 0)
        score += avg_comment_count * self.heat_weights["avg_comment_count"]
        
        return score
    
    def determine_account_type(self, user_info: UserInfo) -> AccountType:
        """
        判断账号类型
        
        Args:
            user_info: 用户信息
            
        Returns:
            账号类型
        """
        if user_info.verification_type and user_info.verification_type > 0:
            return AccountType.VERIFIED
        
        if user_info.custom_verify and user_info.custom_verify.strip():
            return AccountType.ENTERPRISE
        
        return AccountType.NORMAL
    
    def calculate_average_metrics(self, video_list: List[VideoInfo]) -> Dict[str, float]:
        """
        计算平均数据指标
        
        Args:
            video_list: 视频列表
            
        Returns:
            平均数据指标
        """
        if not video_list:
            return {
                "avg_play_count": 0.0,
                "avg_like_count": 0.0,
                "avg_comment_count": 0.0,
                "avg_share_count": 0.0
            }
        
        total_play = 0
        total_like = 0
        total_comment = 0
        total_share = 0
        valid_videos = 0
        
        for video in video_list:
            if video.statistics:
                stats = video.statistics
                total_play += stats.play_count or 0
                total_like += stats.digg_count or 0
                total_comment += stats.comment_count or 0
                total_share += stats.share_count or 0
                valid_videos += 1
        
        if valid_videos == 0:
            return {
                "avg_play_count": 0.0,
                "avg_like_count": 0.0,
                "avg_comment_count": 0.0,
                "avg_share_count": 0.0
            }
        
        return {
            "avg_play_count": total_play / valid_videos,
            "avg_like_count": total_like / valid_videos,
            "avg_comment_count": total_comment / valid_videos,
            "avg_share_count": total_share / valid_videos
        }
    
    def convert_tikhub_user_to_analysis(self, user_info: UserInfo, user_stats: UserStats, 
                                      video_list: List[VideoInfo]) -> CompetitorAccountAnalysis:
        """
        将TikHub用户数据转换为分析结果
        
        Args:
            user_info: 用户信息
            user_stats: 用户统计
            video_list: 视频列表
            
        Returns:
            对标账号分析结果
        """
        # 计算平均数据
        avg_metrics = self.calculate_average_metrics(video_list)
        
        # 准备热度分数计算数据
        heat_data = {
            "follower_count": user_stats.follower_count or 0,
            "avg_play_count": avg_metrics["avg_play_count"],
            "avg_like_count": avg_metrics["avg_like_count"],
            "avg_comment_count": avg_metrics["avg_comment_count"]
        }
        
        # 计算热度分数
        heat_score = self.calculate_heat_score(heat_data)
        
        # 判断账号类型
        account_type = self.determine_account_type(user_info)
        
        # 构建分析结果
        analysis = CompetitorAccountAnalysis(
            account_id=user_info.sec_uid,
            account_name=user_info.nickname,
            avatar_url=user_info.avatar_larger,
            description=user_info.signature,
            
            # 基础数据
            follower_count=user_stats.follower_count or 0,
            following_count=user_stats.following_count or 0,
            video_count=user_stats.aweme_count or 0,
            total_like_count=user_stats.total_favorited or 0,
            
            # 平均数据
            avg_play_count=int(avg_metrics["avg_play_count"]),
            avg_like_count=int(avg_metrics["avg_like_count"]),
            avg_comment_count=int(avg_metrics["avg_comment_count"]),
            avg_share_count=int(avg_metrics["avg_share_count"]),
            
            # 分析结果
            heat_score=heat_score,
            account_type=account_type,
            verification_status=user_info.verification_type > 0 if user_info.verification_type else False,
            
            # 时间信息
            last_active_time=datetime.now(),
            analysis_time=datetime.now()
        )
        
        return analysis
    
    async def get_account_heat_info(self, account_id: str) -> CompetitorAccountAnalysis:
        """
        获取单个账号的热度信息
        
        Args:
            account_id: 账号ID
            
        Returns:
            对标账号分析结果
        """
        logger.info(f"获取账号热度信息: {account_id}")
        
        try:
            # 获取用户信息
            user_response = await tikhub_client.get_user_info(account_id)
            if user_response.status_code != 0 or not user_response.data:
                raise ValueError(f"获取用户信息失败: {user_response.message}")
            
            user_data = user_response.data
            
            # 获取用户视频列表用于计算平均数据
            videos_response = await tikhub_client.get_user_videos(account_id, count=20)
            video_list = []
            if videos_response.status_code == 0 and videos_response.data:
                video_list = videos_response.data.aweme_list
            
            # 转换为分析结果
            analysis = self.convert_tikhub_user_to_analysis(
                user_data.user, 
                user_data.stats, 
                video_list
            )
            
            return analysis
            
        except Exception as e:
            logger.error(f"获取账号热度信息失败: {account_id}, 错误: {e}")
            raise
    
    async def get_account_heat_ranking(self, limit: int = 20) -> List[CompetitorAccountAnalysis]:
        """
        获取对标账号热度榜单
        
        Args:
            limit: 返回数量限制
            
        Returns:
            对标账号热度榜单
        """
        logger.info(f"获取对标账号热度榜单: limit={limit}")
        
        try:
            # 获取热门视频列表，从中提取账号信息
            response = await tikhub_client.get_home_feed(count=limit * 2)
            
            if response.status_code != 0 or not response.data:
                raise ValueError(f"获取热门视频失败: {response.message}")
            
            video_list = response.data.aweme_list
            
            # 提取唯一账号ID
            unique_accounts = {}
            for video in video_list:
                if video.author and video.author.sec_uid:
                    account_id = video.author.sec_uid
                    if account_id not in unique_accounts:
                        unique_accounts[account_id] = []
                    unique_accounts[account_id].append(video)
            
            # 批量获取账号分析结果
            analyses = []
            for account_id, user_videos in unique_accounts.items():
                try:
                    # 获取用户信息
                    user_response = await tikhub_client.get_user_info(account_id)
                    if user_response.status_code != 0 or not user_response.data:
                        continue
                    
                    user_data = user_response.data
                    
                    # 转换为分析结果
                    analysis = self.convert_tikhub_user_to_analysis(
                        user_data.user, 
                        user_data.stats, 
                        user_videos
                    )
                    analyses.append(analysis)
                    
                except Exception as e:
                    logger.warning(f"获取账号 {account_id} 分析失败: {e}")
                    continue
            
            # 按热度分数排序
            analyses.sort(key=lambda x: x.heat_score, reverse=True)
            
            # 设置排名
            for i, analysis in enumerate(analyses):
                analysis.heat_ranking = i + 1
            
            return analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取对标账号热度榜单失败: {e}")
            raise
    
    async def get_account_heat_ranking_by_type(self, account_type: str, 
                                             limit: int = 20) -> List[CompetitorAccountAnalysis]:
        """
        获取指定账号类型的热度榜单
        
        Args:
            account_type: 账号类型
            limit: 返回数量限制
            
        Returns:
            指定类型账号热度榜单
        """
        logger.info(f"获取指定类型账号热度榜单: {account_type}, limit={limit}")
        
        try:
            # 获取全部账号榜单
            all_analyses = await self.get_account_heat_ranking(limit * 2)
            
            # 筛选指定类型的账号
            filtered_analyses = []
            for analysis in all_analyses:
                if account_type == "verified" and analysis.account_type == AccountType.VERIFIED:
                    filtered_analyses.append(analysis)
                elif account_type == "enterprise" and analysis.account_type == AccountType.ENTERPRISE:
                    filtered_analyses.append(analysis)
                elif account_type == "normal" and analysis.account_type == AccountType.NORMAL:
                    filtered_analyses.append(analysis)
            
            # 重新设置排名
            for i, analysis in enumerate(filtered_analyses):
                analysis.heat_ranking = i + 1
            
            return filtered_analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取指定类型账号热度榜单失败: {e}")
            raise
    
    async def get_accounts_by_follower_range(self, min_followers: int, max_followers: int, 
                                           limit: int = 20) -> List[CompetitorAccountAnalysis]:
        """
        获取指定粉丝数量范围的账号
        
        Args:
            min_followers: 最小粉丝数
            max_followers: 最大粉丝数
            limit: 返回数量限制
            
        Returns:
            指定粉丝范围的账号列表
        """
        logger.info(f"获取指定粉丝范围账号: {min_followers}-{max_followers}, limit={limit}")
        
        try:
            # 获取全部账号榜单
            all_analyses = await self.get_account_heat_ranking(limit * 3)
            
            # 筛选指定粉丝范围的账号
            filtered_analyses = []
            for analysis in all_analyses:
                follower_count = analysis.follower_count
                if min_followers <= follower_count <= max_followers:
                    filtered_analyses.append(analysis)
            
            # 按热度分数排序
            filtered_analyses.sort(key=lambda x: x.heat_score, reverse=True)
            
            # 重新设置排名
            for i, analysis in enumerate(filtered_analyses):
                analysis.heat_ranking = i + 1
            
            return filtered_analyses[:limit]
            
        except Exception as e:
            logger.error(f"获取指定粉丝范围账号失败: {e}")
            raise
    
    async def get_verified_account_ranking(self, limit: int = 20) -> List[CompetitorAccountAnalysis]:
        """
        获取认证账号榜单
        
        Args:
            limit: 返回数量限制
            
        Returns:
            认证账号榜单
        """
        logger.info(f"获取认证账号榜单: limit={limit}")
        
        try:
            return await self.get_account_heat_ranking_by_type("verified", limit)
            
        except Exception as e:
            logger.error(f"获取认证账号榜单失败: {e}")
            raise
    
    async def sync_account_data(self, account_id: str) -> CompetitorAccountAnalysis:
        """
        同步账号数据
        
        Args:
            account_id: 账号ID
            
        Returns:
            同步后的账号分析结果
        """
        logger.info(f"同步账号数据: {account_id}")
        
        try:
            # 获取最新账号数据
            analysis = await self.get_account_heat_info(account_id)
            
            # 这里应该保存到数据库
            # 暂时直接返回分析结果
            
            return analysis
            
        except Exception as e:
            logger.error(f"同步账号数据失败: {account_id}, 错误: {e}")
            raise


# 创建全局服务实例
competitor_account_service = CompetitorAccountService() 