# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file seasons.py
@brief 定义已收录季度选择的 HTTP 路由。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session, provide_services
from backend.api.schemas import SeasonListResponse
from backend.services.container import ServiceContainer


router = APIRouter(prefix='/api', tags=['seasons'])


@router.get('/seasons', response_model=SeasonListResponse)
async def list_seasons(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
) -> SeasonListResponse:
    """
    @brief 返回全部已收录季度的汇总信息。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @return 按最新年季优先排序的季度选择响应。
    """
    return await services.seasons.list_seasons(session)


if __name__ == '__main__':
    pass
