# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file seasons.py
@brief 实现季度选择接口的业务编排。
@details 季度服务负责将季度查询行模型转换为公开 DTO；缓存实例由应用生命周期
         创建并注入，服务自身不持有模块级可变状态。
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import config
from backend.api.schemas import SeasonListResponse, SeasonSummary
from backend.core.cache import InMemoryTtlCache
from backend.data.queries.seasons import list_seasons as query_list_seasons


class SeasonService(object):
    """@brief 提供已收录季度的读取能力。"""

    def __init__(self, cache: InMemoryTtlCache) -> None:
        """
        @brief 创建带可选缓存的季度服务。
        @param cache 应用生命周期持有的进程内缓存。
        """
        self._cache = cache

        self._cache_ttl_seconds = config.getint('cache', 'seasons_ttl_seconds')

    async def list_seasons(self, session: AsyncSession, use_cache: bool = True) -> SeasonListResponse:
        """
        @brief 获取按最新季度优先排序的全部季度汇总。
        @param session 当前请求的只读数据库会话。
        @param use_cache 是否读取或写入季度选择缓存。
        @return 包含季度汇总数组的公开响应。
        """
        if not use_cache:
            return await self._load_seasons(session)

        return await self._cache.get_or_load(
            key='seasons',
            ttl_seconds=self._cache_ttl_seconds,
            loader=lambda: self._load_seasons(session),
        )

    @staticmethod
    async def _load_seasons(session: AsyncSession) -> SeasonListResponse:
        """@brief 直接读取数据库并转换全部季度汇总。"""
        rows = await query_list_seasons(session)
        return SeasonListResponse(
            items=[
                SeasonSummary(
                    year=row.year,
                    season=row.season,
                    subject_count=row.subject_count,
                    rated_subject_count=row.rated_subject_count,
                )
                for row in rows
            ],
        )


if __name__ == '__main__':
    pass
