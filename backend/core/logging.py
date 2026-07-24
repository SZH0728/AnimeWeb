# -*- coding:utf-8 -*-
# AUTHOR: Sun
"""@file logging.py
@brief 提供请求标识上下文与应用日志配置。
"""

import logging
from contextvars import ContextVar, Token
from configparser import SectionProxy
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from re import compile
from uuid import uuid4

from backend.core.config import config


_REQUEST_ID_PATTERN = compile(r'^[A-Za-z0-9._-]{1,128}$')
_REQUEST_ID: ContextVar[str | None] = ContextVar('request_id', default=None)


class _RequestIdFilter(logging.Filter):
    """@brief 将当前请求标识注入日志记录。"""

    def filter(self, record: logging.LogRecord) -> bool:
        """
        @brief 为日志记录补充请求标识。
        @param record 待输出的日志记录。
        @return 始终允许输出日志记录。
        """
        record.request_id = get_request_id() or '-'
        return True


def setup_logging() -> None:
    """
    @brief 根据 INI 配置初始化应用日志。
    @details debug 开启时仅输出全部级别的控制台日志；关闭时写入按日轮转的
             info.log 与 warning.log，前者保留 7 天，后者永不自动删除。
    """
    is_debug: bool = config.getboolean('app', 'debug')

    logging_config: SectionProxy = config['logging']
    log_format: str = logging_config['format']
    log_dir: str = logging_config['log_dir']

    info_backup: int = config.getint('logging', 'info_backup_count')
    error_backup: int = config.getint('logging', 'error_backup_count')
    suppress_libraries: list[str] = [lib.strip() for lib in logging_config['suppress_libs'].split(',')]

    root_logger = logging.getLogger()

    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    root_logger.setLevel(logging.DEBUG)
    request_id_filter = _RequestIdFilter()

    if is_debug:
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        handler.setFormatter(logging.Formatter(log_format, datefmt=logging_config['date_format_debug']))
        handler.addFilter(request_id_filter)
        root_logger.addHandler(handler)
    else:
        Path(log_dir).mkdir(parents=True, exist_ok=True)
        formatter = logging.Formatter(log_format, datefmt=logging_config['date_format_prod'])

        info_h = TimedRotatingFileHandler(f'{log_dir}/info.log', when='midnight', backupCount=info_backup, encoding='utf-8', delay=True)
        info_h.setLevel(logging.INFO)
        info_h.setFormatter(formatter)
        info_h.addFilter(request_id_filter)

        error_h = TimedRotatingFileHandler(f'{log_dir}/error.log', when='midnight', backupCount=error_backup, encoding='utf-8', delay=True)
        error_h.setLevel(logging.ERROR)
        error_h.setFormatter(formatter)
        error_h.addFilter(request_id_filter)

        root_logger.addHandler(info_h)
        root_logger.addHandler(error_h)

    for lib in suppress_libraries:
        logging.getLogger(lib).setLevel(logging.WARNING)


def bind_request_id(incoming_request_id: str | None) -> tuple[str, Token[str | None]]:
    """
    @brief 绑定合法的入站请求标识或生成新标识。
    @param incoming_request_id 入站 HTTP 头中的请求标识。
    @return 生效的请求标识及其上下文重置令牌。
    """
    request_id = incoming_request_id or ''

    if not _REQUEST_ID_PATTERN.fullmatch(request_id):
        request_id = str(uuid4())

    return request_id, _REQUEST_ID.set(request_id)


def get_request_id() -> str | None:
    """
    @brief 获取当前请求上下文的请求标识。
    @return 当前请求标识；没有请求上下文时返回空值。
    """
    return _REQUEST_ID.get()


def reset_request_id(token: Token[str | None]) -> None:
    """
    @brief 清理当前请求的请求标识上下文。
    @param token 绑定请求标识时返回的上下文令牌。
    """
    _REQUEST_ID.reset(token)


if __name__ == '__main__':
    pass
