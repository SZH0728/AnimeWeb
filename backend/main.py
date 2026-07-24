# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file main.py
@brief 组装 AnimeWeb FastAPI 应用。
@details 本模块是基础设施和服务对象的唯一组装入口；模块导入阶段不建立
         数据库连接或执行网络 I/O。
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.responses import Response
from starlette.middleware.base import RequestResponseEndpoint

from backend.api.routers.home import router as home_router
from backend.api.routers.images import router as images_router
from backend.api.routers.rankings import router as rankings_router
from backend.api.routers.search import router as search_router
from backend.api.routers.seasons import router as seasons_router
from backend.api.routers.subjects import router as subjects_router
from backend.core.cache import InMemoryTtlCache
from backend.core.config import config
from backend.core.errors import register_exception_handlers
from backend.core.logging import bind_request_id, reset_request_id, setup_logging
from backend.data.database import DatabaseResources, create_database_resources
from backend.services.container import create_service_container


logger = getLogger(__name__)


@asynccontextmanager
async def manage_application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    @brief 管理应用级数据库资源与服务容器。
    @details 生命周期启动时仅创建连接池、会话工厂和服务对象，不主动建立数据库
             连接；应用关闭时释放连接池中的全部连接。
    @param app 当前 FastAPI 应用实例。
    @return 向 FastAPI 提供已完成资源组装的生命周期上下文。
    """
    database_resources: DatabaseResources = create_database_resources()
    app.state.database_engine = database_resources.engine
    app.state.database_session_factory = database_resources.session_factory
    cache = InMemoryTtlCache(enabled=config.getboolean('cache', 'enabled'))
    app.state.cache = cache
    app.state.services = create_service_container(cache)

    try:
        yield
    finally:
        await database_resources.engine.dispose()


def create_app() -> FastAPI:
    """
    @brief 创建并注册公开业务端点的 FastAPI 应用。
    @return 已完成基础中间件、依赖资源、异常处理和当前业务路由配置的应用实例。
    """
    setup_logging()
    app = FastAPI(
        # docs_url=None,
        lifespan=manage_application_lifespan,
        # openapi_url=None,
        # redoc_url=None,
    )

    @app.middleware('http')
    async def attach_request_id(request: Request, call_next: RequestResponseEndpoint) -> Response:
        """
        @brief 为每个 JSON 成功和错误响应附加请求标识。
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
    app.include_router(home_router)
    app.include_router(images_router)
    app.include_router(rankings_router)
    app.include_router(search_router)
    app.include_router(seasons_router)
    app.include_router(subjects_router)
    return app


fast_app = create_app()

if __name__ == '__main__':
    pass
