# -*- coding:utf-8 -*-
# AUTHOR: Sun

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import session
from routers.anime.schemas import AnimeList, AnimeDetail, AnimeScore
from routers.anime.crud import (get_anime_detail, get_anime_list, get_web_info,
                                get_search_anime_list, get_anime_score_history)

anime = APIRouter(
    prefix="/anime",
    tags=["anime"],
    responses={404: {"description": "Not found"}},
)


@anime.get('/list', response_model=AnimeList)
def anime_list(
        page: int | None = 1,
        limit: int | None = 10,
        min_vote: int | None = 0,
        db: Session = Depends(session)):
    result = get_anime_list(page, limit, min_vote, db)
    return result


@anime.get('/detail/{anime_id}', response_model=AnimeDetail)
def anime_detail(anime_id: int, db: Session = Depends(session)):
    result = get_anime_detail(anime_id, db)
    return result


@anime.get('/score/{anime_id}', response_model=list[AnimeScore])
def anime_score(anime_id: int, db: Session = Depends(session)):
    result = get_anime_score_history(anime_id, db)
    return result


@anime.get('/webinfo', response_model=dict)
def anime_web_info(db: Session = Depends(session)):
    result = get_web_info(db)
    return result


@anime.get('/search', response_model=AnimeList)
def anime_search(
        keyword: str,
        page: int | None = 1,
        limit: int | None = 10,
        db: Session = Depends(session)):
    keyword = keyword.strip().split()
    result = get_search_anime_list(keyword, page, limit, db)
    return result


if __name__ == '__main__':
    pass
