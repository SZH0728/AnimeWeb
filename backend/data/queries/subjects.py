# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file subjects.py
@brief 执行季度条目、详情、存在性与评分历史查询，并映射为内部行模型。
"""

from sqlalchemy import ColumnElement, Integer, Select, bindparam, func, select, true
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import RATINGS, SUBJECTS, build_subject_detail_columns, build_subject_list_columns, latest_rating_lateral, stable_latest_rating_order, to_rating_history_row, to_subject_detail_row, to_subject_list_row
from backend.data.rows import RatingHistoryRow, SubjectDetailRow, SubjectListRow


async def count_subjects(session: AsyncSession, year: int, season: str, min_total: int) -> int:
    """
    @brief 统计指定季度和评分人数筛选后的条目数量。
    @param session 当前请求的只读数据库会话。
    @param year 目标播出年份。
    @param season 目标播出季度。
    @param min_total 最新评分人数下限，0 表示不筛选。
    @return 满足筛选条件的条目总数。
    """
    result = await session.execute(
        _build_count_subjects_statement(),
        {'year': year, 'season': season, 'min_total': min_total},
    )
    count = result.scalar_one()
    return count


async def list_subjects(session: AsyncSession, year: int, season: str, min_total: int, limit: int, offset: int) -> tuple[SubjectListRow, ...]:
    """
    @brief 分页读取指定季度的条目列表。
    @param session 当前请求的只读数据库会话。
    @param year 目标播出年份。
    @param season 目标播出季度。
    @param min_total 最新评分人数下限，0 表示不筛选。
    @param limit 本次读取的最大条目数。
    @param offset 要跳过的条目数。
    @return 按稳定最新评分排序的不可变条目列表行模型。
    """
    result = await session.execute(
        _build_list_subjects_statement(),
        {
            'year': year,
            'season': season,
            'min_total': min_total,
            'limit': limit,
            'offset': offset,
        },
    )
    return tuple(to_subject_list_row(record) for record in result.mappings())


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
    @brief 读取单条目的全部评分历史。
    @param session 当前请求的只读数据库会话。
    @param bgm_id Bangumi 公开条目 ID。
    @return 按快照日期正序排列的不可变评分历史行模型。
    """
    result = await session.execute(_build_rating_history_statement(), {'bgm_id': bgm_id})
    return tuple(to_rating_history_row(record) for record in result.mappings())


def _build_count_subjects_statement() -> Select[tuple[int]]:
    latest_rating = latest_rating_lateral()
    min_total: ColumnElement[int] = bindparam('min_total', type_=Integer())

    return (
        select(func.count(SUBJECTS.c.bgm_id))
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(
            SUBJECTS.c.year == bindparam('year'),
            SUBJECTS.c.season == bindparam('season'),
            (min_total == 0) | (latest_rating.c.total >= min_total),
        )
    )


def _build_list_subjects_statement() -> Select[tuple[object, ...]]:
    latest_rating = latest_rating_lateral()
    min_total: ColumnElement[int] = bindparam('min_total', type_=Integer())

    return (
        select(*build_subject_list_columns(SUBJECTS, latest_rating))
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(
            SUBJECTS.c.year == bindparam('year'),
            SUBJECTS.c.season == bindparam('season'),
            (min_total == 0) | (latest_rating.c.total >= min_total),
        )
        .order_by(*stable_latest_rating_order(latest_rating))
        .limit(bindparam('limit'))
        .offset(bindparam('offset'))
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
    return (
        select(
            RATINGS.c.date.label('date'),
            RATINGS.c.score.label('score'),
            RATINGS.c.total.label('total'),
            RATINGS.c.rank.label('rank'),
        )
        .where(RATINGS.c.bgm_id == bindparam('bgm_id'))
        .order_by(RATINGS.c.date.asc())
    )

if __name__ == '__main__':
    pass
