# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file subjects.py
@brief 执行季度条目、详情、存在性与评分历史查询，并映射为内部行模型。
"""

from sqlalchemy import ColumnElement, Integer, Select, bindparam, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import RATINGS, SUBJECTS, build_subject_detail_columns, build_subject_list_columns, latest_rating_lateral, to_rating_history_row, to_subject_detail_row, to_subject_list_row
from backend.data.rows import RatingHistoryRow, SubjectDetailRow, SubjectListPageRow


async def list_subject_page(session: AsyncSession, year: int, season: str, min_total: int, limit: int, offset: int) -> SubjectListPageRow:
    """
    @brief 分页读取指定季度的条目及完整筛选结果总数。
    @param session 当前请求的只读数据库会话。
    @param year 目标播出年份。
    @param season 目标播出季度。
    @param min_total 最新评分人数下限，0 表示不筛选。
    @param limit 本次读取的最大条目数。
    @param offset 要跳过的条目数。
    @return 同时包含总数和按稳定最新评分排序条目的分页行模型。
    """
    result = await session.execute(
        _build_subject_list_page_statement(),
        {
            'year': year,
            'season': season,
            'min_total': min_total,
            'limit': limit,
            'offset': offset,
        },
    )

    records = tuple(result.mappings())
    total = records[0]['total']
    items = tuple(to_subject_list_row(record) for record in records if record['bgm_id'] is not None)

    return SubjectListPageRow(total=total, items=items)


async def get_subject_detail(session: AsyncSession, bgm_id: int) -> SubjectDetailRow | None:
    """
    @brief 读取单个条目的完整公开详情。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 条目存在时返回详情行模型，不存在时返回 None。
    """
    result = await session.execute(_build_subject_detail_statement(), {'bgm_id': bgm_id})
    record = result.mappings().one_or_none()

    if record is None:
        return None

    return to_subject_detail_row(record)


async def subject_exists(session: AsyncSession, bgm_id: int) -> bool:
    """
    @brief 判断指定公开条目 ID 是否存在。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 条目存在时为 True，否则为 False。
    """
    result = await session.execute(_build_subject_exists_statement(), {'bgm_id': bgm_id})
    return result.scalar_one_or_none() is not None


async def list_rating_history(session: AsyncSession, bgm_id: int) -> tuple[RatingHistoryRow, ...]:
    """
    @brief 读取单条目的评分历史快照。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 按快照日期正序排列的不可变评分历史行模型；超过 30 条时按间隔采样且保留最新快照。
    """
    result = await session.execute(_build_rating_history_statement(), {'bgm_id': bgm_id})
    return tuple(to_rating_history_row(record) for record in result.mappings())


def _build_subject_list_page_statement() -> Select[tuple[object, ...]]:
    latest_rating = latest_rating_lateral()
    min_total: ColumnElement[int] = bindparam('min_total', type_=Integer())

    filtered_subjects = (
        select(*build_subject_list_columns(SUBJECTS, latest_rating))
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(
            SUBJECTS.c.year == bindparam('year'),
            SUBJECTS.c.season == bindparam('season'),
            (min_total == 0) | (latest_rating.c.total >= min_total),
        )
        .cte('filtered_subjects')
        .prefix_with('MATERIALIZED')
    )

    total = select(func.count().label('total')).select_from(filtered_subjects).cte('total')

    page = (
        select(filtered_subjects)
        .order_by(
            filtered_subjects.c.latest_rating_score.desc().nulls_last(),
            filtered_subjects.c.latest_rating_total.desc(),
            filtered_subjects.c.bgm_id.asc(),
        )
        .limit(bindparam('limit'))
        .offset(bindparam('offset'))
        .cte('page')
    )

    return (
        select(total.c.total, page)
        .select_from(total.outerjoin(page, true()))
        .order_by(
            page.c.latest_rating_score.desc().nulls_last(),
            page.c.latest_rating_total.desc(),
            page.c.bgm_id.asc(),
        )
    )


def _build_subject_detail_statement() -> Select[tuple[object, ...]]:
    latest_rating = latest_rating_lateral()
    return (
        select(*build_subject_detail_columns(SUBJECTS, latest_rating))
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(SUBJECTS.c.bgm_id == bindparam('bgm_id'))
    )


def _build_subject_exists_statement() -> Select[tuple[int]]:
    return select(SUBJECTS.c.bgm_id).where(SUBJECTS.c.bgm_id == bindparam('bgm_id'))


def _build_rating_history_statement() -> Select[tuple[object, ...]]:
    annotated_history = (
        select(
            RATINGS.c.date.label('date'),
            RATINGS.c.score.label('score'),
            RATINGS.c.total.label('total'),
            RATINGS.c.rank.label('rank'),
            func.row_number().over(order_by=RATINGS.c.date.asc()).label('row_number'),
            func.count().over().label('total_rows'),
        )
        .where(RATINGS.c.bgm_id == bindparam('bgm_id'))
        .cte('annotated_history')
    )
    sampling_stride = (annotated_history.c.total_rows + 29) // 30

    return (
        select(
            annotated_history.c.date,
            annotated_history.c.score,
            annotated_history.c.total,
            annotated_history.c.rank,
        )
        .where(
            (annotated_history.c.total_rows <= 30)
            | ((annotated_history.c.total_rows - annotated_history.c.row_number) % sampling_stride == 0)
        )
        .order_by(annotated_history.c.date.asc())
    )

if __name__ == '__main__':
    pass
