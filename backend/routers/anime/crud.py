# -*- coding:utf-8 -*-
# AUTHOR: Sun

from sqlalchemy import func, and_
from sqlalchemy.engine import row
from sqlalchemy.orm import Session

from database import Detail, Score, NameID, Web


class AllNoneAttribute(object):
    def __getattr__(self, item):
        return None


def get_total_page_by_query(limit: int, query) -> tuple[int, ...]:
    """
    根据查询结果和每页显示的数量计算总页数
    :param limit: 每页显示的数量
    :param query: 查询对象
    :return: 总数和总页数
    """
    # 计算查询结果的总数
    total = query.count()
    # 根据总数和每页数量计算总页数
    total_page = total // limit + (1 if total % limit else 0)
    # 返回总数和总页数
    return total, total_page


def get_detail_dict_by_ids(ids: list[int], session: Session) -> dict[int, row]:
    """
    根据给定的ID列表和数据库会话获取详情内容的字典
    :param ids: ID列表
    :param session: 数据库会话
    :return: 详情内容的字典
    """
    # 构建查询语句，选择Detail表中的多个字段，并过滤出ID在给定列表中的记录
    detail_query = (
        session.query(
            Detail.id, Detail.name, Detail.translation,
            Detail.tag, Detail.description, Detail.picture
        )
        .filter(Detail.id.in_(ids))
    )
    # 执行查询并获取所有匹配的记录
    detail_list = detail_query.all()
    # 将查询结果转换为以ID为键的字典
    detail_dict = {detail.id: detail for detail in detail_list}
    # 返回构建好的字典
    return detail_dict


def get_score_dict_by_query(limit: int, page: int, query) -> dict[int, row]:
    """
    根据已经构建好的查询对象、每页显示的数量以及当前页码获取评分信息的字典
    :param limit: 每页显示的数量
    :param page: 当前页码
    :param query: 查询对象
    :return: 评分信息的字典
    """
    # 计算当前页的偏移量
    offset = (page - 1) * limit
    # 根据偏移量和每页数量获取指定范围内的记录
    score_list = query.offset(offset).limit(limit).all()
    # 将查询结果转换为以detailId为键的字典
    score_dict = {score.detailId: score for score in score_list}
    # 返回构建好的字典
    return score_dict


def construct_anime_list_by_score_and_detail_dict(detail_dict: dict[int, row], score_dict: dict[int, row],
                                                  ids: list[int], total: int, total_page: int) -> dict:
    """
    根据评分和详情字典构造动漫列表
    :param detail_dict: 详情字典
    :param score_dict: 评分字典
    :param ids: ID列表
    :param total: 总数
    :param total_page: 总页数
    :return: 动漫列表
    """
    # 初始化结果字典，包含总数、总页数和数据列表
    result = {'total': total, 'total_page': total_page, 'data': []}
    # 遍历ID列表
    for i in ids:
        # 获取详情信息，如果不存在则使用AllNoneAttribute类的对象
        detail = detail_dict.get(i, AllNoneAttribute())
        # 获取评分信息，如果不存在则使用AllNoneAttribute类的对象
        score = score_dict.get(i, AllNoneAttribute())
        # 构造单个动漫的数据字典
        data = {
            'id': detail.id,
            'name': detail.name,
            'translation': detail.translation,
            'tag': [i for i in detail.tag if i],  # 过滤掉空值
            'description': detail.description,
            'picture': detail.picture,
            'score': score.score,
            'vote': score.vote
        }
        # 将单个动漫的数据追加到结果字典的数据列表中
        result['data'].append(data)
    # 返回构造好的结果字典
    return result


def construct_anime_list_result_by_score_query(limit: int, page: int, query, session: Session) -> dict:
    """
    根据评分查询构造动漫列表结果
    :param limit: 每页显示的数量
    :param page: 当前页码
    :param query: 查询对象
    :param session: 数据库会话
    :return: 动漫列表结果
    """
    # 获取总条数和总页数
    total, total_page = get_total_page_by_query(limit, query)
    # 获取评分信息字典
    score_dict = get_score_dict_by_query(limit, page, query)
    # 提取评分字典中的ID列表
    ids = [i.detailId for i in score_dict.values()]
    # 获取详情信息字典
    detail_dict = get_detail_dict_by_ids(ids, session)
    # 构造最终的动漫列表
    result = construct_anime_list_by_score_and_detail_dict(detail_dict, score_dict, ids, total, total_page)
    # 返回构造好的结果字典
    return result


