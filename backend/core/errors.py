# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file errors.py
@brief 定义统一的公开错误契约并注册 HTTP 异常处理器。
@details 所有 JSON 错误响应均使用稳定的 error.code 和 error.message 外壳，
         不向客户端泄露 SQL、堆栈、文件路径、DSN 或凭据。
"""

from logging import getLogger

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from backend.api.schemas import ErrorDetail, ErrorResponse


logger = getLogger(__name__)


class ApiError(Exception):
    """@brief 表示可映射为固定 JSON 契约的应用异常。"""

    status_code: int = 500
    code: str = 'INTERNAL_ERROR'
    default_message: str = '服务器内部错误'

    def __init__(self, message: str | None = None) -> None:
        """
        @brief 创建包含可公开说明的应用异常。
        @param message 覆盖默认值的脱敏客户端说明。
        """
        self.message = message or self.default_message
        super().__init__(self.message)


class InvalidParameterError(ApiError):
    """@brief 表示不符合公开 API 约束的请求参数错误。"""

    status_code = 400
    code = 'INVALID_PARAMETER'
    default_message = '请求参数无效'


class SubjectNotFoundError(ApiError):
    """@brief 表示请求的 Bangumi 条目不存在。"""

    status_code = 404
    code = 'SUBJECT_NOT_FOUND'
    default_message = '未找到请求的条目'


class DatabaseQueryError(ApiError):
    """
    @brief 表示数据库连接、超时或查询执行失败。
    @details 该异常保留底层异常链供统一错误边界记录，不携带可暴露给客户端的 SQL
             或连接凭据。
    """

    status_code = 500
    code = 'INTERNAL_ERROR'
    default_message = '服务器内部错误'


def register_exception_handlers(app: FastAPI) -> None:
    """
    @brief 为应用注册统一 JSON 异常处理器。
    @param app 待注册异常处理器的 FastAPI 应用。
    @return 无返回值；处理器注册到应用实例。
    """
    app.add_exception_handler(InvalidParameterError, handle_api_error)
    app.add_exception_handler(SubjectNotFoundError, handle_api_error)
    app.add_exception_handler(DatabaseQueryError, handle_internal_error)
    app.add_exception_handler(RequestValidationError, handle_request_validation_error)
    app.add_exception_handler(Exception, handle_internal_error)


async def handle_api_error(request: Request, exception: Exception) -> JSONResponse:
    """
    @brief 将预期应用异常转换为标准 JSON 错误响应。
    @param request 触发异常的 HTTP 请求。
    @param exception 已知的公开应用异常。
    @return 包含稳定错误代码和请求标识的 JSON 响应。
    """
    if not isinstance(exception, ApiError):
        return await handle_internal_error(request, exception)

    return _create_error_response(
        request=request,
        status_code=exception.status_code,
        code=exception.code,
        message=exception.message,
    )


async def handle_request_validation_error(request: Request, exception: Exception) -> JSONResponse:
    """
    @brief 将 FastAPI 参数校验失败转换为 400 错误契约。
    @param request 触发校验失败的 HTTP 请求。
    @param exception FastAPI 产生的参数校验异常。
    @return 不包含框架默认细节的 INVALID_PARAMETER 响应。
    """
    if not isinstance(exception, RequestValidationError):
        return await handle_internal_error(request, exception)

    return _create_error_response(
        request=request,
        status_code=InvalidParameterError.status_code,
        code=InvalidParameterError.code,
        message=InvalidParameterError.default_message,
    )


async def handle_internal_error(request: Request, exception: Exception) -> JSONResponse:
    """
    @brief 记录一次完整异常堆栈并返回脱敏内部错误响应。
    @param request 触发异常的 HTTP 请求。
    @param exception 未预期异常或数据库查询异常。
    @return 不含内部诊断信息的 INTERNAL_ERROR 响应。
    """
    logger.exception(f'请求处理失败：异常类型：{exception.__class__.__name__}，路径：{request.url.path}')
    return _create_error_response(request=request, status_code=500, code='INTERNAL_ERROR', message='服务器内部错误')


def _create_error_response(request: Request, status_code: int, code: str, message: str) -> JSONResponse:
    """
    @brief 创建符合公开错误契约的 JSON 响应。
    @param request 触发错误的 HTTP 请求。
    @param status_code HTTP 状态码。
    @param code 稳定的机器可读错误代码。
    @param message 可展示的脱敏错误说明。
    @return 附带请求标识的 JSON 错误响应。
    """
    response = JSONResponse(
        content=ErrorResponse(error=ErrorDetail(code=code, message=message)).model_dump(mode='json'),
        status_code=status_code,
    )

    request_id = getattr(request.state, 'request_id', None)

    if isinstance(request_id, str):
        response.headers['X-Request-ID'] = request_id

    return response


if __name__ == '__main__':
    pass
