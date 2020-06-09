# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : intros.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/27 22:13
--------------------------------------
"""
from flask import jsonify
from flask_restful import Resource

from App.setting import HTTP_OK, envs


class IntroResource(Resource):
    """
    TODO: SnailAPI使用说明
        1)做成一个接口, /api/intros/{name}
            /api/intros/jobs
            /api/intros/logs
            /api/intros/stats
            /api/intros/users
    """
    def get(self):
        result = {
            "status": HTTP_OK,
            "msg": "Welcome to use the SnailAPI."
        }
        return jsonify(result)
