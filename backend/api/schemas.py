# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file schemas.py
@brief 定义公开 JSON API 的字段白名单与响应模型。
@details 本模块中的 Pydantic 模型是 HTTP 响应的唯一公开数据边界，禁止包含
         数据库内部主键、infobox、封面二进制内容或评分分布字段。
"""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


SeasonName = Literal['winter', 'spring', 'summer', 'fall']
MatchedFieldName = Literal['name', 'translation', 'aliases']


class ApiSchema(BaseModel):
    """
    @brief 定义公开 API DTO 的共用序列化约束。
    @details 禁止模型接收未声明字段，以保证响应模型持续作为公开字段白名单。
    """

    model_config = ConfigDict(extra='forbid', populate_by_name=True)


class LatestRating(ApiSchema):
    """@brief 表示同一采集日产生的最新评分快照。"""

    date: date  # 快照采集日期
    score: float | None  # 综合评分；未知时为 null
    total: int  # 快照对应的评分人数，0 为有效值
    rank: int | None  # Bangumi 综合排名；未知时为 null


class SeasonSummary(ApiSchema):
    """@brief 表示已收录播出季度的条目汇总。"""

    year: int  # 播出年份
    season: SeasonName  # 播出季度
    subject_count: int  # 季度内的条目总数
    rated_subject_count: int  # 至少拥有一个评分快照的条目数


class SubjectListItem(ApiSchema):
    """@brief 表示首页、目录、搜索和榜单使用的条目摘要。"""

    bgm_id: int  # Bangumi 公开条目 ID
    name: str  # 条目原名
    translation: str | None  # 规范化后的译名
    air_date: date | None  # 首播日期
    year: int | None  # 播出年份
    season: SeasonName | None  # 播出季度
    tags: list[str] = Field(default_factory=list)  # 条目标签；无值时返回空数组
    cover_url: str | None  # 抽象封面地址
    latest_rating: LatestRating | None  # 条目的最新评分快照


class SearchSubjectListItem(SubjectListItem):
    """@brief 表示附带命中字段信息的搜索条目摘要。"""

    matched_fields: list[MatchedFieldName] = Field(default_factory=list)  # 固定顺序的搜索命中字段


class SubjectDetail(ApiSchema):
    """@brief 表示单个条目的完整公开详情。"""

    bgm_id: int  # Bangumi 公开条目 ID
    url: str  # Bangumi 条目链接
    name: str  # 条目原名
    translation: str | None  # 规范化后的译名
    aliases: list[str] = Field(default_factory=list)  # 条目别名；无值时返回空数组
    summary: str | None  # 规范化后的剧情简介
    air_date: date | None  # 首播日期
    year: int | None  # 播出年份
    season: SeasonName | None  # 播出季度
    tags: list[str] = Field(default_factory=list)  # 条目标签；无值时返回空数组
    cover_url: str | None  # 抽象封面地址
    latest_rating: LatestRating | None  # 条目的最新评分快照


class RatingHistoryPoint(ApiSchema):
    """@brief 表示一个按采集日期排列的评分历史快照。"""

    date: date  # 快照采集日期
    score: float | None  # 综合评分；未知时为 null
    total: int  # 快照对应的评分人数，0 为有效值
    rank: int | None  # Bangumi 综合排名；未知时为 null


class RankingItem(ApiSchema):
    """@brief 表示当前筛选和排序条件下的一项榜单结果。"""

    position: int  # 按完整稳定排序计算的连续名次
    metric_value: float | int  # 高分榜为评分，最多人评价榜为评分人数
    subject: SubjectListItem  # 上榜条目的公开摘要


class Pagination(ApiSchema):
    """@brief 表示分页查询在当前筛选条件下的统计信息。"""

    page: int  # 当前页码，从 1 开始
    page_size: int  # 当前每页条目数量
    total: int  # 当前筛选条件下的总条目数
    total_pages: int  # 总页数；空结果时为 0


class PaginatedResponse[ItemT](ApiSchema):
    """@brief 表示携带统一分页外壳的公开响应。"""

    items: list[ItemT] = Field(default_factory=list)  # 当前页的公开条目列表
    pagination: Pagination  # 当前分页统计信息


class SubjectPreview(ApiSchema):
    """@brief 表示首页中固定数量的条目预览区块。"""

    items: list[SubjectListItem] = Field(default_factory=list)  # 按对应区块规则排序的条目预览


class LatestSeasonPreview(SeasonSummary):
    """@brief 表示首页最新季度及其固定数量的条目预览。"""

    items: list[SubjectListItem] = Field(default_factory=list)  # 最新季度内按固定规则排序的条目预览


class HomeResponse(ApiSchema):
    """@brief 表示首页聚合接口的公开响应。"""

    latest_season: LatestSeasonPreview | None  # 最新已收录季度；不存在时为 null
    top_score: SubjectPreview  # 最高评分榜预览
    most_rated: SubjectPreview  # 最多人评价榜预览


class SeasonListResponse(ApiSchema):
    """@brief 表示全部已收录季度的选择器响应。"""

    items: list[SeasonSummary] = Field(default_factory=list)  # 按最新季度优先排序的季度列表


class SubjectListMeta(ApiSchema):
    """@brief 表示季度目录分页查询的固定元数据。"""

    year: int  # 当前筛选的播出年份
    season: SeasonName  # 当前筛选的播出季度
    min_total: int  # 当前筛选的最新评分人数下限
    sort: Literal['latest_score_desc']  # 已应用的稳定排序名称
    snapshot_basis: Literal['per_subject_latest']  # 最新评分的读取口径


class SubjectListResponse(PaginatedResponse[SubjectListItem]):
    """@brief 表示季度目录分页接口的公开响应。"""

    meta: SubjectListMeta  # 当前筛选与排序说明


class SearchMeta(ApiSchema):
    """@brief 表示搜索分页查询的固定元数据。"""

    q: str  # 已去除首尾空白的搜索关键词
    sort: Literal['match_relevance_then_latest_score_desc']  # 已应用的稳定排序名称


class SearchResponse(PaginatedResponse[SearchSubjectListItem]):
    """@brief 表示搜索分页接口的公开响应。"""

    meta: SearchMeta  # 当前搜索词与排序说明


class TopScoreRankingMeta(ApiSchema):
    """@brief 表示最高评分榜分页查询的固定元数据。"""

    ranking_type: Literal['top_score']  # 当前榜单类型
    min_total: int  # 当前筛选的最新评分人数下限
    snapshot_basis: Literal['per_subject_latest']  # 最新评分的读取口径


class TopScoreRankingResponse(PaginatedResponse[RankingItem]):
    """@brief 表示最高评分榜分页接口的公开响应。"""

    meta: TopScoreRankingMeta  # 当前筛选与评分口径说明


class MostRatedRankingMeta(ApiSchema):
    """@brief 表示最多人评价榜分页查询的固定元数据。"""

    ranking_type: Literal['most_rated']  # 当前榜单类型
    snapshot_basis: Literal['per_subject_latest']  # 最新评分的读取口径


class MostRatedRankingResponse(PaginatedResponse[RankingItem]):
    """@brief 表示最多人评价榜分页接口的公开响应。"""

    meta: MostRatedRankingMeta  # 当前筛选与评分口径说明


class DateRange(ApiSchema):
    """@brief 表示本次返回评分历史的首末采集日期。"""

    from_date: date = Field(serialization_alias='from', validation_alias='from')  # 返回历史首个快照日期
    to_date: date = Field(serialization_alias='to', validation_alias='to')  # 返回历史最后一个快照日期


class RatingHistoryResponse(ApiSchema):
    """@brief 表示单个条目的评分历史快照响应。"""

    bgm_id: int  # Bangumi 公开条目 ID
    available_range: DateRange | None  # 返回快照的日期范围；无历史时为 null
    items: list[RatingHistoryPoint] = Field(default_factory=list)  # 按日期升序的评分历史快照；长历史可能为采样结果


class ErrorDetail(ApiSchema):
    """@brief 表示面向客户端的标准化错误信息。"""

    code: str  # 稳定的机器可读错误代码
    message: str  # 可直接展示的脱敏错误说明


class ErrorResponse(ApiSchema):
    """@brief 表示所有 JSON API 共用的错误响应外壳。"""

    error: ErrorDetail  # 标准化错误信息


if __name__ == '__main__':
    pass


