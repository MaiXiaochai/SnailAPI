# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : intro.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/27 22:13
--------------------------------------
"""
from flask import jsonify
from flask_restful import Resource

from App.setting import HTTP_OK


class IntroResource(Resource):
    """
    TODO: API说明信息
    """
    def get(self):
        result = {
            "status": HTTP_OK,
            "msg": "Welcome to use the SnailAPI."
        }
        return jsonify(result)
