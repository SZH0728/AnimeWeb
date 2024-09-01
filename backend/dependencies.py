# -*- coding:utf-8 -*-
# AUTHOR: Sun

from database import SessionLocal


def session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == '__main__':
    pass
