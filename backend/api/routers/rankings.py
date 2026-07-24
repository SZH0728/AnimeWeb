# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file rankings.py
@brief 定义高分榜与最多人评价榜的 HTTP 路由。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session, provide_services
from backend.api.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.api.schemas import MostRatedRankingResponse, TopScoreRankingResponse
from backend.services.container import ServiceContainer


router = APIRouter(prefix='/api/rankings', tags=['rankings'])


@router.get('/top-score', response_model=TopScoreRankingResponse)
async def list_top_score_rankings(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    min_total: Annotated[int, Query(ge=0, description='最新评分人数下限')] = 0,
    page: Annotated[int, Query(ge=DEFAULT_PAGE, description='目标页码')] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=DEFAULT_PAGE, le=MAX_PAGE_SIZE, description='单页条目数量')] = DEFAULT_PAGE_SIZE,
) -> TopScoreRankingResponse:
    """
    @brief 返回最新评分优先的稳定分页榜单。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param min_total 最新评分人数下限。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @return 包含完整筛选结果连续名次的高分榜响应。
    """
    return await services.rankings.list_top_score_rankings(
        session=session,
        min_total=min_total,
        page=page,
        page_size=page_size,
    )


@router.get('/most-rated', response_model=MostRatedRankingResponse)
async def list_most_rated_rankings(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    page: Annotated[int, Query(ge=DEFAULT_PAGE, description='目标页码')] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=DEFAULT_PAGE, le=MAX_PAGE_SIZE, description='单页条目数量')] = DEFAULT_PAGE_SIZE,
) -> MostRatedRankingResponse:
    """
    @brief 返回最新评分人数优先的稳定分页榜单。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @return 包含完整筛选结果连续名次的最多人评价榜响应。
    """
    return await services.rankings.list_most_rated_rankings(
        session=session,
        page=page,
        page_size=page_size,
    )


if __name__ == '__main__':
    pass
