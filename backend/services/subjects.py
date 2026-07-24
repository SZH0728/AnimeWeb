# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file subjects.py
@brief 实现季度目录、条目详情和评分历史接口的业务编排。
@details 本服务集中维护行模型到公开 DTO 的映射，包括统一的封面 URL 策略；不
         直接构造 SQLAlchemy 查询或处理 HTTP 请求参数。
"""

from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.config import config
from backend.api.pagination import calculate_offset, create_pagination
from backend.api.schemas import DateRange, LatestRating, RatingHistoryPoint, RatingHistoryResponse, SeasonName, SubjectDetail, SubjectListItem, SubjectListMeta, SubjectListResponse
from backend.core.errors import SubjectNotFoundError
from backend.data.queries.subjects import get_subject_detail, list_rating_history, list_subject_page, subject_exists
from backend.data.rows import LatestRatingRow, RatingHistoryRow, SubjectDetailRow, SubjectListRow


class SubjectService(object):
    """@brief 提供季度条目、详情与评分历史的读取能力。"""

    def __init__(self) -> None:
        """@brief 创建统一处理封面 URL 的条目服务。"""
        self._image_strategy = config.get('images', 'strategy').strip()

    async def list_subjects(self, session: AsyncSession, year: int, season: SeasonName, min_total: int, page: int, page_size: int) -> SubjectListResponse:
        """
        @brief 分页获取指定季度的条目目录。
        @param session 当前请求的只读数据库会话。
        @param year 目标播出年份。
        @param season 目标播出季度。
        @param min_total 最新评分人数下限，0 表示保留无评分条目。
        @param page 从 1 开始的目标页码。
        @param page_size 单页最大返回条目数。
        @return 包含固定排序说明的季度目录分页响应。
        """
        offset = calculate_offset(page=page, page_size=page_size)
        page_result = await list_subject_page(session=session, year=year, season=season, min_total=min_total, limit=page_size, offset=offset)

        return SubjectListResponse(
            items=[self.to_subject_list_item(row) for row in page_result.items],
            pagination=create_pagination(page=page, page_size=page_size, total=page_result.total),
            meta=SubjectListMeta(
                year=year,
                season=season,
                min_total=min_total,
                sort='latest_score_desc',
                snapshot_basis='per_subject_latest',
            ),
        )

    async def get_subject_detail(self, session: AsyncSession, bgm_id: int) -> SubjectDetail:
        """
        @brief 获取单个条目的完整公开详情。
        @param session 当前请求的只读数据库会话。
        @param bgm_id Bangumi 公开条目 ID。
        @return 条目存在时的完整公开详情。
        @throws SubjectNotFoundError 当条目不存在时抛出。
        """
        row = await get_subject_detail(session=session, bgm_id=bgm_id)

        if row is None:
            raise SubjectNotFoundError()

        return self._to_subject_detail(row)

    async def get_rating_history(self, session: AsyncSession, bgm_id: int) -> RatingHistoryResponse:
        """
        @brief 获取单个条目的全部评分历史。
        @param session 当前请求的只读数据库会话。
        @param bgm_id Bangumi 公开条目 ID。
        @return 按快照日期升序排列的评分历史响应。
        @throws SubjectNotFoundError 当条目不存在时抛出。
        """
        if not await subject_exists(session=session, bgm_id=bgm_id):
            raise SubjectNotFoundError()

        rows = await list_rating_history(session=session, bgm_id=bgm_id)
        items = [self._to_rating_history_point(row) for row in rows]
        available_range = None

        if items:
            available_range = DateRange(from_date=items[0].date, to_date=items[-1].date)

        return RatingHistoryResponse(bgm_id=bgm_id, available_range=available_range, items=items)

    def to_subject_list_item(self, row: SubjectListRow) -> SubjectListItem:
        """
        @brief 将季度目录行模型转换为统一条目摘要 DTO。
        @param row 数据访问层返回的条目列表行模型。
        @return 已应用封面策略的公开条目摘要。
        """
        return SubjectListItem(
            bgm_id=row.bgm_id,
            name=row.name,
            translation=row.translation,
            air_date=row.air_date,
            year=row.year,
            season=row.season,
            tags=list(row.tags),
            cover_url=self._map_cover_url(row.bgm_id, row.cover_url),
            latest_rating=self._to_latest_rating(row.latest_rating),
        )

    def _to_subject_detail(self, row: SubjectDetailRow) -> SubjectDetail:
        """
        @brief 将详情行模型转换为统一的详情 DTO。
        @param row 数据访问层返回的条目详情行模型。
        @return 已应用封面策略的公开条目详情。
        """
        return SubjectDetail(
            bgm_id=row.bgm_id,
            url=row.url,
            name=row.name,
            translation=row.translation,
            aliases=list(row.aliases),
            summary=row.summary,
            air_date=row.air_date,
            year=row.year,
            season=row.season,
            tags=list(row.tags),
            cover_url=self._map_cover_url(row.bgm_id, row.cover_url),
            latest_rating=self._to_latest_rating(row.latest_rating),
        )

    def _map_cover_url(self, bgm_id: int, external_cover_url: str | None) -> str | None:
        """
        @brief 根据全局策略映射前端可使用的封面地址。
        @param bgm_id Bangumi 公开条目 ID。
        @param external_cover_url 已由查询层规范化的外部封面地址。
        @return 外部封面地址、固定内部图片地址或 null。
        """
        if self._image_strategy == 'internal':
            return f'/images/{bgm_id}'

        return external_cover_url

    def _to_latest_rating(self, row: LatestRatingRow | None) -> LatestRating | None:
        """
        @brief 将可选最新评分快照行模型转换为公开 DTO。
        @param row 数据访问层返回的可选最新评分快照。
        @return 评分存在时的公开 DTO；否则为 null。
        """
        if row is None:
            return None

        return LatestRating(date=row.date, score=self._to_float(row.score), total=row.total, rank=row.rank)

    def _to_rating_history_point(self, row: RatingHistoryRow) -> RatingHistoryPoint:
        """
        @brief 将评分历史行模型转换为公开 DTO。
        @param row 数据访问层返回的评分历史行模型。
        @return 保持原有日期顺序的公开评分历史点。
        """
        return RatingHistoryPoint(date=row.date, score=self._to_float(row.score), total=row.total, rank=row.rank)

    @staticmethod
    def _to_float(value: Decimal | None) -> float | None:
        """
        @brief 将数据库 numeric 评分转换为 JSON 可序列化浮点数。
        @param value 数据库评分；未知评分为 null。
        @return 评分浮点数或 null。
        """
        if value is None:
            return None

        return float(value)


if __name__ == '__main__':
    pass




