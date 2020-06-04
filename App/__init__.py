# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 13:46
--------------------------------------
"""
from flask import Flask

from App.api import init_api
from App.setting import cfg_obj
from App.extensions import init_ext


def create_app():
    app = Flask(__name__)

    # 初始化配置
    app.config.from_object(cfg_obj)

    # 初始化扩展
    init_ext(app)

    # 初始化API
    init_api(app)

    return app
