# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file errors.py
@brief 注册统一的 HTTP 异常处理入口。
"""

import logging

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


class DatabaseQueryError(Exception, object):
    """
    @brief 表示数据库连接、超时或查询执行失败。
    @details 该异常保留底层异常链，供统一错误边界记录诊断信息，
             不携带会暴露给客户端的 SQL 或连接凭据。
    """


def register_exception_handlers(app: FastAPI) -> None:
    """
    @brief 为应用注册统一异常处理器。
    @param app 待注册异常处理器的 FastAPI 应用。
    """
    app.add_exception_handler(Exception, handle_unexpected_error)


async def handle_unexpected_error(request: Request, exception: Exception) -> JSONResponse:
    """
    @brief 记录未预期异常并返回安全的内部错误响应。
    @param request 触发异常的 HTTP 请求。
    @param exception 未预期异常。
    @return 不含内部诊断信息的 HTTP 错误响应。
    """
    logger.exception(f'未处理的请求异常：{exception.__class__.__name__}，路径：{request.url.path}',)

    response = JSONResponse(
        content={
            'error': {
                'code': 'INTERNAL_ERROR',
                'message': '服务器内部错误',
            },
        },
        status_code=500,
    )

    request_id = getattr(request.state, 'request_id', None)

    if isinstance(request_id, str):
        response.headers['X-Request-ID'] = request_id

    return response

if __name__ == '__main__':
    pass
