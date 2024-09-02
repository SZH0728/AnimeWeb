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

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(levelprefix)s %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "default": {
            "formatter": "default",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./default.txt"
        },
        "access": {
            "formatter": "access",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": "./access.txt"

        },
    },
    "loggers": {
        "": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    }
}

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_origin_regex=allow_origin_regex,
)

app.include_router(anime)


if __name__ == '__main__':
    from uvicorn import run
    run(app, host='0.0.0.0', port=60000, log_config=LOGGING_CONFIG)
