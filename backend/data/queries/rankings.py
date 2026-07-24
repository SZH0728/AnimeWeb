# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file rankings.py
@brief 执行最高评分与最多人评价榜查询，并映射为内部行模型。
"""

from sqlalchemy.engine import RowMapping

from sqlalchemy import Select, bindparam, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import SUBJECTS, build_subject_list_columns, latest_rating_lateral, to_subject_list_row
from backend.data.rows import RankingRow


async def count_top_score_rankings(session: AsyncSession, min_total: int) -> int:
    """
    @brief 统计最高评分榜筛选后的条目数量。
    @param session 当前请求的只读数据库会话。
    @param min_total 最新评分人数下限。
    @return 进入最高评分榜的条目总数。
    """
    result = await session.execute(_build_top_score_ranking_count_statement(), {'min_total': min_total})
    return result.scalar_one()


async def list_top_score_rankings(session: AsyncSession, min_total: int, limit: int, offset: int) -> tuple[RankingRow, ...]:
    """
    @brief 分页读取最高评分榜。
    @param session 当前请求的只读数据库会话。
    @param min_total 最新评分人数下限。
    @param limit 本次读取的最大榜单项数。
    @param offset 要跳过的榜单项数。
    @return 含完整筛选结果连续名次的不可变榜单行模型。
    """
    result = await session.execute(
        _build_top_score_ranking_statement(),
        {'min_total': min_total, 'limit': limit, 'offset': offset},
    )
    return tuple(_to_ranking_row(record) for record in result.mappings())


async def count_most_rated_rankings(session: AsyncSession) -> int:
    """
    @brief 统计最多人评价榜的条目数量。
    @param session 当前请求的只读数据库会话。
    @return 进入最多人评价榜的条目总数。
    """
    result = await session.execute(_build_most_rated_ranking_count_statement())
    return result.scalar_one()


async def list_most_rated_rankings(session: AsyncSession, limit: int, offset: int) -> tuple[RankingRow, ...]:
    """
    @brief 分页读取最多人评价榜。
    @param session 当前请求的只读数据库会话。
    @param limit 本次读取的最大榜单项数。
    @param offset 要跳过的榜单项数。
    @return 含完整筛选结果连续名次的不可变榜单行模型。
    """
    result = await session.execute(
        _build_most_rated_ranking_statement(),
        {'limit': limit, 'offset': offset},
    )
    return tuple(_to_ranking_row(record) for record in result.mappings())


def _build_top_score_ranking_statement() -> Select[tuple[object, ...]]:
    latest_rating = latest_rating_lateral()
    order_by = (
        latest_rating.c.score.desc(),
        latest_rating.c.total.desc(),
        SUBJECTS.c.bgm_id.asc(),
    )

    return (
        select(
            func.row_number().over(order_by=order_by).label('position'),
            latest_rating.c.score.label('metric_value'),
            *build_subject_list_columns(SUBJECTS, latest_rating),
        )
        .select_from(SUBJECTS.join(latest_rating, true()))
        .where(
            latest_rating.c.score.is_not(None),
            latest_rating.c.total >= bindparam('min_total'),
        )
        .order_by(*order_by)
        .limit(bindparam('limit'))
        .offset(bindparam('offset'))
    )


def _build_most_rated_ranking_statement() -> Select[tuple[object, ...]]:
    latest_rating = latest_rating_lateral()
    order_by = (
        latest_rating.c.total.desc(),
        latest_rating.c.score.desc().nulls_last(),
        SUBJECTS.c.bgm_id.asc(),
    )

    return (
        select(
            func.row_number().over(order_by=order_by).label('position'),
            latest_rating.c.total.label('metric_value'),
            *build_subject_list_columns(SUBJECTS, latest_rating),
        )
        .select_from(SUBJECTS.join(latest_rating, true()))
        .where(latest_rating.c.total > 0)
        .order_by(*order_by)
        .limit(bindparam('limit'))
        .offset(bindparam('offset'))
    )


def _build_top_score_ranking_count_statement() -> Select[tuple[int]]:
    latest_rating = latest_rating_lateral()

    return (
        select(func.count(SUBJECTS.c.bgm_id))
        .select_from(SUBJECTS.join(latest_rating, true()))
        .where(
            latest_rating.c.score.is_not(None),
            latest_rating.c.total >= bindparam('min_total'),
        )
    )


def _build_most_rated_ranking_count_statement() -> Select[tuple[int]]:
    latest_rating = latest_rating_lateral()

    return (
        select(func.count(SUBJECTS.c.bgm_id))
        .select_from(SUBJECTS.join(latest_rating, true()))
        .where(latest_rating.c.total > 0)
    )


def _to_ranking_row(record: RowMapping) -> RankingRow:
    metric_value = record['metric_value']
    position = record['position']

    return RankingRow(
        position=position,
        metric_value=metric_value,
        subject=to_subject_list_row(record),
    )

if __name__ == '__main__':
    pass
