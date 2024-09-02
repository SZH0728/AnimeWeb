# -*- coding:utf-8 -*-
# AUTHOR: Sun

from pydantic import BaseModel
from decimal import Decimal
from datetime import date


class Cache(BaseModel):
    id: int
    name: str
    score: Decimal | None = None
    vote: int | None = None
    date: date
    web: int | None = None

    class Config:
        from_attributes = True


class Detail(BaseModel):
    id: int
    name: str
    translation: str | None = None
    alias: list[str] | None = None
    season: str
    time: date | None = None
    tag: list[str] | None = None
    director: str | None = None
    cast: list[str] | None = None
    description: str | None = None
    web: int | None = None
    webId: int | None = None
    picture: str | None = None

    class Config:
        from_attributes = True


class NameID(BaseModel):
    name: str
    id: int

    class Config:
        from_attributes = True


class Score(BaseModel):
    id: int
    detailId: int
    detailScore: dict[str, dict]
    score: Decimal | None = None
    vote: int | None = None
    date: date

    class Config:
        from_attributes = True


class Web(BaseModel):
    id: int
    name: str
    host: str
    url_format: str
    priority: int

    class Config:
        from_attributes = True


class AnimeListDetail(BaseModel):
    id: int
    name: str
    translation: str | None = None
    tag: list[str] | None = None
    description: str | None = None
    picture: str | None = None
    score: Decimal | None = None
    vote: int | None = None


class AnimeList(BaseModel):
    total: int
    total_page: int
    data: list[AnimeListDetail]


class AnimeDetail(BaseModel):
    id: int
    name: str
    translation: str | None = None
    alias: list[str] | None = None
    time: date | None = None
    tag: list[str] | None = None
    director: str | None = None
    cast: list[str] | None = None
    description: str | None = None
    source: str | None = None
    url: str | None = None
    picture: str | None = None


class AnimeScore(BaseModel):
    detailScore: dict[str, dict]
    score: Decimal | None = None
    vote: int | None = None
    date: date


if __name__ == '__main__':
    pass
