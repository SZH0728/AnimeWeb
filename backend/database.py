# -*- coding:utf-8 -*-
# AUTHOR: Sun

from configparser import ConfigParser
from os.path import dirname, join

from sqlalchemy import create_engine, Column, Integer, String, Text, Date, JSON, CHAR, DECIMAL
from sqlalchemy.dialects.mysql import TINYINT, MEDIUMINT
from sqlalchemy.orm import sessionmaker, declarative_base

config = ConfigParser()
config_file = join(dirname(__file__), 'config.ini')
config.read(config_file)

user = config.get('database', 'user')
password = config.get('database', 'password')
host = config.get('database', 'host')
port = config.get('database', 'port')
dbname = config.get('database', 'dbname')

SQLALCHEMY_DATABASE_URL = f'mariadb+pymysql://{user}:{password}@{host}:{port}/{dbname}'

Engine = create_engine(SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, pool_recycle=14400)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=Engine)

Base = declarative_base()


class Cache(Base):
    __tablename__ = 'cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False, index=True)
    score = Column(DECIMAL(3, 1))
    vote = Column(Integer)
    date = Column(Date, nullable=False)
    web = Column(TINYINT)


class Detail(Base):
    __tablename__ = 'detail'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), nullable=False)
    translation = Column(String(64))
    alias = Column(JSON)
    season = Column(String(3), index=True)
    time = Column(Date)
    tag = Column(JSON)
    director = Column(String(32))
    cast = Column(JSON)
    description = Column(Text)
    web = Column(TINYINT)
    webId = Column(MEDIUMINT)
    picture = Column(String(64))


class NameID(Base):
    __tablename__ = 'nameid'

    name = Column(String(128), primary_key=True)
    id = Column(Integer)


class Score(Base):
    __tablename__ = 'score'

    id = Column(Integer, primary_key=True, autoincrement=True)
    detailId = Column(Integer, nullable=False)
    detailScore = Column(JSON, nullable=False)
    score = Column(DECIMAL(3, 1))
    vote = Column(Integer)
    date = Column(Date, nullable=False)


class Web(Base):
    __tablename__ = 'web'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(CHAR(16), nullable=False)
    host = Column(CHAR(16), nullable=False)
    url_format = Column('format', String(16), nullable=False)
    priority = Column(TINYINT, nullable=False)


if __name__ == '__main__':
    pass
