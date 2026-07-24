# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file search.py
@brief 执行基于 PostgreSQL pg_trgm 的条目搜索，并映射为内部行模型。
@details 搜索只读取名称、译名和别名；别名相似度使用聚合子查询，避免展开数组后
         产生重复的 subject 行。
"""

from sqlalchemy.engine import RowMapping

from sqlalchemy import ColumnElement, Select, Text, bindparam, case, func, select, true
from sqlalchemy.dialects.postgresql import array
from sqlalchemy.ext.asyncio import AsyncSession

from backend.data.queries.common import SUBJECTS, build_subject_list_columns, latest_rating_lateral, to_subject_list_row
from backend.data.rows import SearchRow


async def count_search_results(session: AsyncSession, query: str) -> int:
    """
    @brief 统计指定搜索词的命中条目数量。
    @param session 当前请求的只读数据库会话。
    @param query 已由服务层规范化的非空搜索词。
    @return 满足相关性阈值的条目总数。
    """
    result = await session.execute(_build_search_count_statement(), {'query': query})
    count = result.scalar_one()
    return count


async def search_subjects(session: AsyncSession, query: str, limit: int, offset: int) -> tuple[SearchRow, ...]:
    """
    @brief 分页搜索条目并返回命中字段。
    @param session 当前请求的只读数据库会话。
    @param query 已由服务层规范化的非空搜索词。
    @param limit 本次读取的最大结果数。
    @param offset 要跳过的结果数。
    @return 按相关性和稳定次级规则排序的不可变搜索行模型。
    """
    result = await session.execute(
        _build_search_statement(),
        {'query': query, 'limit': limit, 'offset': offset},
    )

    return tuple(_to_search_row(record) for record in result.mappings())


def _build_search_statement() -> Select[tuple[object, ...]]:
    query: ColumnElement[str] = bindparam('query', type_=Text())
    latest_rating = latest_rating_lateral()

    alias_values = (
        func.unnest(SUBJECTS.c.aliases)
        .table_valued('alias')
        .render_derived()
        .alias('alias_values')
    )

    alias_similarity = (
        select(func.max(func.similarity(alias_values.c.alias, query)))
        .select_from(alias_values)
        .scalar_subquery()
    )

    name_similarity = func.similarity(SUBJECTS.c.name, query)
    translation_similarity = func.similarity(SUBJECTS.c.translation, query)
    weighted_alias_similarity = func.coalesce(alias_similarity, 0) * 0.8

    relevance = func.greatest(name_similarity, translation_similarity, weighted_alias_similarity)
    name_or_translation_match = func.greatest(name_similarity, translation_similarity) >= 0.3

    matched_fields = func.array_remove(
        array(
            [
                case((name_similarity >= 0.3, 'name')),
                case((translation_similarity >= 0.3, 'translation')),
                case((weighted_alias_similarity >= 0.3, 'aliases')),
            ]
        ),
        None,
    ).label('matched_fields')

    return (
        select(
            *build_subject_list_columns(SUBJECTS, latest_rating),
            matched_fields,
        )
        .select_from(SUBJECTS.outerjoin(latest_rating, true()))
        .where(relevance >= 0.3)
        .order_by(
            relevance.desc(),
            name_or_translation_match.desc(),
            latest_rating.c.score.desc().nulls_last(),
            latest_rating.c.total.desc(),
            SUBJECTS.c.bgm_id.asc(),
        )
        .limit(bindparam('limit'))
        .offset(bindparam('offset'))
    )


def _build_search_count_statement() -> Select[tuple[int]]:
    query: ColumnElement[str] = bindparam('query', type_=Text())

    alias_values = (
        func.unnest(SUBJECTS.c.aliases)
        .table_valued('alias')
        .render_derived()
        .alias('alias_values')
    )

    alias_similarity = (
        select(func.max(func.similarity(alias_values.c.alias, query)))
        .select_from(alias_values)
        .scalar_subquery()
    )

    relevance = func.greatest(
        func.similarity(SUBJECTS.c.name, query),
        func.similarity(SUBJECTS.c.translation, query),
        func.coalesce(alias_similarity, 0) * 0.8,
    )

    return select(func.count(SUBJECTS.c.bgm_id)).where(relevance >= 0.3)


def _to_search_row(record: RowMapping) -> SearchRow:
    matched_fields = record['matched_fields']
    if not isinstance(matched_fields, (list, tuple)) or not all(
        isinstance(field_name, str) for field_name in matched_fields
    ):
        raise TypeError('搜索命中字段必须是字符串数组')

    return SearchRow(
        subject=to_subject_list_row(record),
        matched_fields=tuple(matched_fields),
    )

if __name__ == '__main__':
    pass
