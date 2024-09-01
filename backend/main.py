# -*- coding:utf-8 -*-
# AUTHOR: Sun

from configparser import ConfigParser
from os.path import dirname, join

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.anime.router import anime

config = ConfigParser()
config_file = join(dirname(__file__), 'config.ini')
config.read(config_file)
allow_origins = config.get('cors', 'allow_origins')
allow_origins = [i.strip() for i in allow_origins.split(',')]
allow_origin_regex = config.get('cors', 'allow_origin_regex')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
)

app.include_router(anime)


if __name__ == '__main__':
    pass
