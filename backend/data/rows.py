# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file rows.py
@brief 定义数据访问层返回的不可变查询投影。
@details 查询模块仅返回本文件中的数据库行模型，不依赖 Pydantic、HTTP 响应或
         FastAPI 对象；服务层负责将这些投影映射为公开 API 模型。
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Literal


SeasonName = Literal['winter', 'spring', 'summer', 'fall']


@dataclass(frozen=True)
class LatestRatingRow(object):
    """@brief 表示单个条目的最新评分快照。"""

    date: date  # 快照采集日期
    score: Decimal | None  # 综合评分
    total: int  # 参与评分总人数
    rank: int | None  # Bangumi 综合排名


@dataclass(frozen=True)
class SeasonSummaryRow(object):
    """@brief 表示一个已收录季度的汇总信息。"""

    year: int  # 播出年份
    season: SeasonName  # 播出季度枚举值
    subject_count: int  # 季度内条目数
    rated_subject_count: int  # 至少拥有一个评分快照的条目数


@dataclass(frozen=True)
class SubjectListRow(object):
    """@brief 表示列表、首页和榜单共用的条目投影。"""

    bgm_id: int  # Bangumi 公开条目 ID
    name: str  # 条目原名
    translation: str | None  # 规范化后的中文译名
    air_date: date | None  # 首播日期
    year: int | None  # 播出年份
    season: SeasonName | None  # 播出季度
    tags: tuple[str, ...]  # 标签集合
    cover_url: str | None  # 规范化后的封面地址
    latest_rating: LatestRatingRow | None  # 最新评分快照


@dataclass(frozen=True)
class SubjectListPageRow(object):
    """@brief 表示季度目录分页查询的总数与当前页条目。"""

    total: int  # 当前筛选条件下的总条目数
    items: tuple[SubjectListRow, ...]  # 当前页的不可变条目列表


@dataclass(frozen=True)
class SubjectDetailRow(object):
    """@brief 表示条目详情查询所需的完整公开字段。"""

    bgm_id: int  # Bangumi 公开条目 ID
    url: str  # Bangumi 条目链接
    name: str  # 条目原名
    translation: str | None  # 规范化后的中文译名
    aliases: tuple[str, ...]  # 别名集合
    summary: str | None  # 规范化后的剧情简介
    air_date: date | None  # 首播日期
    year: int | None  # 播出年份
    season: SeasonName | None  # 播出季度
    tags: tuple[str, ...]  # 标签集合
    cover_url: str | None  # 规范化后的封面地址
    latest_rating: LatestRatingRow | None  # 最新评分快照


@dataclass(frozen=True)
class RatingHistoryRow(object):
    """@brief 表示一条按日期排序的评分历史快照。"""

    date: date  # 快照采集日期
    score: Decimal | None  # 综合评分
    total: int  # 参与评分总人数
    rank: int | None  # Bangumi 综合排名


@dataclass(frozen=True)
class RankingRow(object):
    """@brief 表示排行榜中的一项排序结果。"""

    position: int  # 当前筛选条件下的连续榜单名次
    metric_value: Decimal | int  # 当前榜单使用的指标值
    subject: SubjectListRow  # 榜单条目的公开字段投影


@dataclass(frozen=True)
class SearchRow(object):
    """@brief 表示带命中字段信息的搜索结果投影。"""

    subject: SubjectListRow  # 搜索命中的公开条目字段
    matched_fields: tuple[str, ...]  # 固定顺序的命中字段名称


@dataclass(frozen=True)
class CoverImageRow(object):
    """@brief 表示内部图片端点读取的封面二进制投影。"""

    cover_image: bytes | None  # 数据库存储的封面二进制内容

if __name__ == '__main__':
    pass
