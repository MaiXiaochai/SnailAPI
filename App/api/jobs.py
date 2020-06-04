# -*- coding: utf-8 -*-

"""
--------------------------------------
@File       : __init__.py
@Author     : maixiaochai
@Email      : maixiaochai@outlook.com
@Created on : 2020/5/22 15:39
--------------------------------------
"""
from copy import deepcopy

from flask import jsonify
from flask_restful import Resource, marshal
from flask_restful.reqparse import RequestParser
from flask_restful.fields import Integer, String, DateTime, Nested, List

from App.extensions import scheduler
from App.models.jobs import JobData, JobStatus
from App.utils import set_model_value, job_handler, get_next_time, save_job_data, save_job_status
from App.setting import (HTTP_OK,
                         HTTP_CREATED_OK,
                         HTTP_CREATED_FAILED,
                         MSG_JOB_CREATED_FAILED,
                         MSG_JOB_CREATED_SUCCESS, MSG_JOB_PAUSED, MSG_JOB_RESUMED, MSG_JOB_RUNNING,
                         HTTP_EXECUATE_FAILED, HTTP_CONFLICT, MSG_JOB_EXISTED, MSG_JOB_QUERY_SUCCESS,
                         MSG_JOB_QUERY_FAILED, HTTP_QUERY_ERROR,
                         )

# Request 格式内容检测
parser_jobs = RequestParser(trim=True)

# 继承一份，只包含 jobName字段
parser_actions = parser_jobs.copy()
parser_actions.add_argument("action", type=str, required=True, help="请输入操作名称")

parser_jobs.add_argument("jobType", dest="job_type", type=str, required=True, choices=["cli", ],
                         help="请输入任务类型，暂时只支持cli，[cli|script|proc]")

parser_jobs.add_argument("jobCmd", dest="job_cmd", type=str, required=True, help="请输入任务运行命令, 如 python test.py")
parser_jobs.add_argument("timeStyle", dest="time_style", type=str, required=True, choices=["cron", ],
                         help="请输入时间风格, 暂时只支持 cron, [cron|interval|date]")

parser_jobs.add_argument("timeData", dest="time_data", type=str, required=True, help="请输入执行时间，如 0 5 * * *")
parser_jobs.add_argument("createdBy", dest="created_by", type=str, required=True, help="请输入任务创建人姓名")
parser_jobs.add_argument("category", dest="category", type=str, required=True,
                         help="请输入任务所属业务，[mes|erp|warranty|radar|pms|stopcard|...]")

parser_jobs.add_argument("desc", dest="desc", type=str, required=True, help="请输入任务描述")

job_fields = {
    "jobName": String(attribute="job_name"),
    "job_type": String(attribute="job_type"),
    "jobCmd": String(attribute="job_cmd"),
    "nextRunTime": DateTime(attribute="next_run_time", dt_format="iso8601"),
    "timeStyle": String(attribute="time_style"),
    "timeData": String(attribute="time_data")
}

jobs_fields = {
    "status": Integer,
    "msg": String,
    "total": Integer,
    "data": List(Nested(job_fields)),
    "error": String(default="")
}


class JobsResource(Resource):
    """
    TODO:
        1) job添加是否成功的判断，成功后再写入日志
        2) job修改或者删除后，job_data数据表中，也做相应的修改
    """

    def get(self, job_name):
        """
        任务获取,可获取单个，多个
        """
        status, msg, error = HTTP_OK, MSG_JOB_QUERY_SUCCESS, ""
        job_name = str(job_name.strip())
        jobs_data = []
        result_data = []

        if job_name.lower() != "all":
            if ";" not in job_name:
                jobs_data = [scheduler.get_job(job_name)]

            else:
                job_names = job_name.split(";")
                for name in job_names:
                    jobs_data.append(scheduler.get_job(name))
        else:
            jobs_data = scheduler.get_jobs()

        try:
            jobs_info = get_next_time(jobs_data)

            for item in jobs_info:
                _job = JobData.query.filter(JobData.job_name == item["job_name"]).first()

                _info = deepcopy(item)
                _info["job_type"] = _job.job_type
                _info["job_cmd"] = _job.job_cmd
                _info["time_style"] = _job.time_style
                _info["time_data"] = _job.time_data
                result_data.append(_info)

        except AttributeError as err:
            status, msg = HTTP_QUERY_ERROR, MSG_JOB_QUERY_FAILED
            error = str(err)

        result = {
            "status": status,
            "msg": msg,
            "total": len(result_data),
            "data": result_data
        }

        if error:
            result["error"] = error

        return marshal(result, jobs_fields)

    def post(self, job_name):
        """添加一个任务"""
        args = parser_jobs.parse_args()

        # 准备添加到调度的数据
        sched_dict = {
            "job_name": job_name,
            "job_cmd": args.job_cmd,
            "time_style": args.time_style.lower(),
            "time_data": args.time_data
        }

        status, msg, error = HTTP_CREATED_OK, MSG_JOB_CREATED_SUCCESS, ""
        try:
            _exist = scheduler.get_job(job_name)
            if not _exist:
                # 将 job添加到调度
                job_handler(scheduler, sched_dict)

                # job 数据保存到数据库
                save_job_data(job_name, args, JobData)

                # 添加job name 到job status 表
                save_job_status(job_name, JobStatus)

            else:
                status = HTTP_CONFLICT
                msg = MSG_JOB_EXISTED

        except Exception as err:
            status = HTTP_CREATED_FAILED
            msg = MSG_JOB_CREATED_FAILED
            error = str(err)

        result = {
            "status": status,
            "msg": msg,
            "jobName": job_name
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if not error:
            result["error"] = error

        return jsonify(result)

    def put(self, job_name):
        """
        TODO: 1) 任务运行状态可批量修改
              2) 修改job全部数据和部分数据的API和 ModLog保存
        处理任务操作 暂停/恢复/立即执行
        """
        args = parser_actions.parse_args()
        action = args.get("action").lower()

        status, msg, error = HTTP_OK, "", ""

        # 任务暂停
        if action == "pause":
            try:
                scheduler.pause_job(job_name)
                msg = MSG_JOB_PAUSED
            except Exception as err:
                error = str(err)

        # 任务恢复
        elif action == "resume":
            try:
                scheduler.resume_job(job_name)
                msg = MSG_JOB_RESUMED
            except Exception as err:
                error = str(err)

        # 任务立刻执行
        elif action == "run":
            """
            [2020-06-03]
            Q: 为什么在run_job前后加上pause_job和resume_job？
            A: 主要是考虑到在任务运行期间，该任务的调度时间也到了，会造成两次运行。
               对于某些内部逻辑没有限制的任务，同时运行两个实例，结果是灾难性的。
               所以，为了防止这种情况发生,首先暂停该任务的调度（在内部源码上的实现是将next_run_time置空）
               在程序运行完成后，再恢复该程序的调度。
            """
            try:
                scheduler.pause_job(job_name)
                scheduler.run_job(job_name)
                msg = MSG_JOB_RUNNING

            except Exception as err:
                error = str(err)

            finally:
                scheduler.resume_job(job_name)

        # 修改除job_name外的全部信息
        elif action == "update":

            pass

        status = HTTP_OK if not error else HTTP_EXECUATE_FAILED
        result = {
            "status": status,
            "msg": msg,
            "jobName": job_name,
            "action": action
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error

        return jsonify(result)
