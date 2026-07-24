# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file pagination.py
@brief 提供所有分页 API 共用的分页计算工具。
@details 本模块集中约束页码、每页大小、偏移量和总页数的计算，确保空结果和
         超出页码范围时始终返回稳定的 200 分页外壳。
"""

from collections.abc import Sequence

from backend.api.schemas import PaginatedResponse, Pagination
from backend.core.config import config
from backend.core.errors import InvalidParameterError


DEFAULT_PAGE = config.getint('pagination', 'default_page')
DEFAULT_PAGE_SIZE = config.getint('pagination', 'default_page_size')
MAX_PAGE_SIZE = config.getint('pagination', 'max_page_size')


def calculate_offset(page: int, page_size: int) -> int:
    """
    @brief 根据有效分页参数计算数据库查询偏移量。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @return 对应目标页首条记录的零基偏移量。
    @throws InvalidParameterError 当页码或每页大小不符合公开契约时抛出。
    """
    _validate_pagination_parameters(page=page, page_size=page_size)
    return (page - 1) * page_size


def create_pagination(page: int, page_size: int, total: int) -> Pagination:
    """
    @brief 创建统一的分页统计 DTO。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @param total 当前筛选条件下的总条目数。
    @return 包含总页数的公开分页信息。
    @throws InvalidParameterError 当分页参数或总条目数无效时抛出。
    """
    _validate_pagination_parameters(page=page, page_size=page_size)

    if total < 0:
        raise InvalidParameterError('总条目数不能小于 0')

    total_pages = (total + page_size - 1) // page_size
    return Pagination(page=page, page_size=page_size, total=total, total_pages=total_pages)


def create_paginated_response[ItemT](items: Sequence[ItemT], page: int, page_size: int, total: int) -> PaginatedResponse[ItemT]:
    """
    @brief 创建统一的分页响应外壳。
    @details 即使页码超过总页数，也保留正确的分页统计信息并返回空 items。
    @param items 当前页已转换完成的公开条目。
    @param page 从 1 开始的目标页码。
    @param page_size 单页最大返回条目数。
    @param total 当前筛选条件下的总条目数。
    @return 可直接作为 JSON API 响应返回的分页 DTO。
    @throws InvalidParameterError 当分页参数或总条目数无效时抛出。
    """
    return PaginatedResponse[ItemT](
        items=list(items),
        pagination=create_pagination(page=page, page_size=page_size, total=total),
    )


def _validate_pagination_parameters(page: int, page_size: int) -> None:
    """@brief 验证分页参数符合公开 API 契约。"""
    if page < DEFAULT_PAGE:
        raise InvalidParameterError('page 必须大于或等于 1')

    if not DEFAULT_PAGE <= page_size <= MAX_PAGE_SIZE:
        raise InvalidParameterError('page_size 必须在 1 到 100 之间')


if __name__ == '__main__':
    pass
