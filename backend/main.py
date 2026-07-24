# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file main.py
@brief 组装 AnimeWeb FastAPI 应用。
"""

from contextlib import asynccontextmanager
import logging
from collections.abc import AsyncIterator

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import RequestResponseEndpoint

from backend.data.database import DatabaseResources, create_database_resources
from backend.core.errors import register_exception_handlers
from backend.core.logging import (
    bind_request_id,
    setup_logging,
    reset_request_id,
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def manage_application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    @brief 管理应用级数据库资源。
    @details 生命周期启动时仅创建连接池与会话工厂，不主动建立数据库连接；
             应用关闭时释放连接池中的全部连接。
    @param app 当前 FastAPI 应用实例。
    @return 向 FastAPI 提供已完成资源组装的生命周期上下文。
    """
    database_resources: DatabaseResources = create_database_resources()
    app.state.database_engine = database_resources.engine
    app.state.database_session_factory = database_resources.session_factory

    try:
        yield
    finally:
        await database_resources.engine.dispose()


def create_app() -> FastAPI:
    """
    @brief 创建未注册业务端点的 FastAPI 应用。
    @return 已完成基础中间件和异常处理配置的应用实例。
    """
    setup_logging()
    app = FastAPI(
        docs_url=None,
        lifespan=manage_application_lifespan,
        openapi_url=None,
        redoc_url=None,
    )

    @app.middleware('http')
    async def attach_request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        @brief 为每个 HTTP 响应附加请求标识。
        @param request 当前 HTTP 请求。
        @param call_next FastAPI 提供的后续处理函数。
        @return 已附加请求标识的 HTTP 响应。
        """
        request_id, token = bind_request_id(request.headers.get('X-Request-ID'))
        request.state.request_id = request_id
        try:
            response = await call_next(request)
            response.headers['X-Request-ID'] = request_id
            return response
        finally:
            reset_request_id(token)

    register_exception_handlers(app)
    return app

if __name__ == '__main__':
    pass
