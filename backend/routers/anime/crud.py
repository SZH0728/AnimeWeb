# -*- coding:utf-8 -*-
# AUTHOR: Sun

from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from database import Detail, Score, NameID, Cache


def get_anime_list(page: int, limit: int, min_vote: int, session: Session):
    time = datetime.now().date() - timedelta(days=1)

    query = session.query(Score.detailId, Score.score, Score.vote)
    query = query.filter(Score.vote >= min_vote, Score.date == time)
    query = query.order_by(Score.score.desc())

    offset = (page - 1) * limit

    total = query.count()
    total_page = total // limit + (1 if total % limit else 0)

    paginated_result = query.offset(offset).limit(limit).all()

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


def get_anime_detail(anime_id: int, session: Session) -> Detail:
    query = session.query(Detail).filter(Detail.id == anime_id)
    return query.first()

def get_anime_score_history(anime_id: int, session: Session):
    query = session.query(Score).filter(Score.detailId == anime_id)
    return query.all()


if __name__ == '__main__':
    pass
