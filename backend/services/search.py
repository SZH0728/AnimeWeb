# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file search.py
@brief 实现条目搜索接口的业务编排。
@details 本服务负责规范化搜索关键词、协调分页查询，并将数据访问层的搜索行模型
         映射为包含固定命中字段顺序的公开 DTO；搜索结果不使用缓存。
"""

from typing import cast

from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.pagination import calculate_offset, create_pagination
from backend.api.schemas import MatchedFieldName, SearchMeta, SearchResponse, SearchSubjectListItem
from backend.core.errors import InvalidParameterError
from backend.data.queries.search import count_search_results, search_subjects
from backend.data.rows import SearchRow
from backend.services.subjects import SubjectService


class SearchService(object):
    """@brief 提供按名称、译名和别名检索条目的读取能力。"""

    def __init__(self, subjects: SubjectService) -> None:
        """
        @brief 创建复用统一条目摘要映射能力的搜索服务。
        @param subjects 提供封面策略与条目摘要 DTO 映射的条目服务。
        """
        self._subjects = subjects

    async def search(self, session: AsyncSession, query: str, page: int, page_size: int) -> SearchResponse:
        """
        @brief 分页搜索满足相关性阈值的条目。
        @param session 当前请求的只读数据库会话。
        @param query 原始搜索关键词。
        @param page 从 1 开始的目标页码。
        @param page_size 单页最大返回条目数。
        @return 包含规范化关键词、稳定排序说明和命中字段的搜索分页响应。
        @throws InvalidParameterError 当关键词去除首尾空白后为空时抛出。
        """
        normalized_query = self.normalize_query(query)
        offset = calculate_offset(page=page, page_size=page_size)
        total = await count_search_results(session=session, query=normalized_query)
        rows = await search_subjects(session=session, query=normalized_query, limit=page_size, offset=offset)

        return SearchResponse(
            items=[self._to_search_subject_list_item(row) for row in rows],
            pagination=create_pagination(page=page, page_size=page_size, total=total),
            meta=SearchMeta(q=normalized_query, sort='match_relevance_then_latest_score_desc'),
        )

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        @brief 去除搜索关键词的首尾空白并拒绝空关键词。
        @param query HTTP 请求提供的原始搜索关键词。
        @return 可安全传入相似度查询的非空关键词。
        @throws InvalidParameterError 当关键词只包含空白字符时抛出。
        """
        normalized_query = query.strip()

        if not normalized_query:
            raise InvalidParameterError('q 去除首尾空白后不能为空')

        return normalized_query

    def _to_search_subject_list_item(self, row: SearchRow) -> SearchSubjectListItem:
        """
        @brief 将搜索行模型转换为包含命中字段的公开条目摘要。
        @param row 数据访问层返回的搜索结果行模型。
        @return 已应用统一封面策略且命中字段顺序稳定的搜索条目摘要。
        """
        return SearchSubjectListItem(
            **self._subjects.to_subject_list_item(row.subject).model_dump(),
            matched_fields=self.build_matched_fields(row.matched_fields),
        )

    @staticmethod
    def build_matched_fields(fields: tuple[str, ...]) -> list[MatchedFieldName]:
        """
        @brief 校验并转换按数据库固定顺序返回的命中字段。
        @param fields 数据访问层返回的名称、译名或别名字段名称。
        @return 符合公开枚举约束的命中字段列表。
        @throws ValueError 当数据访问层返回未知字段或错误字段顺序时抛出。
        """
        expected_order: tuple[MatchedFieldName, ...] = ('name', 'translation', 'aliases')
        matched_fields: list[MatchedFieldName] = []
        previous_index = -1

        for field in fields:
            if field not in expected_order:
                raise ValueError(f'搜索命中字段无效：{field}')

            matched_field = cast(MatchedFieldName, field)
            current_index = expected_order.index(matched_field)

            if current_index <= previous_index:
                raise ValueError('搜索命中字段顺序无效')

            matched_fields.append(matched_field)
            previous_index = current_index

        return matched_fields


if __name__ == '__main__':
    pass
