# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file subjects.py
@brief 定义季度目录、条目详情和评分历史的 HTTP 路由。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session, provide_services
from backend.api.pagination import DEFAULT_PAGE, DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE
from backend.api.schemas import RatingHistoryResponse, SeasonName, SubjectDetail, SubjectListResponse
from backend.services.container import ServiceContainer


router = APIRouter(prefix='/api', tags=['subjects'])


@router.get('/subjects', response_model=SubjectListResponse)
async def list_subjects(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    year: Annotated[int, Query(ge=1, description='精确播出年份')],
    season: Annotated[SeasonName, Query(description='播出季度')],
    min_total: Annotated[int, Query(ge=0, description='最新评分人数下限')] = 0,
    page: Annotated[int, Query(ge=DEFAULT_PAGE, description='从 1 开始的页码')] = DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=DEFAULT_PAGE, le=MAX_PAGE_SIZE, description='单页条目数量')] = DEFAULT_PAGE_SIZE,
) -> SubjectListResponse:
    """
    @brief 返回指定年季的稳定排序分页目录。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param year 目标播出年份。
    @param season 目标播出季度。
    @param min_total 最新评分人数下限。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @return 包含筛选、排序与快照口径的目录分页响应。
    """
    return await services.subjects.list_subjects(
        session=session,
        year=year,
        season=season,
        min_total=min_total,
        page=page,
        page_size=page_size,
    )


@router.get('/subjects/{bgm_id}/ratings', response_model=RatingHistoryResponse)
async def get_rating_history(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    bgm_id: Annotated[int, Path(gt=0, description='正整数 Bangumi 条目 ID')],
) -> RatingHistoryResponse:
    """
    @brief 返回指定条目的评分历史快照。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param bgm_id Bangumi 公开条目 ID。
    @return 按采集日期升序排列的评分历史响应；超过 30 条时按间隔采样且保留最新快照。
    """
    return await services.subjects.get_rating_history(session=session, bgm_id=bgm_id)


@router.get('/subjects/{bgm_id}', response_model=SubjectDetail)
async def get_subject(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
    bgm_id: Annotated[int, Path(gt=0, description='正整数 Bangumi 条目 ID')],
) -> SubjectDetail:
    """
    @brief 返回指定条目的完整公开详情。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @param bgm_id Bangumi 公开条目 ID。
    @return 条目存在时的完整公开详情。
    """
    return await services.subjects.get_subject_detail(session=session, bgm_id=bgm_id)


if __name__ == '__main__':
    pass

