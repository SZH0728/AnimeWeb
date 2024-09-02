# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database import Detail, Score, NameID, Web


class AllNoneAttribute(object):
    def __getattr__(self, item):
        return None


def get_total_page(limit: int, query) -> tuple[int, ...]:
    total = query.count()
    total_page = total // limit + (1 if total % limit else 0)
    return total, total_page


def get_anime_by_time(limit, min_vote, page, session, time):
    query = session.query(Score.detailId, Score.score, Score.vote)
    query = query.filter(Score.vote >= min_vote, Score.date == time)
    query = query.order_by(Score.score.desc())
    offset = (page - 1) * limit
    total, total_page = get_total_page(limit, query)
    paginated_result = query.offset(offset).limit(limit).all()
    return paginated_result, total, total_page


def get_anime_list(page: int, limit: int, min_vote: int, session: Session):
    time = datetime.now().date() - timedelta(days=1)

    paginated_result, total, total_page = get_anime_by_time(limit, min_vote, page, session, time)
    if not paginated_result:
        time_item = session.query(Score.date).order_by(Score.id.desc()).first()
        time = time_item.date
        paginated_result, total, total_page = get_anime_by_time(limit, min_vote, page, session, time)

    detail_query = session.query(Detail.name, Detail.translation, Detail.tag, Detail.description, Detail.picture)
    anime_list = [detail_query.filter(Detail.id == score.detailId).first() for score in paginated_result]

    result = {'total': total, 'total_page': total_page, 'data': []}
    for index, score in enumerate(paginated_result):
        data = {
            'id': score.detailId,
            'name': anime_list[index].name,
            'translation': anime_list[index].translation,
            'tag': [i for i in anime_list[index].tag if i],
            'description': anime_list[index].description,
            'picture': anime_list[index].picture,
            'score': score.score,
            'vote': score.vote
        }
        result['data'].append(data)

    return result


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
