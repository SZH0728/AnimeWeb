# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file home.py
@brief 实现首页季度与榜单预览的业务聚合。
@details 首页只复用季度、季度条目和榜单服务的既有口径，不复制独立排序 SQL。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.schemas import HomeResponse, LatestSeasonPreview, SubjectPreview
from backend.core.cache import InMemoryTtlCache
from backend.core.config import config
from backend.services.rankings import RankingService
from backend.services.seasons import SeasonService
from backend.services.subjects import SubjectService


class HomeService(object):
    """@brief 提供首页聚合读取能力。"""

    def __init__(self, cache: InMemoryTtlCache, rankings: RankingService, seasons: SeasonService, subjects: SubjectService) -> None:
        """
        @brief 创建带可选缓存的首页服务。
        @param cache 应用生命周期持有的进程内缓存。
        @param rankings 提供与完整榜单一致的预览数据。
        @param seasons 提供最新已收录季度判定。
        @param subjects 提供最新季度条目预览。
        """
        self._cache = cache
        self._rankings = rankings
        self._seasons = seasons
        self._subjects = subjects

        self._cache_ttl_seconds = config.getint('cache', 'home_ttl_seconds')
        self._latest_season_limit = config.getint('home', 'latest_season_limit')
        self._ranking_preview_limit = config.getint('home', 'ranking_preview_limit')

    async def get_home(self, session: AsyncSession) -> HomeResponse:
        """
        @brief 获取最新季度及两个榜单的固定数量预览。
        @param session 当前请求的只读数据库会话。
        @return 包含可选最新季度和两个独立榜单预览的首页响应。
        """
        return await self._cache.get_or_load(
            key='home',
            ttl_seconds=self._cache_ttl_seconds,
            loader=lambda: self._load_home(session),
        )

    async def _load_home(self, session: AsyncSession) -> HomeResponse:
        """@brief 复用既有服务口径直接组装首页响应。"""
        seasons = await self._seasons.list_seasons(session, use_cache=False)
        top_score = await self._rankings.list_top_score_rankings(
            session=session,
            min_total=0,
            page=1,
            page_size=self._ranking_preview_limit,
            use_cache=False,
        )
        most_rated = await self._rankings.list_most_rated_rankings(
            session=session,
            page=1,
            page_size=self._ranking_preview_limit,
            use_cache=False,
        )
        latest_season = None

        if seasons.items:
            season = seasons.items[0]
            subjects = await self._subjects.list_subjects(
                session=session,
                year=season.year,
                season=season.season,
                min_total=0,
                page=1,
                page_size=self._latest_season_limit,
            )
            latest_season = LatestSeasonPreview(
                year=season.year,
                season=season.season,
                subject_count=season.subject_count,
                rated_subject_count=season.rated_subject_count,
                items=subjects.items,
            )

        return HomeResponse(
            latest_season=latest_season,
            top_score=SubjectPreview(items=[item.subject for item in top_score.items]),
            most_rated=SubjectPreview(items=[item.subject for item in most_rated.items]),
        )


if __name__ == '__main__':
    pass
