# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file search.py
@brief 定义条目搜索 HTTP 路由。
@details 本路由只负责接收并校验公开查询参数，将搜索编排交由 SearchService。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session, provide_services
from backend.api.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.api.schemas import SearchResponse
from backend.services.container import ServiceContainer


router = APIRouter(prefix='/api', tags=['search'])


@router.get('/search', response_model=SearchResponse)
async def search_subjects(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    q: Annotated[str, Query(description='按名称、译名或别名检索的关键词')],
    page: Annotated[int, Query(ge=DEFAULT_PAGE, description='目标页码')] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=DEFAULT_PAGE, le=MAX_PAGE_SIZE, description='单页条目数量')] = DEFAULT_PAGE_SIZE,
) -> SearchResponse:
    """
    @brief 返回按加权相似度和最新评分稳定排序的搜索结果。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param q 原始搜索关键词。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @return 包含命中字段与分页统计信息的搜索响应。
    """
    return await services.search.search(session=session, query=q, page=page, page_size=page_size)


if __name__ == '__main__':
    pass
