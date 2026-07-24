# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file common.py
@brief 定义所有公开查询共享的 Core 表结构、投影、行映射和最新评分表达式。
@details 所有条目查询以 subjects 为驱动表，并复用 latest_rating_lateral()，
         从而保证孤儿评分不可见且评分字段来自同一条最新快照。
"""

from collections.abc import Sequence

from sqlalchemy.engine import RowMapping
from sqlalchemy import Column, Date, Integer, MetaData, Numeric, Table, Text, func, literal_column
from sqlalchemy.dialects.postgresql import ARRAY, ENUM
from sqlalchemy.sql.elements import ColumnElement
from sqlalchemy.sql.selectable import FromClause, LateralFromClause

from backend.data.rows import LatestRatingRow, RatingHistoryRow, SeasonSummaryRow, SubjectDetailRow, SubjectListRow

METADATA = MetaData()

SEASON_TYPE = ENUM(
    'winter',
    'spring',
    'summer',
    'fall',
    name='season_type',
    create_type=False,
)

SUBJECTS = Table(
    'subjects',
    METADATA,
    Column('id', Integer),
    Column('bgm_id', Integer),
    Column('url', Text),
    Column('name', Text),
    Column('translation', Text),
    Column('air_date', Date),
    Column('year', Integer),
    Column('season', SEASON_TYPE),
    Column('summary', Text),
    Column('aliases', ARRAY(Text)),
    Column('tags', ARRAY(Text)),
    Column('infobox'),
    Column('cover_url', Text),
    Column('cover_image'),
)

RATINGS = Table(
    'ratings',
    METADATA,
    Column('id', Integer),
    Column('bgm_id', Integer),
    Column('date', Date),
    Column('score', Numeric),
    Column('total', Integer),
    Column('rank', Integer),
)


def latest_rating_lateral(subjects: FromClause = SUBJECTS) -> LateralFromClause:
    """
    @brief 构造按条目获取单行最新评分的 lateral 子查询。
    @details 查询以 subjects.bgm_id 关联 ratings，并按采集日期倒序取一行。
             所有需要最新评分的公开查询必须复用此表达式。
    @param subjects 作为查询驱动表的 subjects 表或别名。
    @return 带有 date、score、total 与 rank 字段的 lateral 查询。
    """
    rating_rows = RATINGS.alias('latest_rating_source')
    return (
        rating_rows.select()
        .with_only_columns(
            rating_rows.c.date,
            rating_rows.c.score,
            rating_rows.c.total,
            rating_rows.c.rank,
        )
        .where(rating_rows.c.bgm_id == subjects.c.bgm_id)
        .order_by(rating_rows.c.date.desc())
        .limit(1)
        .lateral('latest_rating')
    )


def build_subject_list_columns(subjects: FromClause, latest_rating: LateralFromClause) -> Sequence[ColumnElement[object]]:
    """
    @brief 构造条目列表公开字段的 SQL 投影。
    @details 空字符串统一投影为 NULL，标签缺失时投影为空数组；不读取内部主键、
             infobox、cover_image 或评分分布字段。
    @param subjects 当前查询使用的 subjects 表或别名。
    @param latest_rating 已关联的最新评分 lateral 子查询。
    @return 可直接传入 select() 的稳定字段序列。
    """
    return (
        subjects.c.bgm_id.label('bgm_id'),
        subjects.c.name.label('name'),
        func.nullif(subjects.c.translation, '').label('translation'),
        subjects.c.air_date.label('air_date'),
        subjects.c.year.label('year'),
        subjects.c.season.label('season'),
        func.coalesce(subjects.c.tags, _empty_text_array()).label('tags'),
        func.nullif(subjects.c.cover_url, '').label('cover_url'),
        latest_rating.c.date.label('latest_rating_date'),
        latest_rating.c.score.label('latest_rating_score'),
        latest_rating.c.total.label('latest_rating_total'),
        latest_rating.c.rank.label('latest_rating_rank'),
    )


def build_subject_detail_columns(subjects: FromClause, latest_rating: LateralFromClause) -> Sequence[ColumnElement[object]]:
    """
    @brief 构造条目详情公开字段的 SQL 投影。
    @details 在列表投影基础上补充 URL、别名与简介，仍不读取内部字段和图片二进制。
    @param subjects 当前查询使用的 subjects 表或别名。
    @param latest_rating 已关联的最新评分 lateral 子查询。
    @return 可直接传入 select() 的稳定字段序列。
    """
    return (
        subjects.c.bgm_id.label('bgm_id'),
        subjects.c.url.label('url'),
        subjects.c.name.label('name'),
        func.nullif(subjects.c.translation, '').label('translation'),
        func.coalesce(subjects.c.aliases, _empty_text_array()).label('aliases'),
        func.nullif(subjects.c.summary, '').label('summary'),
        subjects.c.air_date.label('air_date'),
        subjects.c.year.label('year'),
        subjects.c.season.label('season'),
        func.coalesce(subjects.c.tags, _empty_text_array()).label('tags'),
        func.nullif(subjects.c.cover_url, '').label('cover_url'),
        latest_rating.c.date.label('latest_rating_date'),
        latest_rating.c.score.label('latest_rating_score'),
        latest_rating.c.total.label('latest_rating_total'),
        latest_rating.c.rank.label('latest_rating_rank'),
    )


def stable_latest_rating_order(latest_rating: LateralFromClause) -> Sequence[ColumnElement[object]]:
    """
    @brief 构造条目列表使用的稳定最新评分排序。
    @param latest_rating 已关联的最新评分 lateral 子查询。
    @return 按评分、人数和公开条目 ID 收束的排序字段序列。
    """
    return (
        latest_rating.c.score.desc().nulls_last(),
        latest_rating.c.total.desc(),
        SUBJECTS.c.bgm_id.asc(),
    )


def to_season_summary_row(record: RowMapping) -> SeasonSummaryRow:
    """
    @brief 将季度汇总查询结果转换为不可变行模型。
    @param record SQLAlchemy 返回的单行字段映射。
    @return 已完成数据库类型校验的季度汇总行模型。
    """
    return SeasonSummaryRow(
        year=record['year'],
        season=record['season'],
        subject_count=record['subject_count'],
        rated_subject_count=record['rated_subject_count'],
    )


def to_subject_list_row(record: RowMapping) -> SubjectListRow:
    """
    @brief 将通用条目列表查询结果转换为不可变行模型。
    @param record SQLAlchemy 返回的单行字段映射。
    @return 包含规范化文本、标签和可选最新评分的条目列表行模型。
    """
    return SubjectListRow(
        bgm_id=record['bgm_id'],
        name=record['name'],
        translation=record['translation'],
        air_date=record['air_date'],
        year=record['year'],
        season=record['season'],
        tags=tuple(record['tags']),
        cover_url=record['cover_url'],
        latest_rating=_to_latest_rating_row(record),
    )


def to_subject_detail_row(record: RowMapping) -> SubjectDetailRow:
    """
    @brief 将条目详情查询结果转换为不可变行模型。
    @param record SQLAlchemy 返回的单行字段映射。
    @return 包含完整公开详情和可选最新评分的条目详情行模型。
    """
    return SubjectDetailRow(
        bgm_id=record['bgm_id'],
        url=record['url'],
        name=record['name'],
        translation=record['translation'],
        aliases=tuple(record['aliases']),
        summary=record['summary'],
        air_date=record['air_date'],
        year=record['year'],
        season=record['season'],
        tags=tuple(record['tags']),
        cover_url=record['cover_url'],
        latest_rating=_to_latest_rating_row(record),
    )


def to_rating_history_row(record: RowMapping) -> RatingHistoryRow:
    """
    @brief 将评分历史查询结果转换为不可变行模型。
    @param record SQLAlchemy 返回的单行字段映射。
    @return 按原始查询顺序保留的单日评分快照行模型。
    """
    return RatingHistoryRow(
        date=record['date'],
        score=record['score'],
        total=record['total'],
        rank=record['rank'],
    )


def _to_latest_rating_row(record: RowMapping) -> LatestRatingRow | None:
    latest_rating_date = record['latest_rating_date']
    if latest_rating_date is None:
        return None

    return LatestRatingRow(
        date=latest_rating_date,
        score=record['latest_rating_score'],
        total=record['latest_rating_total'],
        rank=record['latest_rating_rank'],
    )


def _empty_text_array() -> ColumnElement[Sequence[str]]:
    return literal_column(
        'ARRAY[]::text[]',
        type_=ARRAY(Text),  # type: ignore[arg-type]
    )

if __name__ == '__main__':
    pass
