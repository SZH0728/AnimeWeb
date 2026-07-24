# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file dependencies.py
@brief HTTP 层依赖注入入口。

后续路由仅通过本模块从应用状态获取已组装的资源。
"""

from collections.abc import AsyncIterator

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from backend.data.database import get_read_only_session


async def provide_database_session(request: Request) -> AsyncIterator[AsyncSession]:
    """
    @brief 提供当前请求专属的只读数据库会话。
    @details 会话工厂必须已由应用生命周期写入应用状态；本函数不创建
             engine、不会读取配置，也不持有跨请求共享的 session。
    @param request 当前 HTTP 请求。
    @return 仅在请求作用域内有效的只读数据库会话。
    @throws RuntimeError 当应用生命周期尚未完成数据库资源初始化时抛出。
    @throws DatabaseQueryError 当连接、超时或 SQL 执行失败时抛出。
    """
    session_factory = getattr(request.app.state, 'database_session_factory', None)

    if not isinstance(session_factory, async_sessionmaker):
        raise RuntimeError('数据库会话工厂尚未初始化')

    async for session in get_read_only_session(session_factory):
        yield session


if __name__ == '__main__':
    pass
