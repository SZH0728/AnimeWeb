# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file rankings.py
@brief 实现最高评分与最多人评价榜的业务编排。
@details 本服务集中维护榜单行模型到公开 DTO 的映射、完整结果名次和首页复用的
         查询入口；仅缓存两个榜单的第一页。
"""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import config
from backend.api.pagination import calculate_offset, create_pagination
from backend.api.schemas import MostRatedRankingMeta, MostRatedRankingResponse, RankingItem, TopScoreRankingMeta, TopScoreRankingResponse
from backend.data.queries.rankings import count_most_rated_rankings, count_top_score_rankings, list_most_rated_rankings, list_top_score_rankings
from backend.data.rows import RankingRow
from backend.core.cache import InMemoryTtlCache
from backend.services.subjects import SubjectService


class RankingService(object):
    """@brief 提供高分与最多人评价榜的读取能力。"""

    def __init__(self, cache: InMemoryTtlCache, subjects: SubjectService) -> None:
        """
        @brief 创建带可选第一页缓存的榜单服务。
        @param cache 应用生命周期持有的进程内缓存。
        @param subjects 提供统一条目 DTO 与封面 URL 映射的条目服务。
        """
        self._cache = cache
        self._subjects = subjects

        self._cache_ttl_seconds = config.getint('cache', 'rankings_ttl_seconds')

    async def list_top_score_rankings(self, session: AsyncSession, min_total: int, page: int, page_size: int, use_cache: bool = True) -> TopScoreRankingResponse:
        """
        @brief 分页获取按最新评分排序的高分榜。
        @param session 当前请求的只读数据库会话。
        @param min_total 最新评分人数下限。
        @param page 从 1 开始的目标页码。
        @param page_size 单页最大返回条目数。
        @param use_cache 是否读取或写入榜单第一页缓存。
        @return 含完整筛选结果连续名次的高分榜分页响应。
        """
        if not use_cache or page != 1:
            return await self._load_top_score_rankings(session, min_total, page, page_size)

        return await self._cache.get_or_load(
            key=f'rankings:top_score:min_total={min_total}:page_size={page_size}',
            ttl_seconds=self._cache_ttl_seconds,
            loader=lambda: self._load_top_score_rankings(session, min_total, page, page_size),
        )

    async def list_most_rated_rankings(self, session: AsyncSession, page: int, page_size: int, use_cache: bool = True) -> MostRatedRankingResponse:
        """
        @brief 分页获取按最新评分人数排序的榜单。
        @param session 当前请求的只读数据库会话。
        @param page 从 1 开始的目标页码。
        @param page_size 单页最大返回条目数。
        @param use_cache 是否读取或写入榜单第一页缓存。
        @return 含完整筛选结果连续名次的最多人评价榜分页响应。
        """
        if not use_cache or page != 1:
            return await self._load_most_rated_rankings(session, page, page_size)

        return await self._cache.get_or_load(
            key=f'rankings:most_rated:page_size={page_size}',
            ttl_seconds=self._cache_ttl_seconds,
            loader=lambda: self._load_most_rated_rankings(session, page, page_size),
        )

    async def _load_top_score_rankings(self, session: AsyncSession, min_total: int, page: int, page_size: int) -> TopScoreRankingResponse:
        """@brief 直接读取数据库并组装高分榜分页响应。"""
        offset = calculate_offset(page=page, page_size=page_size)
        total = await count_top_score_rankings(session=session, min_total=min_total)
        rows = await list_top_score_rankings(session=session, min_total=min_total, limit=page_size, offset=offset)

        return TopScoreRankingResponse(
            items=[self._to_ranking_item(row) for row in rows],
            pagination=create_pagination(page=page, page_size=page_size, total=total),
            meta=TopScoreRankingMeta(
                ranking_type='top_score',
                min_total=min_total,
                snapshot_basis='per_subject_latest',
            ),
        )

    async def _load_most_rated_rankings(self, session: AsyncSession, page: int, page_size: int) -> MostRatedRankingResponse:
        """@brief 直接读取数据库并组装最多人评价榜分页响应。"""
        offset = calculate_offset(page=page, page_size=page_size)
        total = await count_most_rated_rankings(session=session)
        rows = await list_most_rated_rankings(session=session, limit=page_size, offset=offset)

        return MostRatedRankingResponse(
            items=[self._to_ranking_item(row) for row in rows],
            pagination=create_pagination(page=page, page_size=page_size, total=total),
            meta=MostRatedRankingMeta(
                ranking_type='most_rated',
                snapshot_basis='per_subject_latest',
            ),
        )

    def _to_ranking_item(self, row: RankingRow) -> RankingItem:
        """
        @brief 将榜单行模型转换为公开榜单项。
        @param row 数据访问层返回的带完整名次榜单行模型。
        @return 包含统一条目摘要的公开榜单项。
        """
        return RankingItem(
            position=row.position,
            metric_value=self._to_metric_value(row.metric_value),
            subject=self._subjects.to_subject_list_item(row.subject),
        )

    @staticmethod
    def _to_metric_value(value: Decimal | int) -> float | int:
        """
        @brief 将数据库数值指标转换为 JSON 可序列化数值。
        @param value 高分榜评分或最多人评价榜评分人数。
        @return 评分对应浮点数或评分人数对应整数。
        """
        if isinstance(value, Decimal):
            return float(value)

        return value




if __name__ == '__main__':
    pass

