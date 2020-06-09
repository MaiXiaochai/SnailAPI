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
from flask_restful.fields import Integer, String, DateTime, Nested, List
from flask_restful.reqparse import RequestParser
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from App.extensions import scheduler
from App.models.jobs import JobData, JobStatus
from App.models.logs import ModLog
from App.setting import *
from App.utils import (set_model_value, job_handler, get_next_time, save_job_data, save_job_status, up_job_status,
                       save_mod_log, cron_to_dict, up_job_data, del_job, rm_empty_kw, FileHandler
                       )

# Request 解析参数。自动去除值两边空格
parser_jobs = RequestParser(trim=True)

# 继承parser_job
parser_actions = parser_jobs.copy()
# 继承 parser_job
parser_mod = parser_jobs.copy()
# ============================================== [ parser_job ] ==============================================
parser_jobs.add_argument("timeStyle", dest="time_style", type=str, required=True, choices=["cron", ],
                         help="请输入时间风格, 暂时只支持 cron, [cron|interval|date]")

parser_jobs.add_argument("timeData", dest="time_data", type=str, required=True, help="请输入执行时间，如 0 5 * * *")
parser_jobs.add_argument("jobType", dest="job_type", type=str, required=True, choices=["cli", "script"],
                         help="请输入任务类型，暂时不支持proc，[cli|script|proc]")

parser_jobs.add_argument("jobCmd", dest="job_cmd", type=str, required=True, help="请输入任务运行命令, 如 python test.py")
parser_jobs.add_argument("createdBy", dest="created_by", type=str, required=True, help="请输入任务创建人姓名")
parser_jobs.add_argument("category", dest="category", type=str, required=True,
                         help="请输入任务所属业务，[mes|erp|warranty|radar|pms|stopcard|...]")

parser_jobs.add_argument("desc", dest="desc", type=str, required=True, help="请输入任务描述")
# 文件上传
parser_jobs.add_argument("file", type=FileStorage, help="请上传文件", location=["files"])

# ============================================== [ parser_action ] ==============================================
parser_actions.add_argument("action", type=str, required=True, help="请输入操作名称")

# ================================================ [ parser_mod ] ================================================
# 5个参数 action, timeStyle, timeData, desc, category
parser_mod.add_argument("timeStyle", dest="time_style", type=str, choices=["cron", ],
                        help="请输入时间风格, 暂时只支持 cron, [cron|interval|date]")

parser_mod.add_argument("timeData", dest="time_data", type=str, help="请输入执行时间，如 0 5 * * *")
parser_mod.add_argument("createdBy", dest="created_by", type=str, help="请输入需求人")
parser_mod.add_argument("category", dest="category", type=str,
                        help="请输入任务所属业务，[mes|erp|warranty|radar|pms|stopcard|...]")

parser_mod.add_argument("desc", dest="desc", type=str, help="请输入任务描述")

# ============================================== [ parser done ] ==============================================
post_fields = {
    "jobName": String(attribute="job_name"),
    "job_type": String(attribute="job_type"),
    "jobCmd": String(attribute="job_cmd"),
    "timeStyle": String(attribute="time_style"),
    "timeData": String(attribute="time_data")
}

posts_fields = {
    "status": Integer,
    "msg": String,
    "total": Integer,
    "data": List(Nested(post_fields))
}

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
    "data": List(Nested(job_fields))
}