def get_anime_list(page: int, limit: int, min_vote: int, session: Session) -> dict:
    """
    根据页码、每页数量和最低投票数获取动漫列表
    :param page: 当前页码
    :param limit: 每页显示的数量
    :param min_vote: 最低投票数
    :param session: 数据库会话
    :return: 动漫列表结果
    """
    # 创建子查询，筛选出每个detailId下的最高投票日期
    subquery = (
        session.query(
            Score.detailId,
            func.max(Score.date).label('max_date')
        )
        .filter(Score.vote >= min_vote)  # 筛选出投票数大于等于最低投票数的记录
        .group_by(Score.detailId)  # 按detailId分组
        .subquery()  # 创建子查询
    )

    # 创建主查询，筛选出每个detailId下最高投票日期的评分记录
    query = (
        session.query(Score.detailId, Score.score, Score.vote)
        .join(subquery, (Score.detailId == subquery.c.detailId) & (Score.date == subquery.c.max_date))
        .order_by(Score.score.desc())  # 按评分降序排序
    )

    # 调用函数构造最终的动漫列表结果
    return construct_anime_list_result_by_score_query(limit, page, query, session)


def get_anime_season(page: int, limit: int, min_vote: int, season: str, session: Session) -> dict:
    """
    根据页码、每页数量、最低投票数和季度获取动漫列表
    :param page: 当前页码
    :param limit: 每页显示的数量
    :param min_vote: 最低投票数
    :param season: 季度
    :param session: 数据库会话
    :return: 动漫列表结果
    """
    # 创建子查询，筛选出指定季度的detailId
    detail_ids = session.query(Detail.id).filter(Detail.season == season).subquery()

    # 创建子查询，筛选出每个detailId下的最高评分和最新日期
    subquery = (
        session.query(
            Score.detailId,
            func.max(Score.score).label('max_score'),
            func.max(Score.date).label('latest_date')
        )
        .filter(Score.detailId.in_(detail_ids))  # 筛选出detailId在指定季度内的记录
        .group_by(Score.detailId)  # 按detailId分组
        .subquery()  # 创建子查询
    )

    # 创建主查询，筛选出每个detailId下最高评分和最新日期的评分记录
    scores_query = (
        session.query(Score.detailId, Score.score, Score.vote)
        .join(subquery, and_(
            Score.detailId == subquery.c.detailId,
            Score.score == subquery.c.max_score,
            Score.date == subquery.c.latest_date
        ))
        .filter(Score.vote >= min_vote)  # 筛选出投票数大于等于最低投票数的记录
        .order_by(Score.score.desc())  # 按评分降序排序
    )

    # 调用函数构造最终的动漫列表结果
    return construct_anime_list_result_by_score_query(limit, page, scores_query, session)


def get_search_anime_list(keyword: list, page: int, limit: int, session: Session):
    search_kw = '%'.join([i for i in keyword if i])
    search_kw = f'%{search_kw}%'
    offset = (page - 1) * limit

    query = session.query(NameID.id)
    query = query.filter(NameID.name.like(search_kw))
    query = query.offset(offset).limit(limit)
    id_list = list(set([i.id for i in query]))

    total = len(id_list)
    total_page = total // limit + (1 if total % limit else 0)

    detail_query = session.query(Detail.name, Detail.translation, Detail.tag, Detail.description, Detail.picture)
    anime_list = [detail_query.filter(Detail.id == id_).first() for id_ in id_list]

    score_query = session.query(Score.score, Score.vote)
    score_query = score_query.order_by(Score.date.desc())
    score_list = [score_query.filter(Score.detailId == id_).first() for id_ in id_list]

    result = {'total': total, 'total_page': total_page, 'data': []}
    for index, id_ in enumerate(id_list):
        score = score_list[index] if score_list[index] else AllNoneAttribute()
        anime = anime_list[index]
        data = {
            'id': id_,
            'name': anime.name,
            'translation': anime.translation,
            'tag': [i for i in anime.tag if i],
            'description': anime.description,
            'picture': anime.picture,
            'score': score.score,
            'vote': score.vote
        }
        result['data'].append(data)
    return result


def get_anime_detail(anime_id: int, session: Session) -> dict:
    query = session.query(Detail).filter(Detail.id == anime_id)
    detail: Detail = query.first()
    web = session.query(Web).filter(Web.id == detail.web).first()
    result = {
        "id": detail.id,
        "name": detail.name,
        "translation": detail.translation,
        "alias": [i for i in detail.alias if i],
        "time": detail.time,
        "tag": [i for i in detail.tag if i],
        "director": detail.director,
        "cast": [i for i in detail.cast if i],
        "description": detail.description,
        "source": web.name,
        "url": web.host + web.url_format.format(detail.webId),
        "picture": detail.picture
    }
    return result


def get_anime_score_history(anime_id: int, session: Session):
    query = session.query(Score.detailScore, Score.score, Score.vote, Score.date
                          ).filter(Score.detailId == anime_id).all()
    result = [{'detailScore': i.detailScore, 'score': i.score, 'vote': i.vote, 'date': i.date} for i in query]
    return result


def get_web_info(session: Session):
    query = session.query(Web.id, Web.name).all()
    result = {}
    for i in query:
        result[str(i.id)] = i.name
    return result


if __name__ == '__main__':
    pass
