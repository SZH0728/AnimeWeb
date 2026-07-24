# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file seasons.py
@brief 执行季度汇总与最新季度读取所需的 SQLAlchemy Core 查询。
"""

from sqlalchemy import Select, case, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import SUBJECTS, latest_rating_lateral, to_season_summary_row
from backend.data.rows import SeasonSummaryRow


async def list_seasons(session: AsyncSession) -> tuple[SeasonSummaryRow, ...]:
    """
    @brief 读取全部已收录季度的汇总信息。
    @param session 当前请求的只读数据库会话。
    @return 按最新年季优先排序的不可变季度汇总行模型。
    """
    result = await session.execute(_build_list_seasons_statement())
    return tuple(to_season_summary_row(record) for record in result.mappings())


def _build_list_seasons_statement() -> Select[tuple[object, ...]]:
    """
    @brief 构造已收录季度的汇总查询。
    @details 仅统计年季均存在的 subjects；评分条目数由共享最新快照是否存在判定。
    @return 按最新年季优先排序的 SQLAlchemy Core 查询。
    """
    latest_rating = latest_rating_lateral()
    season_order = case(
        (SUBJECTS.c.season == 'winter', 1),
        (SUBJECTS.c.season == 'spring', 2),
        (SUBJECTS.c.season == 'summer', 3),
        (SUBJECTS.c.season == 'fall', 4),
        else_=0,
    )
    return (
        select(
            SUBJECTS.c.year.label('year'),
            SUBJECTS.c.season.label('season'),
            func.count(SUBJECTS.c.bgm_id).label('subject_count'),
            func.count(latest_rating.c.date).label('rated_subject_count'),
        )
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(SUBJECTS.c.year.is_not(None), SUBJECTS.c.season.is_not(None))
        .group_by(SUBJECTS.c.year, SUBJECTS.c.season)
        .order_by(SUBJECTS.c.year.desc(), season_order.desc())
    )

if __name__ == '__main__':
    pass