class JobsResource(Resource):
    """
    Job CRUD/RUN/PAUSE/RESUME
    """
    def get(self, job_name):
        """
        任务获取,可获取单个，多个
        """
        status, msg, error = HTTP_OK, MSG_JOB_QUERY_SUCCESS, ""
        job_name = str(job_name.strip())
        jobs_data, result_data = [], []

        # 部分job data
        if job_name.lower() != "all":
            if ";" not in job_name:
                jobs_data = [scheduler.get_job(job_name)]

            else:
                job_names = job_name.split(";")
                for name in job_names:
                    jobs_data.append(scheduler.get_job(name))
        else:
            # 全部 job data
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
            jobs_fields["error"] = String
        return marshal(result, jobs_fields)

    def post(self, job_name):
        """添加一个任务"""
        job_args = parser_jobs.parse_args()

        full_data = {"job_name": job_name}
        set_model_value(full_data, job_args)
        full_data.pop("file")

        status, msg, error = HTTP_CREATED_OK, MSG_JOB_CREATED_SUCCESS, ""

        try:
            _exist = scheduler.get_job(job_name)

            if not _exist:
                # 准备添加到调度的数据
                sched_dict = {
                    "job_name": job_name,
                    "job_cmd": job_args.job_cmd,
                    "time_style": job_args.time_style.lower(),
                    "time_data": job_args.time_data,
                    "cwd": None
                }

                job_type = job_args.job_type.lower()

                if job_type == "script":
                    file_content = job_args.file

                    if not file_content:
                        raise Exception(MSG_FILE_EMPTY)

                    else:
                        src_filename = file_content.filename
                        s_filename = secure_filename(src_filename)

                        # 替换命令中的不安全文件名称
                        new_cmd = job_args.job_cmd.replace(src_filename, s_filename)
                        full_data["job_cmd"] = sched_dict["job_cmd"] = new_cmd

                        abs_dir = FileHandler().abs_dirname(job_args.category)          # 保存目录, 绝对路径
                        _ = FileHandler.mkdir(abs_dir)                                  # 创建目录
                        full_data["cwd"] = sched_dict["cwd"] = abs_dir                  # 调度的工作目录

                        # 保存文件
                        abs_filename = f"{abs_dir}/{s_filename}"
                        file_content.save(abs_filename)

                else:
                    raise Exception(MSG_CMD_VALID)

                # 将 job添加到调度
                job_handler(scheduler, sched_dict)

                # job 数据保存到数据库
                save_job_data(full_data, JobData)

                # 添加job name 到job status 表
                save_job_status(job_name, JobStatus)

                # 添加job 修改日志
                save_mod_log(ACTION_CREATED, full_data, ModLog, JobData)

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
            "total": 0 if error else 1,
            "data": full_data
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error

        return marshal(result, posts_fields)

    def put(self, job_name):
        """
        处理任务操作 暂停/恢复/立即执行
        """
        args_actions = parser_actions.parse_args()
        action = args_actions.get("action").lower()

        msg, error = "", ""

        # 任务暂停
        if action == "pause":
            try:
                scheduler.pause_job(job_name)  # 暂停
                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))  # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作
                msg = MSG_JOB_PAUSED_SUCCESS
            except Exception as err:
                error = str(err)
                msg = MSG_JOB_PAUSED_FAILED
        # 任务恢复
        elif action == "resume":
            try:
                scheduler.resume_job(job_name)  # 恢复
                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))  # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作
                msg = MSG_JOB_RESUMED_SUCCESS
            except Exception as err:
                error = str(err)
                msg = MSG_JOB_RESUMED_FAILED

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

            # 获取run之前的状态
            next_time = scheduler.get_job(job_name).next_run_time
            before_run_status = STATUS_SLEEP if next_time else STATUS_PAUSED

            try:
                # 总的思想是，run前是什么状态，run之后便恢复到什么状态
                if before_run_status == STATUS_SLEEP:
                    scheduler.pause_job(job_name)

                up_job_status(job_name, JobStatus, STATUS_DICT.get(action))    # 修改任务状态
                save_mod_log(action, {"job_name": job_name}, ModLog, JobData)  # 保存人为动作

                scheduler.run_job(job_name)  # 运行
                msg = MSG_JOB_RUNNING_SUCCESS

            except Exception as err:
                error = str(err)
                msg = MSG_JOB_RUNNING_FAILED

            finally:
                run_result = RESULT_SUCCESS if not error else RESULT_FAILED
                up_job_status(job_name, JobStatus, before_run_status, run_result)  # 修改任务状态

                if before_run_status == STATUS_SLEEP:
                    scheduler.resume_job(job_name)  # 恢复

        # 修改除job_name外的信息
        elif action == "update":
            args_mod = parser_mod.parse_args()

            full_data = {"job_name": job_name}
            set_model_value(full_data, args_mod)
            # 移除没有值的键值对儿
            full_data = rm_empty_kw(full_data)

            try:
                if "time_style" in full_data and "time_data" in full_data:

                    # 字符串时间变字典时间
                    trigger_data = cron_to_dict(CRON_KEYS, full_data.get("time_data"))
                    changes = {
                        # 时间风格
                        "trigger": full_data.get("time_style")
                    }
                    changes.update(trigger_data)

                    # 修改任务时间
                    scheduler.modify_job(job_name, **changes)

                # 更新该job在JobData中的元数据
                up_job_data(full_data, JobData)

                # 将更改记录保存到日志
                save_mod_log(ACTION_UPDATED, full_data, ModLog, JobData)
                msg = MSG_JOB_MODIFIED_SUCCESS

            except Exception as err:
                error = str(err)
                msg = MSG_JOB_MODIFIED_FAILED

        status = HTTP_OK if not error else HTTP_EXECUTE_FAILED
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

    def delete(self, job_name):
        """
        删除指定job
        :param job_name:        str/list    要删除的job
        """
        error = ""
        try:
            args = {"job_name": job_name}
            # 移除
            scheduler.remove_job(job_name)

            # 注意这里的顺序，先添加移除日志，再移除，否则移除日志找不到元数据
            save_mod_log(ACTION_DELETED, args, ModLog, JobData)

            # 删除job状态和数据
            del_job(job_name, JobStatus, JobData)
        except Exception as err:
            error = str(err)

        status, msg = (HTTP_EXECUTE_FAILED, MSG_JOB_DELETED_FAILED) if error else (HTTP_OK, MSG_JOB_DELETED_SUCCESS)
        result = {
            "status": status,
            "msg": msg,
            "jobName": job_name,
            "action": ACTION_DELETED
        }

        # 如果出现错误，则在返回结果中加上报错内容
        if error:
            result["error"] = error

        return jsonify(result)
