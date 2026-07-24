# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file cache.py
@brief 提供应用生命周期持有的进程内 TTL 缓存。
@details 缓存仅用于加速只读热点查询；实例必须由应用入口创建并显式注入服务，
         禁止使用模块级可变状态跨应用实例共享。
"""

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import cast


@dataclass(frozen=True)
class _CacheEntry(object):
    """@brief 表示一个带单调时钟失效时间的缓存项。"""

    expires_at: float  # 使用单调时钟计算的失效时间
    value: object  # 已完成的只读服务响应


class InMemoryTtlCache(object):
    """@brief 提供带异步互斥保护的可关闭进程内 TTL 缓存。"""

    def __init__(self, enabled: bool) -> None:
        """
        @brief 创建空缓存实例。
        @param enabled 是否启用缓存；关闭时不读取、不写入也不等待锁。
        """
        self._enabled = enabled
        self._entries: dict[str, _CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get_or_load[ResultT](self, key: str, ttl_seconds: int, loader: Callable[[], Awaitable[ResultT]]) -> ResultT:
        """
        @brief 在有效期内返回缓存结果，缺失或过期时加载并写回。
        @param key 唯一标识请求参数组合的缓存键。
        @param ttl_seconds 缓存有效秒数，必须为非负整数。
        @param loader 缓存未命中时执行的异步数据库读取函数。
        @return 加载器返回或缓存命中的服务响应。
        @throws ValueError 当缓存有效期小于 0 时抛出。
        """
        if ttl_seconds < 0:
            raise ValueError('缓存有效期不能小于 0')

        if not self._enabled or ttl_seconds == 0:
            return await loader()

        async with self._lock:
            entry = self._entries.get(key)

            if entry is not None and entry.expires_at > monotonic():
                return cast(ResultT, entry.value)

            value = await loader()
            self._entries[key] = _CacheEntry(expires_at=monotonic() + ttl_seconds, value=value)
            return value


if __name__ == '__main__':
    pass
