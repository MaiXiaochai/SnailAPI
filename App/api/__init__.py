# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 13:50
--------------------------------------
"""
from flask_restful import Api

from .intro import IntroResource
from .jobs import JobsResource
from .logs import LogResource
from ..setting import api_interface, ERRORS

api_snail = Api(prefix=api_interface, errors=ERRORS, catch_all_404s=True)
api_snail.add_resource(IntroResource, "/")
api_snail.add_resource(JobsResource, "/jobs/<string:job_name>")
api_snail.add_resource(LogResource, "/logs/<string:job_name>")


def init_api(app):
    api_snail.init_app(app)
