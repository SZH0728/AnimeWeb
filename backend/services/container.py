# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file container.py
@brief 定义服务层的应用级组装与注入容器。
@details 容器在应用生命周期中创建并写入 app.state；缓存实例由 main.py 创建后
         显式注入所有需要缓存的服务，路由禁止自行构造业务服务或读取运行时配置。
"""

from dataclasses import dataclass

from backend.core.cache import InMemoryTtlCache
from backend.core.config import config
from backend.services.home import HomeService
from backend.services.rankings import RankingService
from backend.services.search import SearchService
from backend.services.seasons import SeasonService
from backend.services.subjects import SubjectService


@dataclass(frozen=True)
class ServiceContainer(object):
    """@brief 表示当前应用可注入的业务服务集合。"""

    seasons: SeasonService  # 季度选择服务
    subjects: SubjectService  # 季度条目、详情与评分历史服务
    rankings: RankingService  # 高分与最多人评价榜服务
    home: HomeService  # 首页聚合服务
    search: SearchService  # 名称、译名与别名搜索服务


def create_service_container(cache: InMemoryTtlCache) -> ServiceContainer:
    """
    @brief 创建应用生命周期持有的服务容器。
    @param cache 已由应用入口创建的进程内 TTL 缓存。
    @return 已注入运行时配置、缓存和共享服务依赖的应用级服务容器。
    """
    subjects = SubjectService()
    seasons = SeasonService(cache=cache)
    rankings = RankingService(cache=cache, subjects=subjects)
    home = HomeService(cache=cache, rankings=rankings, seasons=seasons, subjects=subjects)
    search = SearchService(subjects=subjects)

    return ServiceContainer(seasons=seasons, subjects=subjects, rankings=rankings, home=home, search=search)


if __name__ == '__main__':
    pass
