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
from App.setting import HTTP_OK, HTTP_QUERY_ERROR, MSG_JOB_QUERY_SUCCESS, MSG_JOB_QUERY_FAILED

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
        args = parser_logs.parse_args()
        total = args.total

        error, data, len_data = "", "", 0
        try:
            if total <= 1:
                # 查询单个job_name最新的运行日志
                data = RunningLog.query.filter(RunningLog.job_name == job_name).order_by(-RunningLog.id).first()
                len_data = 1 if data else len_data
            else:
                data = RunningLog.query.filter(RunningLog.job_name == job_name).order_by(-RunningLog.id).limit(total).all()
                len_data = len(data)

        except Exception as err:
            error = str(err)

        finally:
            status, msg = (HTTP_OK, MSG_JOB_QUERY_SUCCESS) if not error else (HTTP_QUERY_ERROR, MSG_JOB_QUERY_FAILED)
            result = {
                "status": status,
                "msg": msg,
                "total": len_data,
                "data": data
            }
            return marshal(result, logs_fields_running)
