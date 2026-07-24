# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file home.py
@brief 定义首页聚合接口的 HTTP 路由。
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies import provide_database_session, provide_services
from backend.api.schemas import HomeResponse
from backend.services.container import ServiceContainer


router = APIRouter(prefix='/api', tags=['home'])


@router.get('/home', response_model=HomeResponse)
async def get_home(
    session: Annotated[AsyncSession, Depends(provide_database_session)],
    services: Annotated[ServiceContainer, Depends(provide_services)],
) -> HomeResponse:
    """
    @brief 返回最新季度和两个固定数量榜单预览。
    @param session 当前请求的只读数据库会话。
    @param services 当前应用共享的业务服务容器。
    @return 首页聚合响应。
    """
    return await services.home.get_home(session=session)


if __name__ == '__main__':
    pass
