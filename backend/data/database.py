# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file database.py
@brief 管理异步 PostgreSQL 连接池与请求级只读会话。
@details 本模块只负责创建可注入的 SQLAlchemy 资源，并为每个请求建立短生命周期、
         设置事务只读与语句超时的会话；不在模块导入阶段连接数据库。
"""

from collections.abc import AsyncIterator
from dataclasses import dataclass

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from backend.core.config import config
from backend.core.errors import DatabaseQueryError


@dataclass(frozen=True)
class DatabaseResources(object):
    """@brief 封装应用生命周期持有的数据库资源。"""

    engine: AsyncEngine  # 异步数据库连接池
    session_factory: async_sessionmaker[AsyncSession]  # 请求级会话工厂


def create_database_resources() -> DatabaseResources:
    """
    @brief 根据 INI 配置创建异步 engine 与会话工厂。
    @details 仅构造资源对象，不会在此阶段建立网络连接；连接超时、
             池规模和池等待时间均由数据库配置决定。
    @return 可注入到 FastAPI 应用状态的数据库资源。
    @throws ValueError 当数据库配置缺失、格式错误或超出允许范围时抛出。
    """
    engine = create_async_engine(
        config.get('database', 'dsn').strip(),
        connect_args={'timeout': config.getint('database', 'connect_timeout_seconds')},
        max_overflow=config.getint('database', 'max_overflow'),
        pool_pre_ping=True,
        pool_size=config.getint('database', 'pool_size'),
        pool_timeout=config.getint('database', 'connect_timeout_seconds'),
    )

    session_factory = async_sessionmaker(engine, autoflush=False, expire_on_commit=False)
    return DatabaseResources(engine=engine, session_factory=session_factory)


async def get_read_only_session(session_factory: async_sessionmaker[AsyncSession]) -> AsyncIterator[AsyncSession]:
    """
    @brief 创建并提供单次请求使用的只读数据库会话。
    @details 每个会话在独立事务中设置只读标志和本地语句超时。所有 SQLAlchemy、
             连接池或 asyncio 超时错误均转换为内部数据库查询异常并保留异常链。
    @param session_factory 由应用生命周期创建的异步会话工厂。
    @return 已启用只读约束的短生命周期会话。
    @throws DatabaseQueryError 当数据库资源不可用、事务配置失败或查询失败时抛出。
    """
    statement_timeout_seconds = config.getint('database', 'statement_timeout_seconds')

    try:
        async with session_factory() as session, session.begin():
            await session.execute(text('SET TRANSACTION READ ONLY'))
            await session.execute(
                text("SELECT set_config('statement_timeout', :timeout, true)"),
                {'timeout': f'{statement_timeout_seconds}s'},
            )
            yield session
    except DatabaseQueryError:
        raise
    except (SQLAlchemyError, TimeoutError) as exception:
        raise DatabaseQueryError('数据库查询失败') from exception

if __name__ == '__main__':
    pass
