# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:40
--------------------------------------
"""

from flask_restful import Resource, marshal
from flask_restful.fields import String, Integer, DateTime, Nested, List
from flask_restful.reqparse import RequestParser

from App.models.logs import RunningLog
from App.setting import HTTP_OK

parser_logs = RequestParser(trim=True)
parser_logs.add_argument("total", type=int, required=True, help="查询正确的查询数据量")


log_fields_running = {
    "jobName": String(attribute="job_name"),
    "jobCmd": String(attribute="job_cmd"),
    "startDate": DateTime(attribute="start_date", dt_format="iso8601"),
    "endDate": DateTime(attribute="end_date", dt_format="iso8601"),
    "returnCode": Integer(attribute="return_code"),
    "stdout": String,
    "stderr": String
}

logs_fields_running = {
    "status": Integer,
    "msg": String,
    "total": Integer,
    "data": List(Nested(log_fields_running))
}


class LogResource(Resource):
    def get(self, job_name):
        arges = parser_logs.parse_args()
        total = arges.total

        if total <= 1:
            # 查询单个job_name最新的运行日志
            log = RunningLog.query.filter(RunningLog.job_name == job_name).order_by(-RunningLog.id).first()
            result = {
                "status": HTTP_OK,
                "msg": "log queried.",
                "total":  1 if log else 0,
                "data": log
            }
            return marshal(result, logs_fields_running)

        else:
            logs = RunningLog.query.filter(RunningLog.job_name == job_name).order_by(-RunningLog.id).limit(total).all()
            result = {
                "status": HTTP_OK,
                "msg": "log queried.",
                "total": len(logs),
                "data": logs
            }
            return marshal(result, logs_fields_running)
