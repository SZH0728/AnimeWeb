# -*- coding:utf-8 -*-
# AUTHOR: Sun

"""
@file config.py
@brief 提供运行时 INI 配置单例。
"""

import os
from configparser import RawConfigParser
from pathlib import Path

_DEFAULT_CONFIG_PATH = Path(__file__).resolve().parents[1] / 'config.ini'
_CONFIG_PATH = Path(os.environ.get('ANIMEWEB_CONFIG_PATH', '').strip() or _DEFAULT_CONFIG_PATH)

config = RawConfigParser()  # 此处无需使用大写的CONFIG，因其不为常量
config.read(_CONFIG_PATH, encoding='utf-8')

if __name__ == '__main__':
    pass
