# -*- coding:utf-8 -*-
# AUTHOR: Sun

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from dependencies import session
from routers.anime.schemas import AnimeList, Detail
from routers.anime.crud import get_anime_detail, get_anime_list

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


@anime.get('/anime/{anime_id}', response_model=Detail)
def anime_detail(anime_id: int, db: Session = Depends(session)):
    result = get_anime_detail(anime_id, db)
    return result


if __name__ == '__main__':
    pass
