# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/27 21:19
--------------------------------------
"""
from os import environ

from .constants import *
from .settings import envs

flask_env = environ.get("FLASK_ENV", "default")
cfg_obj = envs.get(flask_env)

api_interface = cfg_obj.API_INTERFACE
